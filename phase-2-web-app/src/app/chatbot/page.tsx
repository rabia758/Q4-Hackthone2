'use client';

import React, { useState, useEffect } from 'react';
import ChatInterface from '../../components/chatbot/ChatInterface';
import { v4 as uuidv4 } from 'uuid';
import Link from 'next/link';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

interface Todo {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at?: string;
  updated_at?: string;
  user_id: string;
}

export default function ChatbotPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: uuidv4(),
      text: "Hello! I'm your AI Todo Assistant. I can help you manage your tasks. Try asking 'Add a task to buy milk' or 'Show my tasks'.",
      sender: 'ai',
      timestamp: new Date(),
    }
  ]);
  const [todos, setTodos] = useState<Todo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  async function fetchTodos(token: string) {
    try {
      const res = await fetch(`${API_URL}/todos`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setTodos(data);
      } else {
        console.error("Failed to fetch todos");
      }
    } catch (error) {
      console.error("Error fetching todos:", error);
    }
  }

  // Clear messages after 3 seconds
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  async function fetchChatHistory(token: string) {
    try {
      const res = await fetch(`${API_URL}/chatbot/history`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        // Backend returns { messages: [ {message, response, created_at, ...}, ... ] }
        // We need to transform this into our Message format (User msg -> AI msg)
        
        const historyMessages: Message[] = [];
        
        // Add welcome message first
        historyMessages.push({
          id: 'welcome-msg',
          text: "Hello! I'm your AI Todo Assistant. I can help you manage your tasks. Try asking 'Add a task to buy milk' or 'Show my tasks'.",
          sender: 'ai',
          timestamp: new Date(), // Just now
        });

        // The backend returns messages oldest to newest usually, or we should sort.
        // Assuming backend sends chronologically or we reverse if needed. 
        // Let's assume standard order.
        data.messages.forEach((msg: any) => {
            // User message
            historyMessages.push({
                id: `user-${msg.id}`,
                text: msg.message,
                sender: 'user',
                timestamp: msg.created_at ? new Date(msg.created_at) : new Date(),
            });
            // AI response
            historyMessages.push({
                id: `ai-${msg.id}`,
                text: msg.response,
                sender: 'ai',
                timestamp: msg.created_at ? new Date(msg.created_at) : new Date(),
            });
        });

        setMessages(historyMessages);
      }
    } catch (error) {
      console.error("Error fetching chat history:", error);
    }
  }

  // Load auth token from localStorage on mount
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      setAuthToken(token);
      fetchTodos(token);
      fetchChatHistory(token);
    }
  }, []);

  if (!authToken) {
    return (
      <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center p-4">
        <div className="bg-gray-800 p-8 rounded-2xl shadow-2xl border border-gray-700 max-w-md w-full text-center">
            <h2 className="text-2xl font-bold text-white mb-4">Authentication Required</h2>
            <p className="text-gray-400 mb-6">You need to be signed in to access the AI Assistant.</p>
            <Link 
                href="/" 
                className="inline-block px-8 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold rounded-xl shadow-lg hover:shadow-purple-500/25 transition-all"
            >
                Go to Login
            </Link>
        </div>
      </div>
    );
  }


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
      const response = await fetch(`${API_URL}/chatbot/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}` // Include auth token
        },
        body: JSON.stringify({ message }),
      });

      let responseText = "I'm sorry, I couldn't process your request.";

      if (response.ok) {
          const data = await response.json();
          console.log("Chatbot response data:", data); // For debugging
          responseText = data.response || "I processed your request successfully.";

          // If the response includes a new todo (for real-time updates), add it to our todo list
          if (data.action_result) {
            if (data.intent === 'CREATE') {
                setTodos(prev => [data.action_result, ...prev]);
                setSuccessMessage('Task added successfully! 🚀');
            } else if (data.intent === 'UPDATE') {
                setTodos(prev => prev.map(t => t.id === data.action_result.id ? data.action_result : t));
                setSuccessMessage('Task updated successfully! ✨');
            } else if (data.intent === 'DELETE') {
                setTodos(prev => prev.filter(t => t.id !== data.action_result.id));
                setSuccessMessage('Task moved to Trash! 🗑️');
            }
          }
      } else {
          const errorData = await response.json().catch(() => ({}));
          console.error("Chatbot API error:", errorData);
          responseText = errorData.detail || `Error: ${response.status} - ${response.statusText}. Backend might not be running or AI service not configured.`;
      }

      // Add AI response to the chat
      const aiMessage: Message = {
        id: uuidv4(),
        text: responseText,
        sender: 'ai',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message to the chat
      const errorMessage: Message = {
        id: uuidv4(),
        text: "Sorry, I'm having trouble connecting to the AI service. Is the backend running?",
        sender: 'ai',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleTodo = async (id: string) => {
    const todoToToggle = todos.find(t => t.id === id);
    if (!todoToToggle || !authToken) return;

    // Optimistic Update
    const previousTodos = [...todos];
    const updatedTodos = todos.map(todo =>
        todo.id === id ? { ...todo, completed: !todo.completed } : todo
    );
    setTodos(updatedTodos);

    try {
      const res = await fetch(`${API_URL}/todos/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({
            completed: !todoToToggle.completed
        })
      });

      if (!res.ok) {
        // Revert if failed
        setTodos(previousTodos);
      }
    } catch (error) {
      console.error("Error toggling todo:", error);
      setTodos(previousTodos);
    }
  };

  const deleteTodo = async (id: string) => {
    if (!authToken) return;

    // Optimistic Update
    const previousTodos = [...todos];
    setTodos(todos.filter(todo => todo.id !== id));

    try {
        const res = await fetch(`${API_URL}/todos/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (!res.ok) {
            setTodos(previousTodos);
        }
    } catch (error) {
        console.error("Error deleting todo:", error);
        setTodos(previousTodos);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 font-sans flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex justify-between items-center">
                <div className="flex items-center space-x-8">
                    <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
                        Neon Todo
                    </h1>
                    <nav className="hidden md:flex space-x-6">
                        <Link href="/" className="text-gray-400 hover:text-purple-400 transition-colors font-medium relative group">
                            Dashboard
                            <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-purple-500 transition-all group-hover:w-full"></span>
                        </Link>
                        <Link href="/chatbot" className="text-gray-100 hover:text-purple-400 transition-colors font-medium relative group">
                            AI Chatbot
                            <span className="absolute -bottom-1 left-0 w-full h-0.5 bg-purple-500 transition-all"></span>
                        </Link>
                    </nav>
                </div>
            </div>
        </div>
      </header>

      {/* Success Toast */}
      {successMessage && (
          <div className="fixed top-24 right-4 z-50 animate-fade-in-down">
              <div className="bg-gray-800 border-l-4 border-green-500 text-green-100 p-4 rounded-r shadow-2xl flex items-center max-w-sm">
                  <div className="mr-3">
                      <svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                  </div>
                  <div>
                      <p className="font-bold">Success</p>
                      <p className="text-sm">{successMessage}</p>
                  </div>
              </div>
          </div>
      )}

      <main className="flex-1 max-w-6xl mx-auto w-full p-4 md:p-8 flex flex-col lg:flex-row gap-8">
        <div className="flex-1">
          <div className="mb-6">
              <h1 className="text-3xl font-bold text-white mb-2">AI Assistant</h1>
              <p className="text-gray-400">Chat with your personal task manager.</p>
          </div>

          <div className="min-h-[500px]">
              <ChatInterface
              onSendMessage={handleSendMessage}
              messages={messages}
              isLoading={isLoading}
              />
          </div>
        </div>

        <div className="lg:w-1/3">
          <div className="bg-gray-800/80 backdrop-blur rounded-2xl border border-gray-700/50 p-6">
            <h2 className="text-xl font-bold text-white mb-4">Your Tasks</h2>
            <div className="space-y-3 max-h-[500px] overflow-y-auto">
              {todos.length === 0 ? (
                <p className="text-gray-500 italic">No tasks yet. Add some using the chat!</p>
              ) : (
                todos.map((todo) => (
                  <div
                    key={todo.id}
                    className={`group relative bg-gray-700/50 backdrop-blur rounded-xl border border-gray-600/50 p-4 ${
                      todo.completed ? 'opacity-60' : ''
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      {/* Checkbox */}
                      <button
                        onClick={() => toggleTodo(todo.id)}
                        className={`mt-0.5 flex-shrink-0 w-5 h-5 rounded border flex items-center justify-center transition-all ${
                          todo.completed
                            ? 'bg-purple-500 border-purple-500'
                            : 'border-gray-500 hover:border-purple-400'
                        }`}
                      >
                        {todo.completed && <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>}
                      </button>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <h3 className={`text-sm font-medium truncate ${todo.completed ? 'line-through text-gray-500' : 'text-gray-200'}`}>{todo.title}</h3>
                        {todo.description && <p className="text-xs text-gray-500 mt-1">{todo.description}</p>}
                      </div>

                      {/* Actions */}
                      <button
                        onClick={() => deleteTodo(todo.id)}
                        className="p-1 text-gray-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
