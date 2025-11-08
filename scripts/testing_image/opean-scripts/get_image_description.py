"""
Simple script to analyze product images using OpenAI Vision API
"""

import os
import sys
import base64
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Please run: pip install openai")
    sys.exit(1)


def encode_image_to_base64(image_path: str) -> str:
    """Encode image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def analyze_product_image(image_path: str) -> dict:
    """
    Analyze a product image using OpenAI Vision API.
    
    Args:
        image_path: Path to the product image
        
    Returns:
        dict with product analysis including:
        - product_type: What kind of product it is
        - description: Detailed description
        - colors: Main colors present
        - style: Visual style/aesthetic
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Encode image
    base64_image = encode_image_to_base64(image_path)
    
    # Create the prompt for product analysis
    prompt = """Analyze this product image and provide a detailed description in JSON format with the following fields:

{
  "product_type": "What type of product is this? (e.g., cosmetic bottle, skincare jar, perfume, etc.)",
  "product_category": "General category (e.g., beauty, skincare, cosmetics, fragrance)",
  "description": "Detailed description of the product's appearance",
  "colors": ["List of main colors visible"],
  "materials": ["Materials the product appears to be made of (e.g., glass, plastic, metal)"],
  "style": "Visual style/aesthetic (e.g., minimalist, luxury, modern, vintage)",
  "shape": "Description of the product's shape and form",
  "size_estimate": "Estimated size category (e.g., small, medium, large)",
  "branding_visible": "Is there visible branding or logos? (yes/no)",
  "background": "Description of the background/setting"
}

Be specific and detailed in your analysis."""
    
    print(f"Analyzing image: {image_path}")
    print("Sending request to OpenAI Vision API...")
    
    # Call OpenAI Vision API
    response = client.chat.completions.create(
        model="gpt-4o",  # or "gpt-4-vision-preview"
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=1000,
        temperature=0.3
    )
    
    # Extract the response
    analysis_text = response.choices[0].message.content
    
    print("\n" + "="*60)
    print("PRODUCT ANALYSIS")
    print("="*60)
    print(analysis_text)
    print("="*60)
    
    return {
        "raw_response": analysis_text,
        "model": response.model,
        "usage": {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }
    }


def main():
    """Main function to run the product image analyzer."""
    if len(sys.argv) < 2:
        print("Usage: python get_image_description.py <image_path>")
        print("\nExample:")
        print("  python get_image_description.py product-image.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    try:
        result = analyze_product_image(image_path)
        
        print(f"\nTokens used: {result['usage']['total_tokens']}")
        print(f"Model: {result['model']}")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
