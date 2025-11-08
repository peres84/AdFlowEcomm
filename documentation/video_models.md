# Runware Video Model Providers

This table summarizes the available video model providers on Runware, their approximate maximum durations, a short description, and typical video dimensions or other requirements where available.

| Provider      | Max Duration           | Description | Typical Dimensions / Notes |
|---------------|----------------------|-------------|----------------------------|
| **OpenAI**    | Not publicly specified | Major AI research lab. Provides video models on Runware; exact durations and dimensions not clearly documented. | Check model-specific documentation; dimensions may vary. |
| **Wan**       | Not publicly specified | Likely a model supplier (possibly Chinese market). Details scarce. | Not specified. |
| **Lightricks**| Not publicly specified | Known for creative media tools (e.g., mobile apps). Duration limits not clearly shown. | Not specified. |
| **MiniMax**   | 6 s (some models) / up to 10 s (Hailuo 02) | “Hailuo” series supports text-to-video and image-to-video workflows. Advanced models allow 10 s videos. | Example payload: width & height required (e.g., 512×512). Only one frame image allowed. |
| **KlingAI**   | 10 s                  | Multiple versions (Standard, Pro, Master) supporting text-to-video and image-to-video workflows in HD. | Likely HD default (1280×720 or 1920×1080); confirm per model. |
| **ByteDance** | 10 s                  | “Seedance” models support cinematic short clips from text or images. | Typically 720p or 1080p. |
| **Google Veo**| 8 s                   | Offers cinematic-quality output, including audio support, up to ~8 s duration. | Likely HD default; verify per model. |
| **Runway**    | Not clearly specified | Runway video models available on Runware; exact duration limits not documented publicly. | Model-specific dimensions required. |
| **PixVerse**  | 8 s                   | Social-media ready clips with stylized effects. | Typically 720×720 or 1080×1080. |
| **Vidu**      | 8 s                   | Multimodal video generation (text, image, reference) with 1080p support. | 1080p recommended (1920×1080). |

---

## Payload Parameters for Video Generation (Example)

When submitting a **videoInference task**, the following parameters are typically required:

```json
{
  "taskType": "videoInference",
  "taskUUID": "your-task-uuid",
  "model": "minimax:1@1",          
  "positivePrompt": "Your prompt here",
  "duration": 6,                   
  "width": 512,                    
  "height": 512,                   
  "outputType": "URL",
  "outputFormat": "MP4",
  "deliveryMethod": "async",       
  "frameImages": [
    {"inputImage": "image-id", "frame": "first"}  
  ],
  "numberResults": 1
}
