# Generators Module - Runware & Mirelo Integration

Dieses Modul integriert Runware.ai für Bild- und Video-Generierung sowie Mirelo für Audio-Generierung.

## Architektur

### OpenAI (Analyse & Prompts)
- **GPT-4o Vision**: Produktbild- und Logo-Analyse
- **GPT-4o Chat**: Prompt-Generierung für Runware

### Runware (Bild & Video Generierung)
- **Default Bild-Modell**: `bfl:2@1` (Flux 1.1 Pro, kann vom User überschrieben werden)
- **Default Video-Modell**: `klingai:6@1` (kann vom User überschrieben werden)
- **Flexible Modelle**: User kann beide Modelle überschreiben
- **Bilder**: 1024x1024 professionelle Produktbilder
- **Videos**: 1920x1080 (HD) Video-Szenen (KlingAI Standard)

### Mirelo (Audio Generierung)
- **Background Music**: Basierend auf Audio-Design-Beschreibungen
- **Sound Effects**: SFX für Video-Szenen
- **Voice/Narration**: Text-to-Speech für Dialog

## Verwendung

### Basis-Setup

```python
from src.generators import AssetGenerator
import os

generator = AssetGenerator(
    runware_api_key=os.getenv("RUNWARE_API_KEY"),
    mirelo_api_key=os.getenv("MIRELO_API_KEY"),
    runware_image_model="bfl:2@1",  # Default: Flux 1.1 Pro, kann überschrieben werden
    runware_video_model="klingai:6@1",  # Default, kann überschrieben werden
    output_dir="output"
)
```

### Bilder generieren

```python
# Prompts von OpenAI Prompt Generator
prompts = [
    {
        "use_case": "Morning Routine",
        "runware_prompt": "Professional product photography..."
    },
    # ... mehr Prompts
]

# Bilder generieren
images = generator.generate_images(
    prompts=prompts,
    model="bfl:2@1",  # Optional, verwendet Default (Flux 1.1 Pro) wenn nicht angegeben
    width=1024,
    height=1024
)
```

### Videos mit Audio generieren

```python
# Video-Szenen von OpenAI Prompt Generator
scenes = [
    {
        "scene_number": 1,
        "duration": 7,
        "visual_description": "...",
        "audio_design": {
            "music": "upbeat modern electronic, 128 BPM",
            "sfx": "subtle mechanical whir",
            "dialog": "Meet the future of coffee making..."
        }
    },
    # ... mehr Szenen
]

# Videos mit Audio generieren
videos = generator.generate_video_scenes(
    scenes=scenes,
    model="klingai:6@1",  # Optional
    generate_audio=True  # Mirelo Audio generieren
)
```

## API-Konfiguration

### Runware API
- Base URL: `https://api.runware.ai/v1` (Standard)
- Endpunkte:
  - `/images/generations` - Bild-Generierung
  - `/videos/generations` - Video-Generierung
  - `/tasks/{task_id}` - Task-Status

### Mirelo API
- Base URL: `https://api.mirelo.ai/v1` (Standard)
- Endpunkte:
  - `/audio/generate` - Musik-Generierung
  - `/audio/sound-effects` - Sound-Effekte
  - `/audio/voice` - Text-to-Speech
  - `/tasks/{task_id}` - Task-Status

## Modelle

### Runware Modelle
- **Default Bild-Modell**: `bfl:2@1` (Flux 1.1 Pro)
- **Default Video-Modell**: `klingai:6@1`
- **Flexibel**: User kann beide Modelle überschreiben
- Beispiel Bild-Modelle: `"bfl:2@1"` (Flux 1.1 Pro), `"runware:101@1"`, etc.
- Beispiel Video-Modelle: `"klingai:6@1"`, `"minimax:4@1"`, etc.

### Mirelo
- Automatische Modell-Auswahl basierend auf Beschreibung
- Keine explizite Modell-Auswahl nötig

## Output-Struktur

### Generierte Bilder
```
output/
  image_1_morning_routine.png
  image_2_professional_workspace.png
  ...
```

### Generierte Videos
```
output/
  scene_1.mp4
  scene_2.mp4
  scene_3.mp4
  scene_4.mp4
  music_1234567890.mp3
  sfx_1234567890.mp3
  voice_1234567890.mp3
  ...
```

## Fehlerbehandlung

Alle API-Calls haben Timeouts und Fehlerbehandlung:
- **Runware Images**: 120s Timeout
- **Runware Videos**: 300s Timeout
- **Mirelo Audio**: 120-180s Timeout
- **Task Polling**: Automatisches Warten auf Completion

## Environment Variables

```bash
RUNWARE_API_KEY=your_runware_key
MIRELO_API_KEY=your_mirelo_key
```
