# Prompt-Konfiguration

Diese Datei erklärt, wie du die zentrale Prompt-Konfiguration (`prompts_config.py`) verwendest und anpasst.

## 📁 Datei-Struktur

```
src/prompts/
├── prompts_config.py          # ⭐ ZENTRALE PROMPT-DATEI (hier alles anpassen!)
├── system_prompts.py          # Importiert aus prompts_config.py (für Kompatibilität)
├── image_prompts.py           # Verwendet IMAGE_GENERATION_SYSTEM_PROMPT
└── video_prompts.py           # Verwendet VIDEO_GENERATION_SYSTEM_PROMPT
```

## 🎯 Verwendung

### Alle Prompts anpassen

Öffne `src/prompts/prompts_config.py` und passe die folgenden Variablen an:

1. **`IMAGE_GENERATION_SYSTEM_PROMPT`** - System-Prompt für Bild-Prompt-Generierung
2. **`VIDEO_GENERATION_SYSTEM_PROMPT`** - System-Prompt für Video-Szenen-Generierung
3. **`PRODUCT_IMAGE_ANALYSIS_PROMPT`** - Anweisung für Produktbild-Analyse
4. **`LOGO_ANALYSIS_PROMPT`** - Anweisung für Logo-Analyse
5. **`DEFAULT_SCENE_DESCRIPTION`** - Standard-Szene-Beschreibung
6. **`DEFAULT_PRODUCT_DATA`** - Standard-Produkt-Daten

### Beispiel-Anpassungen

#### 1. Mehr kreative Bilder

```python
# In prompts_config.py, ändere IMAGE_GENERATION_SYSTEM_PROMPT:
IMAGE_GENERATION_SYSTEM_PROMPT = IMAGE_GENERATION_SYSTEM_PROMPT.replace(
    "professional, social-media-ready",
    "artistic, creative, unique, social-media-ready"
)
```

#### 2. Kürzere Video-Szenen

```python
# In prompts_config.py, ändere VIDEO_GENERATION_SYSTEM_PROMPT:
VIDEO_GENERATION_SYSTEM_PROMPT = VIDEO_GENERATION_SYSTEM_PROMPT.replace(
    "Scene 1 (Hook): 7 seconds",
    "Scene 1 (Hook): 5 seconds"
).replace(
    "Scene 2 (Problem): 7 seconds",
    "Scene 2 (Problem): 5 seconds"
)
```

#### 3. Andere Standard-Szene-Beschreibung

```python
# In prompts_config.py:
DEFAULT_SCENE_DESCRIPTION = (
    "Luxury lifestyle setting. Premium materials, golden hour lighting. "
    "Aspirational mood, high-end aesthetic."
)
```

#### 4. Andere Standard-Produkt-Daten

```python
# In prompts_config.py:
DEFAULT_PRODUCT_DATA = {
    "product_name": "Mein Produkt",
    "category": "Kategorie",
    "benefit": "Hauptvorteil",
    "audience": "Zielgruppe",
    "tone": "Casual",  # Professional, Casual, Energetic, Luxury
    "brand_color": "#FF5733",
    "website": "https://meine-website.com"
}
```

## 🔄 Nach Änderungen

- **Kein Neustart nötig**: Die Änderungen werden beim nächsten Script-Aufruf automatisch verwendet
- **Testen**: Teste die Änderungen mit einem kleinen Beispiel
- **Backup**: Erstelle ein Backup vor größeren Änderungen

## 📝 Struktur der Prompts

### IMAGE_GENERATION_SYSTEM_PROMPT

Definiert, wie OpenAI Bild-Prompts für Runware generiert:
- Anzahl der Prompts (standardmäßig 4)
- Format der Ausgabe
- Anforderungen an Details (Lighting, Composition, etc.)
- Logo-Integration

### VIDEO_GENERATION_SYSTEM_PROMPT

Definiert, wie OpenAI Video-Szenen generiert:
- Anzahl der Szenen (standardmäßig 4: Hook, Problem, Solution, CTA)
- Timing pro Szene
- Audio-Design-Anforderungen
- Format der Ausgabe

### PRODUCT_IMAGE_ANALYSIS_PROMPT

Anweisung für die Analyse von Produktbildern:
- Was soll extrahiert werden?
- Welche Details sind wichtig?

### LOGO_ANALYSIS_PROMPT

Anweisung für die Logo-Analyse:
- Logo-Stil, Farben, Design-Elemente
- Platzierungs-Optionen

## ⚠️ Wichtige Hinweise

1. **Format beibehalten**: Die Ausgabe-Formate müssen genau eingehalten werden, sonst funktioniert das Parsing nicht
2. **Timing**: Video-Szenen-Timing muss zur Gesamt-Dauer passen (standardmäßig 30 Sekunden)
3. **Kompatibilität**: `system_prompts.py` importiert aus `prompts_config.py` für Rückwärts-Kompatibilität

## 🐛 Troubleshooting

### Prompts werden nicht verwendet

- Stelle sicher, dass `system_prompts.py` korrekt aus `prompts_config.py` importiert
- Prüfe, ob es Import-Fehler gibt

### Parsing-Fehler

- Überprüfe das Ausgabe-Format in den System-Prompts
- Stelle sicher, dass die Format-Anweisungen klar sind

### Unerwartete Ergebnisse

- Teste mit einem kleinen Beispiel
- Überprüfe die Prompt-Logik in `prompts_config.py`
- Stelle sicher, dass die Anweisungen klar und spezifisch sind

