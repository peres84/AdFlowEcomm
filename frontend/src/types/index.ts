/**
 * Common types for ProductFlow application
 */

export interface FormData {
  productName: string;
  category: string;
  targetAudience: string;
  mainBenefit: string;
  brandColors: string[];
  brandTone: string;
  targetPlatform: string;
  websiteUrl: string;
  sceneDescription: string;
}

export interface GeneratedImage {
  id: string;
  scenario: 'hook' | 'problem' | 'solution' | 'cta';
  useCase: string;
  prompt: string;
  imageUrl: string;
  hasLogo: boolean;
  createdAt: string;
}

export interface SceneDescription {
  scenario: 'hook' | 'problem' | 'solution' | 'cta';
  duration: number;
  visualDescription: string;
  cameraWork: string;
  lighting: string;
  audioDesign: string;
  backgroundMusic: string;
  soundEffects: string;
  dialogNarration: string;
  selectedImageId: string;
}

export interface SceneVideo {
  scenario: 'hook' | 'problem' | 'solution' | 'cta';
  videoUrl: string;
  duration: number;
  status: 'generating' | 'completed' | 'failed';
  createdAt: string;
}

export interface ApiError {
  error: boolean;
  message: string;
  details?: string;
}
