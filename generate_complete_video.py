"""
Vollständiges Script zur Generierung eines Videos mit Audio
Verwendet OpenAI für Prompts, Runware für Bilder/Videos, Mirelo für Audio
"""

import os
import sys
import argparse
import requests
import tempfile
import json
import re
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from src.prompts.prompt_generator import RunwarePromptGenerator
from src.generators import AssetGenerator
from openai import OpenAI
import base64

# Environment-Variablen laden
# Explizit .env Datei im aktuellen Verzeichnis laden
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)
load_dotenv()  # Auch aus aktuellem Verzeichnis laden


def _load_image_for_analysis(image_path_or_url: str) -> tuple[str, str]:
    """
    Load image from file path or URL and return base64 data and mime type.
    
    Args:
        image_path_or_url: Path to image file or URL
        
    Returns:
        Tuple of (base64_image_data, mime_type)
    """
    if image_path_or_url.startswith(("http://", "https://")):
        # Download from URL
        response = requests.get(image_path_or_url, timeout=30)
        response.raise_for_status()
        image_data = base64.b64encode(response.content).decode('utf-8')
        
        # Determine mime type from content type or file extension
        content_type = response.headers.get('content-type', '')
        if 'image/jpeg' in content_type or 'image/jpg' in content_type:
            mime_type = 'image/jpeg'
        elif 'image/png' in content_type:
            mime_type = 'image/png'
        elif 'image/webp' in content_type:
            mime_type = 'image/webp'
        else:
            # Try to determine from URL
            if image_path_or_url.lower().endswith('.png'):
                mime_type = 'image/png'
            elif image_path_or_url.lower().endswith(('.jpg', '.jpeg')):
                mime_type = 'image/jpeg'
            else:
                mime_type = 'image/jpeg'  # Default
    else:
        # Load from file
        with open(image_path_or_url, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Determine mime type from file extension
        if image_path_or_url.lower().endswith('.png'):
            mime_type = 'image/png'
        elif image_path_or_url.lower().endswith(('.jpg', '.jpeg')):
            mime_type = 'image/jpeg'
        elif image_path_or_url.lower().endswith('.webp'):
            mime_type = 'image/webp'
        else:
            mime_type = 'image/jpeg'  # Default
    
    return image_data, mime_type


def _refine_user_context_with_chatgpt(
    openai_client: OpenAI,
    theme: Optional[str],
    vibe: Optional[str],
    details: Optional[str]
) -> Dict[str, Any]:
    """
    Refine user-provided context (theme, vibe, details) using ChatGPT to make it more precise.
    
    Args:
        openai_client: OpenAI client instance
        theme: Rough theme (e.g., "Coffee Machine")
        vibe: Rough vibe (e.g., "luxury", "energetic")
        details: Additional details (e.g., "für Büro")
        
    Returns:
        Dictionary with refined theme, vibe, and details
    """
    # Build user input summary
    user_input_parts = []
    if theme:
        user_input_parts.append(f"Theme: {theme}")
    if vibe:
        user_input_parts.append(f"Vibe: {vibe}")
    if details:
        user_input_parts.append(f"Details: {details}")
    
    if not user_input_parts:
        return {"theme": None, "vibe": None, "details": None}
    
    user_input = ", ".join(user_input_parts)
    
    prompt = f"""The user has provided rough context for an e-commerce product video. Refine and expand this into precise, professional descriptions.

**USER INPUT:**
{user_input}

**TASK:**
Refine the user's rough input into precise, professional descriptions suitable for AI video generation. Return JSON in this format:

{{
  "theme": "Precise product theme/category (e.g., 'Premium Espresso Machine', 'Anti-Aging Skincare Serum', 'Wireless Headphones')",
  "vibe": "Detailed vibe description (e.g., 'Luxury premium aesthetic with sophisticated, high-end product presentation' or 'Energetic and dynamic, modern tech-forward, vibrant and colorful')",
  "details": "Expanded context details (e.g., 'Designed for busy professionals in modern office environments' or 'Perfect for active lifestyle enthusiasts')"
}}

**GUIDELINES:**
- Expand rough inputs into detailed, professional descriptions
- Make theme specific and clear
- Expand vibe into full visual/emotional description
- Expand details into comprehensive context
- Keep it professional and suitable for e-commerce advertising
- If user input is vague, make reasonable assumptions based on context

Return ONLY valid JSON, no additional text."""
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Extract JSON
        try:
            product_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            if json_start != -1:
                brace_count = 0
                json_end = json_start
                for i in range(json_start, len(response_text)):
                    if response_text[i] == '{':
                        brace_count += 1
                    elif response_text[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
                
                if brace_count == 0:
                    json_str = response_text[json_start:json_end]
                    product_data = json.loads(json_str)
                else:
                    raise ValueError("Could not find complete JSON object")
            else:
                raise ValueError("No JSON object found in response")
        
        return {
            "theme": product_data.get("theme", theme),
            "vibe": product_data.get("vibe", vibe),
            "details": product_data.get("details", details)
        }
        
    except Exception as e:
        print(f"⚠️  Error refining context: {e}")
        print("   Using original input")
        return {
            "theme": theme,
            "vibe": vibe,
            "details": details
        }


def _generate_scene_description_from_context(
    openai_client: OpenAI,
    product_data: Dict[str, Any],
    vibe: Optional[str],
    details: Optional[str]
) -> str:
    """
    Generate scene description based on product data, vibe, and details.
    
    Args:
        openai_client: OpenAI client instance
        product_data: Product data dictionary
        vibe: Vibe description
        details: Additional context details
        
    Returns:
        Scene description string
    """
    prompt = f"""Generate a detailed scene description for e-commerce product video based on the following information:

**PRODUCT INFORMATION:**
- Product: {product_data.get('product_name', 'Product')}
- Category: {product_data.get('category', 'Category')}
- Benefit: {product_data.get('benefit', 'Benefit')}
- Target Audience: {product_data.get('audience', 'Audience')}
- Brand Tone: {product_data.get('tone', 'Professional')}

**VIBE:**
{vibe or 'Professional, clean aesthetic'}

**ADDITIONAL DETAILS:**
{details or 'General use case'}

**TASK:**
Create a detailed scene description (2-3 sentences) that describes:
- Visual atmosphere and environment
- Lighting and mood
- Aesthetic style
- Setting and context

This description will be used to generate consistent visual style across all video scenes. Make it cinematic and suitable for e-commerce advertising.

Return ONLY the scene description, no additional text or formatting."""
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        scene_description = response.choices[0].message.content.strip()
        return scene_description
        
    except Exception as e:
        print(f"⚠️  Error generating scene description: {e}")
        # Fallback to default
        return (
            "Modern minimalist setting. Clean and professional aesthetic. "
            "Soft natural light. Premium quality presentation, lifestyle moment."
        )


def _generate_product_data_from_theme_and_image(
    openai_client: OpenAI,
    theme: Optional[str],
    vibe: Optional[str] = None,
    details: Optional[str] = None,
    product_image_url: str = ""
) -> Dict[str, Any]:
    """
    Generate product data based on theme, vibe, details and product image analysis.
    
    Args:
        openai_client: OpenAI client instance
        theme: Product theme/context (e.g., "Coffee Machine", "Skincare Product")
        vibe: Vibe description (optional)
        details: Additional context details (optional)
        product_image_url: URL or path to product image
        
    Returns:
        Dictionary with product data (product_name, category, benefit, audience, tone, brand_color, website)
    """
    # Load image for analysis
    try:
        image_data, mime_type = _load_image_for_analysis(product_image_url)
    except Exception as e:
        print(f"⚠️  Could not load image: {e}")
        print("   Using default product data")
        return {
            "product_name": theme or "Product",
            "category": theme or "Product Category",
            "benefit": "Main benefit or value proposition",
            "audience": "Target audience",
            "tone": "Professional",
            "brand_color": "#1a1a1a",
            "website": "https://example.com"
        }
    
    # Build prompt for product data generation
    context_parts = []
    if theme:
        context_parts.append(f"Theme: {theme}")
    if vibe:
        context_parts.append(f"Vibe: {vibe}")
    if details:
        context_parts.append(f"Details: {details}")
    
    context_section = "\n**CONTEXT:** " + ", ".join(context_parts) if context_parts else "\n**CONTEXT:** Analyze from product image"
    
    prompt = f"""Analyze this product image and generate comprehensive product data for e-commerce video advertising.

{context_section}

**TASK:**
Based on the product image (and theme if provided), generate product data in the following JSON format:

{{
  "product_name": "Specific product name or descriptive name (e.g., 'Premium Espresso Machine', 'Anti-Aging Serum')",
  "category": "Product category (e.g., 'Coffee Machine', 'Skincare', 'Electronics', 'Home Appliances')",
  "benefit": "Main benefit or value proposition (e.g., 'Perfect espresso in seconds, professional quality')",
  "audience": "Target audience (e.g., 'Coffee Enthusiasts', 'Beauty Enthusiasts', 'Tech-Savvy Professionals')",
  "tone": "Brand tone - one of: Professional, Casual, Energetic, Luxury",
  "brand_color": "Primary brand color in hex format (e.g., '#1a1a1a', '#FF5C85')",
  "website": "Example website URL (use https://example.com if not visible)"
}}

**GUIDELINES:**
- If theme is provided, use it to inform the category and context
- Analyze the product image to extract visual details
- Generate realistic, specific product data
- Choose appropriate tone based on product type and visual style
- Extract brand color from image if visible, otherwise use neutral color
- Make benefit specific and compelling for e-commerce

Return ONLY valid JSON, no additional text."""
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON from response (handle nested objects)
        # Find JSON object by finding first { and matching closing }
        try:
            # Try parsing entire response as JSON first
            product_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks or text
            # Look for JSON between ```json and ``` or just find first complete JSON object
            json_start = response_text.find('{')
            if json_start != -1:
                # Find matching closing brace
                brace_count = 0
                json_end = json_start
                for i in range(json_start, len(response_text)):
                    if response_text[i] == '{':
                        brace_count += 1
                    elif response_text[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
                
                if brace_count == 0:
                    json_str = response_text[json_start:json_end]
                    product_data = json.loads(json_str)
                else:
                    raise ValueError("Could not find complete JSON object")
            else:
                raise ValueError("No JSON object found in response")
        
        # Validate and set defaults
        return {
            "product_name": product_data.get("product_name", theme or "Product"),
            "category": product_data.get("category", theme or "Product Category"),
            "benefit": product_data.get("benefit", "Main benefit or value proposition"),
            "audience": product_data.get("audience", "Target audience"),
            "tone": product_data.get("tone", "Professional"),
            "brand_color": product_data.get("brand_color", "#1a1a1a"),
            "website": product_data.get("website", "https://example.com")
        }
        
    except Exception as e:
        print(f"⚠️  Error generating product data: {e}")
        print("   Using default product data based on theme")
        
        # Fallback: Use theme to generate basic product data
        if theme:
            category = theme
            product_name = theme
        else:
            category = "Product Category"
            product_name = "Product"
        
        return {
            "product_name": product_name,
            "category": category,
            "benefit": "Main benefit or value proposition",
            "audience": "Target audience",
            "tone": "Professional",
            "brand_color": "#1a1a1a",
            "website": "https://example.com"
        }


def main():
    """Hauptfunktion für komplette Video-Generierung"""
    
    # Argumente parsen
    parser = argparse.ArgumentParser(
        description="Generiere komplettes Video mit Bildern und Audio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiel:
  python generate_complete_video.py \\
    --image "https://example.com/product.jpg" \\
    --logo "https://example.com/logo.jpg" \\
    --output output/
        """
    )
    
    parser.add_argument(
        "--image",
        "--product-image",
        dest="product_image_url",
        type=str,
        required=True,
        help="URL oder Pfad zum Produktbild (erforderlich)"
    )
    
    parser.add_argument(
        "--logo",
        "--logo-image",
        dest="logo_url",
        type=str,
        default=None,
        help="URL oder Pfad zum Logo (optional)"
    )
    
    parser.add_argument(
        "--output",
        dest="output_dir",
        type=str,
        default="output",
        help="Output-Verzeichnis (default: output)"
    )
    
    parser.add_argument(
        "--runware-image-model",
        dest="runware_image_model",
        type=str,
        default="bfl:2@1",
        help="Runware Bild-Modell (default: bfl:2@1 für Flux 1.1 Pro, kann überschrieben werden)"
    )
    
    parser.add_argument(
        "--runware-video-model",
        dest="runware_video_model",
        type=str,
        default="klingai:6@1",
        help="Runware Video-Modell (default: klingai:6@1, kann überschrieben werden)"
    )
    
    parser.add_argument(
        "--audio-mode",
        dest="audio_mode",
        type=str,
        choices=["per-scene", "full-video"],
        default="per-scene",
        help="Audio-Generierungs-Modus: 'per-scene' (jede Szene einzeln, empfohlen) oder 'full-video' (ein Audio für gesamtes Video)"
    )
    
    parser.add_argument(
        "--theme",
        "--context",
        dest="theme",
        type=str,
        default=None,
        help="Produkt-Thema/Kontext (z.B. 'Coffee Machine', 'Skincare Product', 'Electronics', etc.). Grobe Angabe, wird mit ChatGPT präzisiert."
    )
    
    parser.add_argument(
        "--vibe",
        dest="vibe",
        type=str,
        default=None,
        help="Vibe/Stimmung (z.B. 'luxury', 'energetic', 'minimalist', 'professional', etc.). Wird mit ChatGPT präzisiert."
    )
    
    parser.add_argument(
        "--details",
        dest="details",
        type=str,
        default=None,
        help="Zusätzliche Details/Kontext (z.B. 'für Büro', 'für Zuhause', 'für Sportler', etc.). Wird mit ChatGPT präzisiert."
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("COMPLETE VIDEO GENERATION")
    print("="*80)
    print(f"📸 Product Image: {args.product_image_url}")
    print(f"🎨 Logo: {args.logo_url or 'None'}")
    print(f"🎯 Theme/Context: {args.theme or 'Will be analyzed from product image'}")
    print(f"📁 Output: {args.output_dir}")
    print(f"🖼️  Runware Image Model: {args.runware_image_model}")
    print(f"📹 Runware Video Model: {args.runware_video_model}")
    print()
    
    # API Keys prüfen
    openai_key = os.getenv("OPENAI_API_KEY")
    runware_key = os.getenv("RUNWARE_API_KEY")
    mirelo_key = os.getenv("MIRELO_API_KEY")
    
    # Debug: Zeige welche Keys gefunden wurden (ohne Werte)
    print("🔍 API Key Status:")
    print(f"   OPENAI_API_KEY: {'✅ found' if openai_key else '❌ not found'}")
    print(f"   RUNWARE_API_KEY: {'✅ found' if runware_key else '❌ not found'}")
    print(f"   MIRELO_API_KEY: {'✅ found' if mirelo_key else '❌ not found'}")
    
    # Prüfe auch alternative Schreibweisen
    if not mirelo_key:
        # Versuche alternative Namen
        mirelo_key = os.getenv("MIRELO_KEY") or os.getenv("mirelo_api_key") or os.getenv("Mirelo_API_Key")
        if mirelo_key:
            print(f"   ⚠️  MIRELO_API_KEY not found, but alternative key found")
    
    errors = []
    if not openai_key:
        errors.append("❌ OPENAI_API_KEY not found")
    if not runware_key:
        errors.append("❌ RUNWARE_API_KEY not found")
    if not mirelo_key:
        errors.append("❌ MIRELO_API_KEY not found")
        # Zeige alle Environment-Variablen mit "MIRELO" im Namen
        mirelo_vars = {k: v[:10] + "..." if v else "None" for k, v in os.environ.items() if "MIRELO" in k.upper()}
        if mirelo_vars:
            print(f"\n   Found MIRELO variables: {list(mirelo_vars.keys())}")
    
    if errors:
        print("\nERRORS:")
        for error in errors:
            print(f"   {error}")
        print("\n💡 Make sure all API keys are set in .env file")
        print(f"💡 .env file should be in directory: {os.path.dirname(__file__)}")
        sys.exit(1)
    
    print("✅ All API keys found\n")
    
    try:
        # Schritt 1: Prompts generieren mit OpenAI
        print("="*80)
        print("STEP 1: GENERATE PROMPTS (OpenAI)")
        print("="*80)
        
        prompt_generator = RunwarePromptGenerator(openai_api_key=openai_key)
        openai_client = OpenAI(api_key=openai_key)
        
        # Schritt 1a: Präzisiere User-Input (Theme, Vibe, Details) mit ChatGPT
        if args.theme or args.vibe or args.details:
            print("🔄 Refining theme, vibe and details with ChatGPT...")
            refined_context = _refine_user_context_with_chatgpt(
                openai_client=openai_client,
                theme=args.theme,
                vibe=args.vibe,
                details=args.details
            )
            print(f"✅ Refined context:")
            print(f"   🎯 Theme: {refined_context.get('theme', 'N/A')}")
            print(f"   🎨 Vibe: {refined_context.get('vibe', 'N/A')}")
            print(f"   📝 Details: {refined_context.get('details', 'N/A')}")
            print()
        else:
            refined_context = {
                "theme": None,
                "vibe": None,
                "details": None
            }
        
        # Schritt 1b: Produkt-Daten generieren basierend auf präzisiertem Kontext und Produktbild
        print("🔄 Analyzing product image and generating product data...")
        product_data = _generate_product_data_from_theme_and_image(
            openai_client=openai_client,
            theme=refined_context.get("theme"),
            vibe=refined_context.get("vibe"),
            details=refined_context.get("details"),
            product_image_url=args.product_image_url
        )
        
        print(f"✅ Product data generated:")
        print(f"   📦 Product: {product_data['product_name']}")
        print(f"   📂 Category: {product_data['category']}")
        print(f"   ✨ Benefit: {product_data['benefit']}")
        print(f"   👥 Target Audience: {product_data['audience']}")
        print()
        
        # Schritt 1c: Scene Description generieren basierend auf präzisiertem Kontext
        print("🔄 Generating scene description based on context...")
        scene_description = _generate_scene_description_from_context(
            openai_client=openai_client,
            product_data=product_data,
            vibe=refined_context.get("vibe"),
            details=refined_context.get("details")
        )
        print(f"✅ Scene description generated:")
        print(f"   🎬 {scene_description[:100]}...")
        print()
        
        print("🔄 Generating image prompts...")
        image_prompts_result = prompt_generator.generate_image_prompts(
            product_data=product_data,
            scene_description=scene_description,
            product_image_path=args.product_image_url,
            logo_path=args.logo_url,
            validate=True
        )
        
        print(f"✅ {image_prompts_result['count']} image prompts generated\n")
        
        print("🔄 Generating video scenes...")
        video_scenes_result = prompt_generator.generate_video_scenes(
            product_data=product_data,
            scene_description=scene_description,
            generated_images=image_prompts_result["prompts"],
            logo_info={"description": "Logo available"} if args.logo_url else None,
            validate=True
        )
        
        print(f"✅ {video_scenes_result['count']} video scenes generated")
        print(f"📹 Total duration: {video_scenes_result['total_duration']} seconds\n")
        
        # Schritt 2: Bilder generieren mit Runware
        print("="*80)
        print("STEP 2: GENERATE IMAGES (Runware)")
        print("="*80)
        
        asset_generator = AssetGenerator(
            runware_api_key=runware_key,
            mirelo_api_key=mirelo_key,
            runware_image_model=args.runware_image_model,
            runware_video_model=args.runware_video_model,
            output_dir=args.output_dir
        )
        
        # Upload product image and logo to Runware for referenceImages (like scripts/testing_image)
        product_image_uuid = None
        logo_image_uuid = None
        
        # Download and upload product image if URL provided
        if args.product_image_url:
            try:
                print("📤 Uploading product image for image-to-image generation...")
                # Download image temporarily
                response = requests.get(args.product_image_url, timeout=30)
                response.raise_for_status()
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    tmp_file.write(response.content)
                    tmp_path = tmp_file.name
                
                # Upload to Runware
                product_image_uuid = asset_generator.runware.upload_image(tmp_path)
                print(f"✅ Product image UUID: {product_image_uuid}")
                
                # Clean up temp file
                os.unlink(tmp_path)
            except Exception as e:
                print(f"⚠️  Could not upload product image: {e}")
                print("   Using text-to-image instead of image-to-image")
        
        # Download and upload logo if provided
        if args.logo_url:
            try:
                print("📤 Uploading logo for image-to-image generation...")
                response = requests.get(args.logo_url, timeout=30)
                response.raise_for_status()
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    tmp_file.write(response.content)
                    tmp_path = tmp_file.name
                
                # Upload to Runware
                logo_image_uuid = asset_generator.runware.upload_image(tmp_path)
                print(f"✅ Logo UUID: {logo_image_uuid}")
                
                # Clean up temp file
                os.unlink(tmp_path)
            except Exception as e:
                print(f"⚠️  Could not upload logo: {e}")
        
        print("\n🔄 Generating product images with Runware (image-to-image with references)...")
        generated_images = asset_generator.generate_images(
            prompts=image_prompts_result["prompts"],
            model=args.runware_image_model,
            width=1024,
            height=1024,
            product_image_uuid=product_image_uuid,  # For referenceImages
            logo_image_uuid=logo_image_uuid,  # For referenceImages
            use_reference_images=True  # Enable image-to-image like scripts/testing_image
        )
        
        print(f"✅ {len(generated_images)} images generated")
        for img in generated_images:
            print(f"   📸 {img['use_case']}: {img.get('local_path', 'N/A')}")
        print()
        
        # Schritt 3: Videos mit Audio generieren
        print("="*80)
        print("STEP 3: GENERATE VIDEOS WITH AUDIO (Runware + Mirelo)")
        print("="*80)
        
        print("🔄 Generating video scenes with Runware...")
        
        # Entscheide, ob Audio pro Szene oder für gesamtes Video generiert wird
        generate_audio_per_scene = (args.audio_mode == "per-scene")
        
        if generate_audio_per_scene:
            print("🎵 Generating audio with Mirelo (per scene)...")
            print("   💡 Each scene receives individual audio (Hook/Problem/Solution/CTA)")
        else:
            print("🎵 Audio will be generated later for entire video...")
            print("   💡 One consistent audio for all scenes")
        
        generated_videos = asset_generator.generate_video_scenes(
            scenes=video_scenes_result["scenes"],
            generated_images=generated_images,  # Pass generated images for frameImages
            model=args.runware_video_model,
            width=1920,  # KlingAI default width
            height=1080,  # KlingAI default height
            generate_audio=generate_audio_per_scene  # Audio pro Szene nur wenn per-scene Modus
        )
        
        print(f"\n✅ {len(generated_videos)} video scenes with audio generated")
        for video in generated_videos:
            scene_num = video.get("scene_number", "?")
            print(f"\n📹 Scene {scene_num}:")
            print(f"   Video: {video.get('video_path', 'N/A')}")
            audio_files = video.get("audio_files", {})
            if audio_files.get("music"):
                print(f"   🎵 Music: {audio_files['music']}")
            if audio_files.get("sfx"):
                print(f"   🔊 SFX: {audio_files['sfx']}")
            if audio_files.get("voice"):
                print(f"   🎤 Voice: {audio_files['voice']}")
        
        # Zusammenfassung
        print("\n" + "="*80)
        print("✅ SUCCESSFULLY COMPLETED")
        print("="*80)
        print(f"📁 Output directory: {args.output_dir}")
        print(f"📸 Generated images: {len(generated_images)}")
        print(f"📹 Generated videos: {len(generated_videos)}")
        print(f"🎵 Audio files: {sum(len(v.get('audio_files', {})) for v in generated_videos)}")
        
        # Zeige final videos mit Audio
        final_videos = [v for v in generated_videos if v.get("final_video_path")]
        if final_videos:
            print(f"\n🎬 Final videos with audio: {len(final_videos)}")
            for video in final_videos:
                scene_num = video.get("scene_number", "?")
                final_path = video.get("final_video_path")
                print(f"   📹 Scene {scene_num}: {os.path.basename(final_path)}")
        
        # Schritt 4: Videos zu einem finalen Video kombinieren
        if final_videos:
            print("\n" + "="*80)
            print("STEP 4: COMBINE FINAL VIDEO")
            print("="*80)
            
            # Sortiere Videos nach scene_number für richtige Reihenfolge
            sorted_videos = sorted(
                final_videos,
                key=lambda v: v.get("scene_number", 999)
            )
            
            # Sammle alle Video-Pfade in richtiger Reihenfolge
            video_paths = [v.get("final_video_path") for v in sorted_videos]
            video_paths = [p for p in video_paths if p and os.path.exists(p)]
            
            if video_paths:
                print(f"🔄 Combining {len(video_paths)} videos into final video...")
                
                # Importiere Funktionen
                from scripts.utils.video_audio_merger import concatenate_videos_with_transitions
                
                # Erstelle finales Video im output-Verzeichnis
                final_output_path = os.path.join(args.output_dir, "final_video.mp4")
                
                # Verwende Crossfade-Transitions für smooth Übergänge
                # Transition-Dauer: 0.3 Sekunden (subtile Crossfades, Szenen bleiben getrennt)
                success = concatenate_videos_with_transitions(
                    video_paths=video_paths,
                    output_path=final_output_path,
                    transition_duration=0.3,  # 0.3 Sekunden Crossfade - Frames überblenden, nicht fade to black
                    verbose=True
                )
                
                if success:
                    print(f"✅ Final video created: {final_output_path}")
                    print(f"   📹 Contains {len(video_paths)} scenes in correct order")
                    print(f"   🎬 With crossfade transitions (0.3s) - frames blend, scenes remain separated")
                    print(f"   🎵 Audio crossfades for smooth sound transitions")
                else:
                    print("❌ Error combining videos")
            else:
                print("⚠️  No valid video paths found")
        
        # Alternative: Wenn audio_mode="full-video", kombiniere Videos zuerst, dann generiere Audio
        elif args.audio_mode == "full-video" and generated_videos:
            print("\n" + "="*80)
            print("STEP 4: COMBINE VIDEOS, THEN GENERATE AUDIO")
            print("="*80)
            
            # Sortiere Videos nach scene_number
            sorted_videos = sorted(
                generated_videos,
                key=lambda v: v.get("scene_number", 999)
            )
            
            # Sammle Video-Pfade (ohne Audio)
            video_paths = [v.get("video_path") for v in sorted_videos]
            video_paths = [p for p in video_paths if p and os.path.exists(p)]
            
            if video_paths:
                print(f"🔄 Combining {len(video_paths)} videos into one video (without audio)...")
                
                from scripts.utils.video_audio_merger import concatenate_videos
                
                # Temporäres Video ohne Audio
                temp_video_path = os.path.join(args.output_dir, "temp_combined_video.mp4")
                
                success = concatenate_videos(
                    video_paths=video_paths,
                    output_path=temp_video_path,
                    verbose=True
                )
                
                if success:
                    print(f"✅ Videos combined: {temp_video_path}")
                    
                    # Generiere Audio für das gesamte Video
                    print(f"\n🎵 Generating audio for entire video...")
                    
                    # Kombiniere Audio-Designs aller Szenen für ein konsistentes Audio
                    combined_audio_design = {
                        "music": "Professional, dynamic background music that builds throughout the video",
                        "sfx": "Synchronized sound effects matching the video content",
                        "dialog": "Engaging narration that guides through the product story"
                    }
                    
                    # Get total duration
                    total_duration = sum(v.get("duration", 10) for v in sorted_videos)
                    
                    # Generate audio for full video
                    audio_files = asset_generator._generate_scene_audio_from_video(
                        temp_video_path,
                        combined_audio_design,
                        int(total_duration)
                    )
                    
                    if audio_files.get("audio"):
                        # Merge video and audio
                        final_output_path = os.path.join(args.output_dir, "final_video.mp4")
                        from scripts.utils.video_audio_merger import merge_video_audio
                        
                        success = merge_video_audio(
                            temp_video_path,
                            audio_files["audio"],
                            final_output_path
                        )
                        
                        if success:
                            print(f"✅ Final video with audio created: {final_output_path}")
                            # Clean up temp file
                            try:
                                os.remove(temp_video_path)
                            except:
                                pass
                        else:
                            print("❌ Error merging video and audio")
                    else:
                        print("❌ Error generating audio")
                else:
                    print("❌ Error combining videos")
        
        print("\n💡 Next steps:")
        if final_videos:
            print("   ✅ Videos have already been merged with audio")
            final_output = os.path.join(args.output_dir, "final_video.mp4")
            if os.path.exists(final_output):
                print(f"   ✅ Final video was created: final_video.mp4")
            else:
                print("   - Videos can be combined into a final video with FFmpeg")
        else:
            print("   - Videos can be combined with FFmpeg")
            print("   - Audio can be added to videos with FFmpeg")
            print("   - Create final 30-second video")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

