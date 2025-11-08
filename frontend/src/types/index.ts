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
  scenario: string;
  useCase: string;
  prompt: string;
  imageUrl: string;
  hasLogo: boolean;
  createdAt: string;
}

export interface SceneDescription {
  scenario: string;
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
  scenario: string;
  videoUrl: string;
  duration: number;
  status: string;
  createdAt: string;
}

export interface SessionData {
  sessionId: string;
  createdAt: string;
  expiresAt: string;
  formData?: FormData;
  productImageUrl?: string;
  logoImageUrl?: string;
  generatedImages?: GeneratedImage[];
  selectedImages?: Record<string, string>;
  sceneDescriptions?: SceneDescription[];
  sceneVideos?: SceneVideo[];
  finalVideoUrl?: string;
}
