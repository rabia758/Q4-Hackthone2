'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link';

// Backend API URL - Change this if your backend runs on a different port/host
const API_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

interface Todo {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  is_deleted: boolean;
  created_at?: string;
  updated_at?: string;
}

type FilterType = 'all' | 'today' | 'completed';

export default function Home() {
  const [todos, setTodos] = useState<Todo[]>([]);
  
  // View State
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');

  // App Entry State
  const [hasEnteredApp, setHasEnteredApp] = useState(false);

  // Add Task Modal State
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newTodo, setNewTodo] = useState('');
  const [newDescription, setNewDescription] = useState('');

  // Editing state
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');

  // Auth state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<{email: string} | null>(null);
  const [token, setToken] = useState<string | null>(null);
  
  // Login form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [authError, setAuthError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Success/Error Message State
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Load auth state and todos on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('auth_user');
    
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
      setIsAuthenticated(true);
      fetchTodos(storedToken);
    }
  }, []);

  // Clear messages after 3 seconds
  useEffect(() => {
    if (successMessage || errorMessage) {
      const timer = setTimeout(() => {
        setSuccessMessage(null);
        setErrorMessage(null);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [successMessage, errorMessage]);

  const fetchTodos = async (authToken: string) => {
    try {
      const res = await fetch(`${API_URL}/todos`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setTodos(data);
      } else {
        console.error("Failed to fetch todos");
        if (res.status === 401) handleSignOut();
      }
    } catch (error) {
      console.error("Error fetching todos:", error);
      setErrorMessage("Could not connect to the server. Is the backend running?");
    }
  };

  const addTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTodo.trim() || !token) return;

    try {
      const res = await fetch(`${API_URL}/todos`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title: newTodo,
          description: newDescription || undefined,
          completed: false
        })
      });

      if (res.ok) {
        const createdTodo = await res.json();
        setTodos([createdTodo, ...todos]);
        setNewTodo('');
        setNewDescription('');
        setIsAddModalOpen(false); // Close modal on success
        setSuccessMessage('Task added successfully! 🚀');
        
        // Switch to 'all' or 'today' view to ensure the user sees their new task
        if (activeFilter === 'completed') {
            setActiveFilter('all');
        }
      } else {
          const errorData = await res.json().catch(() => ({}));
          setErrorMessage(errorData.detail || "Failed to add task");
      }
    } catch (error) {
      console.error("Error adding todo:", error);
      setErrorMessage("Network error: Could not add task.");
    }
  };

  const toggleTodo = async (id: string) => {
    const todoToToggle = todos.find(t => t.id === id);
    if (!todoToToggle || !token) return;

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
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            completed: !todoToToggle.completed
        })
      });

      if (res.ok) {
        // Show completion message
        if (!todoToToggle.completed) {
            setSuccessMessage('Task moved to Completed folder! 🎉');
        }
      } else {
        // Revert if failed
        setTodos(previousTodos);
        setErrorMessage("Failed to update task status");
      }
    } catch (error) {
        console.error("Error toggling todo:", error);
        setErrorMessage("Network error: Could not update task");
    }
  };

  const deleteTodo = async (id: string) => {
    if (!token) return;
    
    // Optimistic Update
    const previousTodos = [...todos];
    setTodos(todos.map(todo => todo.id === id ? { ...todo, is_deleted: true } : todo));

    try {
        const res = await fetch(`${API_URL}/todos/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (res.ok) {
            setSuccessMessage('Task moved to Trash! 🗑️');
        } else {
            setTodos(previousTodos);
            setErrorMessage("Failed to delete task");
        }
    } catch (error) {
        console.error("Error deleting todo:", error);
        setTodos(previousTodos);
        setErrorMessage("Network error: Could not delete task");
    }
  };

  const startEditing = (todo: Todo) => {
    setEditingId(todo.id);
    setEditTitle(todo.title);
    setEditDescription(todo.description || '');
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditTitle('');
    setEditDescription('');
  };

  const saveEdit = async (id: string) => {
    if (!editTitle.trim() || !token) return;
    
    try {
        const res = await fetch(`${API_URL}/todos/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                title: editTitle,
                description: editDescription || undefined
            })
        });

        if (res.ok) {
            const updatedTodo = await res.json();
            // Note: updatedTodo will have created_at/updated_at from backend
            setTodos(todos.map(todo => todo.id === id ? updatedTodo : todo));
            setEditingId(null);
            setSuccessMessage('Task updated successfully! ✨');
        } else {
            setErrorMessage("Failed to save changes");
        }
    } catch (error) {
        console.error("Error updating todo:", error);
        setErrorMessage("Network error: Could not save changes");
    }
  };

  const handleSignIn = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setAuthError('');
    
    if (!email.trim() || !password.trim()) {
        setAuthError('Please enter both email and password.');
        return;
    }

    setIsLoading(true);

    try {
        const res = await fetch('/api/auth', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (res.ok && data.token) {
            localStorage.setItem('auth_token', data.token);
            localStorage.setItem('auth_user', JSON.stringify(data.user));
            setToken(data.token);
            setUser(data.user);
            setIsAuthenticated(true);
            fetchTodos(data.token);
        } else {
            setAuthError(data.error || 'Login failed');
        }
    } catch (err) {
        setAuthError('An error occurred. Is the backend running?');
    } finally {
        setIsLoading(false);
    }
  };

  const handleSignOut = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    setIsAuthenticated(false);
    setHasEnteredApp(false);
    setUser(null);
    setToken(null);
    setTodos([]);
    setEmail('');
    setPassword('');
  };

  // Filter Logic - Updated: 
  // 'all': Active ONLY (!completed && !is_deleted). 
  // 'today': ALL (Active + Completed + Deleted) from today.
  // 'completed': Completed ONLY (!is_deleted).
  const getFilteredTodos = () => {
    const todayStr = new Date().toDateString();
    switch (activeFilter) {
        case 'today':
            return todos.filter(todo => {
                if (!todo.created_at) return false;
                return new Date(todo.created_at).toDateString() === todayStr;
            });
        case 'completed':
            return todos.filter(todo => todo.completed && !todo.is_deleted);
        case 'all':
        default:
            return todos.filter(todo => !todo.completed && !todo.is_deleted);
    }
  };

  const filteredTodos = getFilteredTodos();

  const getPageTitle = () => {
      switch (activeFilter) {
          case 'today': return 'My Day';
          case 'completed': return 'Completed Tasks';
          default: return 'Active Tasks';
      }
  };

  // LANDING PAGE (Authenticated but not entered)
  if (isAuthenticated && !hasEnteredApp) {
      return (
        <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center p-4 relative overflow-hidden">
            {/* Ambient Background */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-2 bg-gradient-to-r from-purple-500 via-pink-500 to-red-500 blur-sm"></div>
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-gray-800 via-gray-900 to-black opacity-40 pointer-events-none"></div>

            <div className="text-center space-y-8 max-w-lg z-10 animate-fade-in-down">
                <div className="space-y-4">
                    <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
                        Welcome to the Todo App
                    </h1>
                    <p className="text-xl text-gray-400">
                        Here is your place to maintain your todo list.
                    </p>
                </div>

                <button 
                    onClick={() => setHasEnteredApp(true)}
                    className="px-10 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white text-lg font-bold rounded-full shadow-2xl hover:shadow-purple-500/40 transform hover:-translate-y-1 transition-all duration-300 flex items-center justify-center mx-auto space-x-3 group"
                >
                    <span>Go to App</span>
                    <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path></svg>
                </button>
            </div>
            
            <div className="absolute bottom-8 text-gray-600 text-sm">
                Signed in as {user?.email}
            </div>
        </div>
      );
  }

  // LOGIN PAGE (Unauthenticated)
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="bg-gray-800 p-8 rounded-2xl shadow-2xl border border-gray-700 max-w-md w-full relative overflow-hidden">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-2 bg-gradient-to-r from-purple-500 via-pink-500 to-red-500 blur-sm"></div>
          
          <div className="text-center mb-8">
            <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600 mb-2">
              Neon Todo
            </h1>
            <p className="text-gray-400">Sign in to manage your tasks in style</p>
          </div>

          <form onSubmit={handleSignIn} className="space-y-4">
            <div>
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Email"
                    className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-xl text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                    required
                />
            </div>
            <div>
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Password"
                    className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-xl text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                    required
                />
            </div>
            
            {authError && (
                <p className="text-red-400 text-sm text-center">{authError}</p>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold py-3 px-4 rounded-xl shadow-lg hover:shadow-purple-500/30 transform hover:-translate-y-0.5 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Signing In...' : 'Sign In'}
            </button>
          </form>
          
          <div className="mt-4 text-center">
             <p className="text-gray-500 text-sm">Any email/password works for demo</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 selection:bg-pink-500 selection:text-white pb-20">
      {/* Navigation Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex justify-between items-center">
                <div className="flex items-center space-x-8">
                    <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
                        Neon Todo
                    </h1>
                    <nav className="hidden md:flex space-x-6">
                        <Link href="/" className="text-gray-100 hover:text-purple-400 transition-colors font-medium relative group">
                            Dashboard
                            <span className="absolute -bottom-1 left-0 w-full h-0.5 bg-purple-500 transition-all"></span>
                        </Link>
                        <Link href="/chatbot" className="text-gray-400 hover:text-purple-400 transition-colors font-medium relative group">
                            AI Chatbot
                            <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-purple-500 transition-all group-hover:w-full"></span>
                        </Link>
                    </nav>
                </div>
                
                <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-400 hidden sm:inline px-3 py-1 rounded-full bg-gray-800 border border-gray-700">
                        {user?.email}
                    </span>
                    <button
                        onClick={handleSignOut}
                        className="text-sm text-red-400 hover:text-red-300 transition-colors font-medium"
                    >
                        Sign Out
                    </button>
                </div>
            </div>
        </div>
      </header>

      <div className="flex min-h-[calc(100vh-80px)]">
          {/* SIDEBAR */}
          <aside className="w-64 bg-gray-800/50 border-r border-gray-700 hidden md:flex flex-col fixed h-full top-16 left-0 z-40">
            {/* Navigation */}
            <nav className="flex-1 px-3 py-6 space-y-1 overflow-y-auto">
              <button 
                onClick={() => setActiveFilter('all')}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all group ${activeFilter === 'all' ? 'bg-gray-700/80 text-white border border-gray-600/50' : 'text-gray-400 hover:text-white hover:bg-gray-700/30'}`}
              >
                <svg className={`w-5 h-5 transition-transform ${activeFilter === 'all' ? 'text-purple-400' : 'group-hover:text-purple-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h7"></path>
                </svg>
                <span className="font-medium">All Tasks</span>
                <span className="ml-auto bg-gray-700 text-xs py-0.5 px-2 rounded-full text-gray-300">
                    {todos.filter(t => !t.completed && !t.is_deleted).length}
                </span>
              </button>
              
              <button 
                onClick={() => setActiveFilter('today')}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all group ${activeFilter === 'today' ? 'bg-gray-700/80 text-white border border-gray-600/50' : 'text-gray-400 hover:text-white hover:bg-gray-700/30'}`}
              >
                <svg className={`w-5 h-5 transition-transform ${activeFilter === 'today' ? 'text-purple-400' : 'group-hover:text-purple-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
                </svg>
                <span className="font-medium">My Day</span>
              </button>

              <button 
                onClick={() => setActiveFilter('completed')}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all group ${activeFilter === 'completed' ? 'bg-gray-700/80 text-white border border-gray-600/50' : 'text-gray-400 hover:text-white hover:bg-gray-700/30'}`}
              >
                <svg className={`w-5 h-5 transition-transform ${activeFilter === 'completed' ? 'text-purple-400' : 'group-hover:text-purple-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span className="font-medium">Completed</span>
                <span className="ml-auto bg-gray-700 text-xs py-0.5 px-2 rounded-full text-gray-300">
                    {todos.filter(t => t.completed && !t.is_deleted).length}
                </span>
              </button>
            </nav>

            {/* User Profile Footer */}
            <div className="p-4 border-t border-gray-700 mt-auto">
              <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3 overflow-hidden">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-purple-500 to-pink-500 flex items-center justify-center text-xs font-bold shadow-lg">
                        {user?.email[0].toUpperCase()}
                    </div>
                    <div className="flex flex-col min-w-0">
                        <span className="text-sm font-medium text-white truncate">{user?.email}</span>
                        <span className="text-xs text-gray-500">Free Plan</span>
                    </div>
                  </div>
              </div>
            </div>
          </aside>

          {/* MAIN CONTENT */}
          <main className="flex-1 flex flex-col relative min-w-0 md:ml-64">
            
            {/* Content Header (Sub-header) */}
            <div className="flex items-center justify-between px-6 py-6">
                <div>
                    <h2 className="text-2xl font-bold text-gray-100">{getPageTitle()}</h2>
                    <p className="text-sm text-gray-500 mt-1">{new Date().toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' })}</p>
                </div>

                <div className="hidden md:block">
                    <button 
                        onClick={() => setIsAddModalOpen(true)}
                        className="flex items-center space-x-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 hover:border-purple-500/50 text-gray-200 px-4 py-2 rounded-lg transition-all text-sm font-medium"
                    >
                        <svg className="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path>
                        </svg>
                        <span>Manual Add Task</span>
                    </button>
                </div>

                {/* Mobile Add Button */}
                <button 
                    onClick={() => setIsAddModalOpen(true)}
                    className="md:hidden bg-gradient-to-r from-purple-600 to-pink-600 text-white p-3 rounded-full shadow-lg"
                >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path>
                    </svg>
                </button>
            </div>

            {/* Content Scroll Area */}
            <div className="flex-1 overflow-y-auto px-6 pb-20">
              
              {/* Toasts */}
              {(successMessage || errorMessage) && (
                  <div className="fixed top-24 right-4 z-50 animate-fade-in-down">
                      <div className={`border-l-4 p-4 rounded-r shadow-2xl flex items-center max-w-sm ${successMessage ? 'bg-gray-800 border-green-500 text-green-100' : 'bg-gray-800 border-red-500 text-red-100'}`}>
                          <div className="mr-3">
                              {successMessage ? (
                                  <svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                              ) : (
                                  <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                              )}
                          </div>
                          <div>
                              <p className="font-bold">{successMessage ? "Success" : "Error"}</p>
                              <p className="text-sm">{successMessage || errorMessage}</p>
                          </div>
                      </div>
                  </div>
              )}

              {/* Task List */}
              <div className="space-y-3">
                  {filteredTodos.length === 0 ? (
                      <div className="flex flex-col items-center justify-center py-24 text-center opacity-50">
                        <svg className="w-24 h-24 text-gray-700 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                        </svg>
                        <p className="text-xl font-medium text-gray-400">
                            {activeFilter === 'completed' 
                                ? "No completed tasks yet" 
                                : "No active tasks found"}
                        </p>
                        <p className="text-gray-600 mt-2">
                            {activeFilter === 'completed' 
                                ? "Complete some tasks to see them here." 
                                : "Click 'Manual Add Task' to create one."}
                        </p>
                      </div>
                  ) : (
                      filteredTodos.map((todo) => (
                        <div
                          key={todo.id}
                          className={`group relative bg-gray-800/80 backdrop-blur rounded-xl border border-gray-700/50 hover:border-purple-500/30 transition-all duration-200 hover:shadow-lg hover:shadow-purple-900/10 ${
                            todo.completed || todo.is_deleted ? 'opacity-70' : ''
                          }`}
                        >
                          <div className="p-4 flex items-start space-x-4">
                              {/* Checkbox */}
                              <button
                                  onClick={() => !todo.is_deleted && toggleTodo(todo.id)}
                                  className={`mt-1 flex-shrink-0 w-5 h-5 rounded border flex items-center justify-center transition-all ${
                                      todo.is_deleted ? 'bg-gray-700 border-gray-600 cursor-not-allowed' :
                                      todo.completed 
                                          ? 'bg-purple-500 border-purple-500' 
                                          : 'border-gray-500 hover:border-purple-400'
                                  }`}
                                  disabled={todo.is_deleted}
                                  title={todo.is_deleted ? "Task deleted" : todo.completed ? "Mark as active" : "Mark as completed"}
                              >
                                  {todo.completed && <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>}
                              </button>

                              {/* Content */}
                              <div className="flex-1 min-w-0">
                                  {editingId === todo.id ? (
                                      <div className="space-y-3 animate-fade-in">
                                          <input
                                              type="text"
                                              value={editTitle}
                                              onChange={(e) => setEditTitle(e.target.value)}
                                              className="w-full bg-gray-900 border border-gray-600 rounded p-2 text-white text-sm focus:border-purple-500 focus:outline-none"
                                              autoFocus
                                          />
                                          <input
                                              type="text"
                                              value={editDescription}
                                              onChange={(e) => setEditDescription(e.target.value)}
                                              placeholder="Description"
                                              className="w-full bg-gray-900 border border-gray-600 rounded p-2 text-gray-400 text-xs focus:border-purple-500 focus:outline-none"
                                          />
                                          <div className="flex space-x-2">
                                              <button onClick={() => saveEdit(todo.id)} className="text-xs bg-purple-600 text-white px-3 py-1 rounded hover:bg-purple-500">Save</button>
                                              <button onClick={cancelEdit} className="text-xs bg-gray-700 text-white px-3 py-1 rounded hover:bg-gray-600">Cancel</button>
                                          </div>
                                      </div>
                                  ) : (
                                      <>
                                          <h3 className={`text-sm font-medium truncate ${todo.completed || todo.is_deleted ? 'line-through text-gray-500' : 'text-gray-200'}`}>
                                              {activeFilter === 'today' && (
                                                  <span className={`mr-2 text-[10px] font-bold px-1.5 py-0.5 rounded ${
                                                      todo.is_deleted ? 'bg-red-500/20 text-red-400' : 
                                                      todo.completed ? 'bg-green-500/20 text-green-400' : 
                                                      'bg-blue-500/20 text-blue-400'
                                                  }`}>
                                                      {todo.is_deleted ? 'DELETED' : todo.completed ? 'COMPLETED' : 'ACTIVE'}
                                                  </span>
                                              )}
                                              {todo.title}
                                          </h3>
                                          {todo.description && <p className="text-xs text-gray-500 mt-0.5">{todo.description}</p>}
                                          <div className="flex items-center mt-2 space-x-4">
                                              <span className="text-[10px] text-gray-600 uppercase tracking-wide flex items-center">
                                                  <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                                                  {todo.created_at 
                                                      ? new Date(todo.created_at).toLocaleString(undefined, { 
                                                          month: 'short', 
                                                          day: 'numeric', 
                                                          hour: '2-digit', 
                                                          minute: '2-digit' 
                                                        }) 
                                                      : 'Just now'}
                                              </span>
                                          </div>
                                      </>
                                  )}
                              </div>

                              {/* Actions */}
                              <div className="flex items-center space-x-1 opacity-100 transition-opacity">
                                  {!todo.is_deleted && (
                                      <button onClick={() => startEditing(todo)} className="p-1.5 text-gray-500 hover:text-purple-400 hover:bg-gray-700 rounded-lg transition-colors">
                                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                                      </button>
                                  )}
                                  <button onClick={() => deleteTodo(todo.id)} className="p-1.5 text-gray-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors" title={todo.is_deleted ? "Permanently Delete" : "Delete"}>
                                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                                  </button>
                              </div>
                          </div>
                        </div>
                      ))
                  )}
              </div>
            </div>
          </main>
      </div>

      {/* Add Task Modal/Overlay */}
      {isAddModalOpen && (
          <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
              <div className="bg-gray-800 rounded-2xl shadow-2xl border border-gray-700 w-full max-w-lg overflow-hidden animate-fade-in-down">
                  <div className="p-6">
                      <div className="flex justify-between items-center mb-6">
                          <h2 className="text-xl font-bold text-white">Add New Task</h2>
                          <button onClick={() => setIsAddModalOpen(false)} className="text-gray-400 hover:text-white transition-colors">
                              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                          </button>
                      </div>
                      
                      <form onSubmit={addTodo} className="space-y-4">
                          <div>
                              <label className="block text-sm font-medium text-gray-400 mb-1">Title</label>
                              <input
                                  type="text"
                                  value={newTodo}
                                  onChange={(e) => setNewTodo(e.target.value)}
                                  placeholder="What needs to be done?"
                                  className="w-full px-4 py-2.5 bg-gray-900 border border-gray-600 rounded-xl text-white placeholder-gray-500 focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all"
                                  autoFocus
                              />
                          </div>
                          <div>
                              <label className="block text-sm font-medium text-gray-400 mb-1">Description <span className="text-gray-600">(Optional)</span></label>
                              <textarea
                                  value={newDescription}
                                  onChange={(e) => setNewDescription(e.target.value)}
                                  placeholder="Add details..."
                                  rows={3}
                                  className="w-full px-4 py-2.5 bg-gray-900 border border-gray-600 rounded-xl text-white placeholder-gray-500 focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all resize-none"
                              />
                          </div>
                          
                          <div className="flex space-x-3 pt-4">
                              <button 
                                type="button" 
                                onClick={() => setIsAddModalOpen(false)}
                                className="flex-1 px-4 py-2.5 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded-xl transition-colors"
                              >
                                  Cancel
                              </button>
                              <button 
                                type="submit" 
                                className="flex-1 px-4 py-2.5 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-bold rounded-xl shadow-lg hover:shadow-purple-500/25 transition-all"
                              >
                                  Create Task
                              </button>
                          </div>
                      </form>
                  </div>
              </div>
          </div>
      )}

    </div>
  );
}