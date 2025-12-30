"""
AI Service for processing natural language commands and interacting with the OpenAI API
"""
import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from pydantic import BaseModel
import json
import asyncio
from enum import Enum
from openai import AsyncOpenAI, APIError, AuthenticationError, RateLimitError, APIConnectionError, Timeout

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIResponse(BaseModel):
    """Structure for AI responses"""
    success: bool
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = {}
    response: str = ""
    action_result: Optional[Dict[str, Any]] = {}


class AIErrorType(Enum):
    """Enumeration of possible AI error types"""
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
    INVALID_REQUEST_ERROR = "INVALID_REQUEST_ERROR"
    API_ERROR = "API_ERROR"
    PARSE_ERROR = "PARSE_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class AIService:
    """Main AI service class for processing natural language commands"""

    def __init__(self):
        # Prefer OPENROUTER_MODEL if using OpenRouter, otherwise OPENAI_MODEL, default to gpt-3.5-turbo
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = "https://openrouter.ai/api/v1" if os.getenv("OPENROUTER_API_KEY") else None
        
        if os.getenv("OPENROUTER_API_KEY"):
             self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
             logger.info("Using OpenRouter API")
        else:
             self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
             logger.info("Using OpenAI API")

        if not api_key:
            raise ValueError("No API key found. Please set OPENROUTER_API_KEY or OPENAI_API_KEY environment variable.")
            
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
             
        self.max_retries = 3
        self.timeout = 30

    async def process_command(self, user_id: str, message: str) -> AIResponse:
        """
        Process a natural language command from the user with comprehensive error handling
        """
        retry_count = 0
        last_error = None

        while retry_count < self.max_retries:
            try:
                # Create a prompt that guides the AI to identify intent and extract entities
                prompt = f"""
                You are a helpful AI assistant that helps users manage their todos.
                Analyze the following user message and respond in JSON format with:
                - intent: The action the user wants to perform (CREATE, UPDATE, DELETE, QUERY, or UNKNOWN)
                - entities: Any relevant entities like todo titles, dates, etc.
                - response: A natural language response to the user

                User message: "{message}"

                Respond in JSON format only:
                """

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant that helps users manage their todos. Respond in JSON format with intent, entities, and response."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=200,
                    timeout=self.timeout
                )

                # Extract the AI's response
                ai_output = response.choices[0].message.content.strip()
                logger.info(f"Raw AI Output: {ai_output}")

                # Clean up markdown code blocks if present
                if ai_output.startswith("```"):
                    ai_output = ai_output.replace("```json", "").replace("```", "").strip()

                # Parse the JSON response from AI
                parsed_response = json.loads(ai_output)

                return AIResponse(
                    success=True,
                    intent=parsed_response.get("intent"),
                    entities=parsed_response.get("entities", {}),
                    response=parsed_response.get("response", ""),
                    action_result=None
                )

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {ai_output}")
                logger.error(f"JSON Parse Error: {str(e)}")
                return AIResponse(
                    success=False,
                    response="I'm sorry, I had trouble understanding your request. Could you please rephrase it?",
                    intent="UNKNOWN"
                )
            except AuthenticationError:
                logger.error("OpenAI authentication failed")
                return AIResponse(
                    success=False,
                    response="Authentication error. Please check your API configuration.",
                    intent="UNKNOWN"
                )
            except RateLimitError as e:
                logger.warning(f"OpenAI rate limit exceeded: {str(e)}")
                retry_count += 1
                if retry_count < self.max_retries:
                    # Wait before retrying (exponential backoff)
                    wait_time = 2 ** retry_count
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    return AIResponse(
                        success=False,
                        response="I'm currently experiencing high demand. Please try again in a few moments.",
                        intent="UNKNOWN"
                    )
            # OpenAI v1 renamed InvalidRequestError to BadRequestError, but generic APIError often covers it or we check specific types if needed.
            # Here we will catch generic APIError which covers connection issues too in some contexts, but specifically APIConnectionError is separate.
            except APIConnectionError as e:
                 logger.error(f"OpenAI connection error: {str(e)}")
                 retry_count += 1
                 last_error = str(e)
                 if retry_count < self.max_retries:
                    wait_time = 2 ** retry_count
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                 else:
                    return AIResponse(
                        success=False,
                        response="I'm having trouble connecting to the AI service. Please try again later.",
                        intent="UNKNOWN"
                    )
            except APIError as e:
                logger.error(f"OpenAI API error: {str(e)}")
                retry_count += 1
                last_error = str(e)
                if retry_count < self.max_retries:
                    wait_time = 2 ** retry_count
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    return AIResponse(
                        success=False,
                        response="I'm having trouble connecting to the AI service. Please try again later.",
                        intent="UNKNOWN"
                    )
            except Timeout as e:
                logger.error(f"OpenAI request timed out: {str(e)}")
                retry_count += 1
                if retry_count < self.max_retries:
                    logger.info("Retrying due to timeout...")
                    continue
                else:
                    return AIResponse(
                        success=False,
                        response="The request took too long to process. Please try again.",
                        intent="UNKNOWN"
                    )
            except asyncio.TimeoutError:
                logger.error("Request timed out")
                return AIResponse(
                    success=False,
                    response="The request took too long to process. Please try again.",
                    intent="UNKNOWN"
                )
            except Exception as e:
                logger.error(f"Unexpected error processing command: {str(e)}")
                retry_count += 1
                last_error = str(e)
                if retry_count < self.max_retries:
                    wait_time = 2 ** retry_count
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    return AIResponse(
                        success=False,
                        response="I'm sorry, I encountered an error processing your request. Please try again.",
                        intent="UNKNOWN"
                    )

        # If all retries failed
        logger.error(f"All retries failed. Last error: {last_error}")
        return AIResponse(
            success=False,
            response="I'm experiencing technical difficulties. Please try again later.",
            intent="UNKNOWN"
        )

    def validate_intent(self, intent: str) -> bool:
        """
        Validate if the detected intent is one we support
        """
        valid_intents = ["CREATE", "UPDATE", "DELETE", "QUERY", "UNKNOWN"]
        return intent in valid_intents


# Global instance of the AI service
ai_service = AIService()