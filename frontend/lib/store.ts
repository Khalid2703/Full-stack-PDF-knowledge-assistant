import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: number;
  name: string;
  email: string;
  organization?: string;
  created_at?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      login: (user, token) => {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
        set({ user, token, isAuthenticated: true });
      },
      logout: () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        set({ user: null, token: null, isAuthenticated: false });
      },
      updateUser: (updates) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...updates } : null,
        })),
    }),
    {
      name: 'auth-storage',
    }
  )
);

interface File {
  id: number;
  filename: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  page_count?: number;
  is_processed: number;
  uploaded_at: string;
}

interface FileState {
  files: File[];
  selectedFile: File | null;
  setFiles: (files: File[]) => void;
  addFile: (file: File) => void;
  removeFile: (fileId: number) => void;
  selectFile: (file: File | null) => void;
}

export const useFileStore = create<FileState>((set) => ({
  files: [],
  selectedFile: null,
  setFiles: (files) => set({ files }),
  addFile: (file) => set((state) => ({ files: [...state.files, file] })),
  removeFile: (fileId) =>
    set((state) => ({
      files: state.files.filter((f) => f.id !== fileId),
    })),
  selectFile: (file) => set({ selectedFile: file }),
}));

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: any[];
  timestamp?: string;
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  currentSession: string | null;
  addMessage: (message: Message) => void;
  setMessages: (messages: Message[]) => void;
  clearMessages: () => void;
  setLoading: (loading: boolean) => void;
  setSession: (sessionId: string) => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isLoading: false,
  currentSession: null,
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  setMessages: (messages) => set({ messages }),
  clearMessages: () => set({ messages: [] }),
  setLoading: (loading) => set({ isLoading: loading }),
  setSession: (sessionId) => set({ currentSession: sessionId }),
  clearChat: () => set({ messages: [], currentSession: null }),
}));
