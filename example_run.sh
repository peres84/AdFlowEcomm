#!/bin/bash
# Beispiel: Video-Generierung mit Default-Modellen
# - Bild-Modell: bfl:2@1 (Flux 1.1 Pro) - Default
# - Video-Modell: klingai:6@1 - Default
# - Theme, Vibe, Details: Werden mit ChatGPT präzisiert

python generate_complete_video.py \
  --image "https://www.coffeeness.de/wp-content/uploads/2025/04/bosch-verocup-100-espresso-ziehen.jpg" \
  --logo "https://img.freepik.com/free-vector/colorful-bird-illustration-gradient_343694-1741.jpg?semt=ais_hybrid&w=740&q=80" \
  --theme "Coffee Machine" \
  --vibe "luxury professional" \
  --details "für moderne Küche, Premium-Qualität" \
  --output output/

