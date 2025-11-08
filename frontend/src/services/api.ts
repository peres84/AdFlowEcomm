/**
 * API service layer for ProductFlow
 * Handles all HTTP requests to the backend
 */

import axios, { type AxiosInstance, type AxiosError } from 'axios';
import { getSessionId } from '../utils/session';
import type { FormData, GeneratedImage, SceneDescription, SceneVideo, ApiError } from '../types';

// Create axios instance with base configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 60000, // 60 seconds for long-running operations
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add session ID to all requests
apiClient.interceptors.request.use(
  (config) => {
    const sessionId = getSessionId();
    if (sessionId) {
      // Add session ID to request body or params
      if (config.method === 'get') {
        config.params = { ...config.params, session_id: sessionId };
      } else if (config.data instanceof FormData) {
        config.data.append('session_id', sessionId);
      } else {
        config.data = { ...config.data, session_id: sessionId };
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response?.data) {
      // Return structured error from backend
      return Promise.reject(error.response.data);
    }
    // Network or other errors
    return Promise.reject({
      error: true,
      message: error.message || 'An unexpected error occurred',
      details: error.toString(),
    } as ApiError);
  }
);

// Session API
export const sessionApi = {
  create: async (): Promise<{ session_id: string }> => {
    const response = await apiClient.post('/api/session/create');
    return response.data;
  },
  
  get: async (sessionId: string): Promise<any> => {
    const response = await apiClient.get(`/api/session/${sessionId}`);
    return response.data;
  },
};

// Form API
export const formApi = {
  submit: async (formData: FormData): Promise<{ success: boolean }> => {
    const response = await apiClient.post('/api/form/submit', formData);
    return response.data;
  },
};

// Upload API
export const uploadApi = {
  uploadProduct: async (file: File): Promise<{ success: boolean; image_url: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/api/upload/product', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  
  uploadLogo: async (file: File): Promise<{ success: boolean; image_url: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/api/upload/logo', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};

// Images API
export const imagesApi = {
  generate: async (): Promise<{ images: GeneratedImage[] }> => {
    const response = await apiClient.post('/api/images/generate');
    return response.data;
  },
  
  regenerate: async (
    scenario: string,
    promptModifications: string
  ): Promise<{ image: GeneratedImage }> => {
    const response = await apiClient.post('/api/images/regenerate', {
      scenario,
      prompt_modifications: promptModifications,
    });
    return response.data;
  },
};

// Scenes API
export const scenesApi = {
  generateDescriptions: async (
    selectedImages: Record<string, string>
  ): Promise<{ scenes: SceneDescription[] }> => {
    const response = await apiClient.post('/api/scenes/generate-descriptions', {
      selected_images: selectedImages,
    });
    return response.data;
  },
  
  regenerateDescription: async (
    scenario: string,
    feedback: string
  ): Promise<{ scene: SceneDescription }> => {
    const response = await apiClient.post('/api/scenes/regenerate-description', {
      scenario,
      feedback,
    });
    return response.data;
  },
};

// Videos API
export const videosApi = {
  generateScenes: async (
    sceneDescriptions: SceneDescription[]
  ): Promise<{ job_id: string }> => {
    const response = await apiClient.post('/api/videos/generate-scenes', {
      scene_descriptions: sceneDescriptions,
    });
    return response.data;
  },
  
  getStatus: async (jobId: string): Promise<{ scenes: SceneVideo[] }> => {
    const response = await apiClient.get(`/api/videos/status/${jobId}`);
    return response.data;
  },
  
  regenerateScene: async (
    scenario: string,
    sceneDescription: SceneDescription
  ): Promise<{ video_url: string }> => {
    const response = await apiClient.post('/api/videos/regenerate-scene', {
      scenario,
      scene_description: sceneDescription,
    });
    return response.data;
  },
  
  merge: async (
    sceneVideos: Record<string, string>
  ): Promise<{ final_video_url: string }> => {
    const response = await apiClient.post('/api/videos/merge', {
      scene_videos: sceneVideos,
    });
    return response.data;
  },
};

export default apiClient;
