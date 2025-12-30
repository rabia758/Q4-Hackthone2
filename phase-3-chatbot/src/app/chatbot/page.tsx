'use client';

import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import { v4 as uuidv4 } from 'uuid';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

interface Todo {
  id: string;
  title: string;
  completed: boolean;
  user_id: string;
  created_at?: string;
}

const ChatbotPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: uuidv4(),
      text: "Hello! I'm your AI Todo Assistant. You can ask me to create, update, or manage your todos.",
      sender: 'ai',
      timestamp: new Date(),
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [todos, setTodos] = useState<Todo[]>([]);

  const handleSendMessage = async (message: string) => {
    // Add user message to the chat
    const userMessage: Message = {
      id: uuidv4(),
      text: message,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Call the backend API to process the message
      const response = await fetch('/api/v1/chatbot/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });

      const data = await response.json();

      // Check if the response includes a new todo (for real-time updates)
      if (data.action_result && data.intent === 'CREATE') {
        // Add the new todo to our local state
        setTodos(prev => [...prev, data.action_result]);
      }

      // Add AI response to the chat
      const aiMessage: Message = {
        id: uuidv4(),
        text: data.response || "I'm sorry, I couldn't process your request.",
        sender: 'ai',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message to the chat
      const errorMessage: Message = {
        id: uuidv4(),
        text: "Sorry, I'm having trouble connecting to the AI service. Please try again later.",
        sender: 'ai',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-6xl">
      <div className="mb-6 text-center">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">AI Todo Assistant</h1>
        <p className="text-gray-600">
          Natural language interface for managing your todos
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-4 h-[600px] flex flex-col">
          <ChatInterface
            onSendMessage={handleSendMessage}
            messages={messages}
            isLoading={isLoading}
          />
        </div>

        <div className="bg-white rounded-lg shadow-lg p-4">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Your Todos</h2>
          <div className="space-y-2 max-h-[500px] overflow-y-auto">
            {todos.length === 0 ? (
              <p className="text-gray-500 italic">No todos yet. Add some using the chat!</p>
            ) : (
              todos.map(todo => (
                <div
                  key={todo.id}
                  className={`p-3 rounded-lg border ${todo.completed ? 'bg-green-50 border-green-200' : 'bg-white border-gray-200'}`}
                >
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={todo.completed}
                      onChange={() => {
                        // In a real implementation, this would update the todo via API
                        setTodos(prev =>
                          prev.map(t =>
                            t.id === todo.id ? { ...t, completed: !t.completed } : t
                          )
                        );
                      }}
                      className="mr-2 h-4 w-4"
                    />
                    <span className={`${todo.completed ? 'line-through text-gray-500' : 'text-gray-800'}`}>
                      {todo.title}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="mt-6 bg-blue-50 p-4 rounded-lg">
        <h3 className="font-semibold text-blue-800 mb-2">How to use:</h3>
        <ul className="list-disc pl-5 space-y-1 text-blue-700">
          <li>Ask me to create todos: "Add a todo to buy groceries"</li>
          <li>Ask me to update todos: "Mark the grocery todo as complete"</li>
          <li>Ask me to show your todos: "What are my todos?"</li>
          <li>Ask me to delete todos: "Delete my task to call John"</li>
        </ul>
      </div>
    </div>
  );
};

export default ChatbotPage;