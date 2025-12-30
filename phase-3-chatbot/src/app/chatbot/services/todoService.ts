// Mock todo service for demonstration purposes
// In a real implementation, this would connect to the actual todo API

interface Todo {
  id: string;
  title: string;
  completed: boolean;
  user_id: string;
  created_at?: string;
}

let mockTodos: Todo[] = [];

export const todoService = {
  // Get all todos for the user
  getTodos: async (userId: string): Promise<Todo[]> => {
    // In a real implementation, this would make an API call
    return mockTodos.filter(todo => todo.user_id === userId);
  },

  // Add a new todo
  addTodo: async (title: string, userId: string): Promise<Todo> => {
    const newTodo: Todo = {
      id: `todo_${Date.now()}`,
      title,
      completed: false,
      user_id: userId,
      created_at: new Date().toISOString()
    };

    mockTodos.push(newTodo);
    return newTodo;
  },

  // Update a todo
  updateTodo: async (id: string, updates: Partial<Todo>): Promise<Todo | null> => {
    const index = mockTodos.findIndex(todo => todo.id === id);
    if (index !== -1) {
      mockTodos[index] = { ...mockTodos[index], ...updates };
      return mockTodos[index];
    }
    return null;
  },

  // Delete a todo
  deleteTodo: async (id: string): Promise<boolean> => {
    const initialLength = mockTodos.length;
    mockTodos = mockTodos.filter(todo => todo.id !== id);
    return mockTodos.length < initialLength;
  }
};