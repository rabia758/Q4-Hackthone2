"""
AI utilities for intent detection, entity extraction, and natural language processing
"""
import re
from typing import Dict, List, Tuple, Optional
import json


def detect_intent(message: str) -> Tuple[str, Dict[str, str]]:
    """
    Detect the intent from a user message and extract relevant entities
    """
    message_lower = message.lower().strip()

    # Define patterns for different intents
    create_patterns = [
        r'add a todo (?:to|for) (.+)',
        r'create (?:a |new )?task (?:to|for) (.+)',
        r'add (?:a |new )?task (?:to|for) (.+)',
        r'create a todo (?:to|for) (.+)',
        r'make (?:a |new )?todo (?:to|for) (.+)',
        r'add (.+) to my (?:todos|tasks)',
    ]

    update_patterns = [
        r'mark (?:the |my )?(.+?) (?:as )?complete',
        r'mark (?:the |my )?(.+?) (?:as )?done',
        r'complete (?:the |my )?(.+?)',
        r'finish (?:the |my )?(.+?)',
    ]

    delete_patterns = [
        r'delete (?:the |my )?(.+)',
        r'remove (?:the |my )?(.+)',
        r'get rid of (?:the |my )?(.+)',
    ]

    query_patterns = [
        r'what are my (?:todos|tasks)',
        r'show me my (?:todos|tasks)',
        r'list my (?:todos|tasks)',
        r'what (?:do I have|have I got) (?:to do|to do today)',
        r'what (?:todos|tasks) (?:do I have|have I got)',
        r'show (?:completed|done) (?:todos|tasks)',
    ]

    # Check for CREATE intent
    for pattern in create_patterns:
        match = re.search(pattern, message_lower)
        if match:
            todo_title = match.group(1).strip()
            return "CREATE", {"title": todo_title}

    # Check for UPDATE intent
    for pattern in update_patterns:
        match = re.search(pattern, message_lower)
        if match:
            todo_title = match.group(1).strip()
            return "UPDATE", {"title": todo_title, "action": "complete"}

    # Check for DELETE intent
    for pattern in delete_patterns:
        match = re.search(pattern, message_lower)
        if match:
            todo_title = match.group(1).strip()
            return "DELETE", {"title": todo_title}

    # Check for QUERY intent
    for pattern in query_patterns:
        match = re.search(pattern, message_lower)
        if match:
            query_type = "all" if "completed" not in message_lower else "completed"
            return "QUERY", {"type": query_type}

    # If no pattern matches, return UNKNOWN
    return "UNKNOWN", {}


def extract_entities(message: str) -> Dict[str, str]:
    """
    Extract named entities from a message (todo titles, dates, etc.)
    """
    entities = {}

    # Extract potential todo titles (already handled in detect_intent, but keeping for completeness)
    # Look for quoted strings which might be titles
    quoted_matches = re.findall(r'"([^"]*)"', message)
    if quoted_matches:
        entities["title"] = quoted_matches[0]  # Use first quoted string as title

    # Extract dates
    date_patterns = [
        r'today',
        r'tomorrow',
        r'next week',
        r'next month',
        r'\d{1,2}/\d{1,2}(?:/\d{2,4})?',  # MM/DD or MM/DD/YYYY
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}(?:,? \d{4})?',  # Month DD, YYYY
    ]

    for pattern in date_patterns:
        matches = re.findall(pattern, message, re.IGNORECASE)
        if matches:
            entities["due_date"] = matches[0]
            break

    return entities


def normalize_intent(intent: str) -> str:
    """
    Normalize intent to standard values
    """
    intent_map = {
        'create': 'CREATE',
        'add': 'CREATE',
        'make': 'CREATE',
        'update': 'UPDATE',
        'edit': 'UPDATE',
        'modify': 'UPDATE',
        'complete': 'UPDATE',
        'done': 'UPDATE',
        'finish': 'UPDATE',
        'delete': 'DELETE',
        'remove': 'DELETE',
        'query': 'QUERY',
        'list': 'QUERY',
        'show': 'QUERY',
        'get': 'QUERY',
    }

    normalized = intent.upper()
    if normalized in intent_map.values():
        return normalized
    elif intent.lower() in intent_map:
        return intent_map[intent.lower()]
    else:
        return "UNKNOWN"


def format_response(intent: str, entities: Dict[str, str], success: bool = True) -> str:
    """
    Format a natural language response based on intent and entities
    """
    if not success:
        return "I'm sorry, I couldn't process your request. Could you please try rephrasing?"

    if intent == "CREATE":
        title = entities.get("title", "the task")
        return f"I've created a new todo for you: '{title}'."
    elif intent == "UPDATE":
        title = entities.get("title", "the task")
        action = entities.get("action", "update")
        if action == "complete":
            return f"I've marked '{title}' as complete."
    elif intent == "DELETE":
        title = entities.get("title", "the task")
        return f"I've deleted '{title}' from your todos."
    elif intent == "QUERY":
        query_type = entities.get("type", "all")
        if query_type == "completed":
            return "Here are your completed tasks."
        else:
            return "Here are your current todos."
    else:
        return "I'm not sure how to handle that request. You can ask me to add, update, delete, or show your todos."