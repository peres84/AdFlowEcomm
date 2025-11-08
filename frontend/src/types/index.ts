/**
 * Common types for ProductFlow application
 */

export interface FormData {
  product_name: string;
  category: string;
  target_audience: string;
  main_benefit: string;
  brand_colors: string[];
  brand_tone: string;
  target_platform: string;
  website_url: string;
  scene_description: string;
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
