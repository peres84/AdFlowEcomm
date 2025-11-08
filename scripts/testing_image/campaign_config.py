"""
Campaign Configuration Data Structure
Contains all user input fields for generating dynamic ad campaigns
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class BrandTone(Enum):
    PROFESSIONAL = "Professional"
    CASUAL = "Casual"
    ENERGETIC = "Energetic"
    LUXURY = "Luxury"


class TargetPlatform(Enum):
    INSTAGRAM_REELS = "Instagram Reels"
    TIKTOK = "TikTok"
    YOUTUBE_SHORTS = "YouTube Shorts"
    FACEBOOK = "Facebook"


@dataclass
class SceneVibeDescription:
    """
    Complete description of how the user wants ALL scenes to look, feel, and be styled.
    This is the most important field for visual consistency.
    """
    visual_style: str  # e.g., minimalist, lifestyle, cinematic, product-focused, bright, moody, premium
    lighting: str  # e.g., natural light, studio lighting, golden hour, bright and clean, soft diffused
    environment: str  # e.g., modern office, home environment, outdoor/nature, professional studio
    mood: str  # e.g., energetic and fun, luxurious and premium, real and authentic
    specific_inspirations: Optional[str] = None  # Visual references or inspirations
    avoid: Optional[str] = None  # What to avoid in the visuals
    
    def to_prompt_context(self) -> str:
        """Convert scene vibe to prompt context string."""
        context = f"{self.visual_style} visual style. {self.lighting} lighting. "
        context += f"{self.environment} environment. {self.mood} mood and atmosphere."
        
        if self.specific_inspirations:
            context += f" Inspired by: {self.specific_inspirations}."
        
        return context


@dataclass
class CampaignConfig:
    """
    Complete campaign configuration from user input form.
    """
    # Basic Product Info
    product_name: str
    product_category: str
    target_audience: str
    main_benefit: str
    
    # Brand Identity
    brand_color: str  # Hex color code
    brand_tone: BrandTone
    
    # Platform & Distribution
    target_platform: TargetPlatform
    website_url: Optional[str] = None
    
    # Visual Direction (MOST IMPORTANT)
    scene_vibe: SceneVibeDescription = None
    
    # Product Analysis (from image analysis)
    product_type: Optional[str] = None
    product_description: Optional[str] = None
    product_colors: List[str] = field(default_factory=list)
    product_materials: List[str] = field(default_factory=list)
    
    def get_base_prompt_context(self) -> str:
        """Generate base prompt context for all scenes."""
        context = f"{self.product_name} - {self.product_type}. "
        context += f"Target audience: {self.target_audience}. "
        context += f"Main benefit: {self.main_benefit}. "
        context += f"Brand tone: {self.brand_tone.value}. "
        
        if self.scene_vibe:
            context += f"\n\nVisual direction: {self.scene_vibe.to_prompt_context()}"
        
        return context
    
    def get_brand_color_integration(self) -> str:
        """Get brand color integration instruction."""
        return f"Subtly integrate brand color {self.brand_color} in accent lights, background elements, or styling."


# Example mockup configurations for testing

MOCKUP_CONFIG_LUXURY = CampaignConfig(
    product_name="CleanBot Pro X1",
    product_category="Home Appliances - Robot Vacuum",
    target_audience="Tech-savvy homeowners aged 30-50, busy professionals",
    main_benefit="Effortless cleaning with smart navigation and self-emptying technology",
    brand_color="#FF5C85",
    brand_tone=BrandTone.LUXURY,
    target_platform=TargetPlatform.INSTAGRAM_REELS,
    website_url="https://cleanbot.example.com",
    scene_vibe=SceneVibeDescription(
        visual_style="Luxury premium aesthetic with sophisticated, high-end product presentation",
        lighting="Professional studio lighting with soft diffused highlights, clean and bright",
        environment="Modern minimalist home interior, professional studio setup, premium lifestyle setting",
        mood="Luxurious and premium, exclusive and sophisticated, aspirational quality",
        specific_inspirations="Apple product photography, premium tech advertising, luxury home magazines",
        avoid="Cluttered backgrounds, harsh shadows, overly busy compositions, cheap-looking props"
    ),
    product_type="Robot vacuum cleaner with docking station",
    product_description="Sleek, modern robot vacuum cleaner with tall docking station. Circular vacuum with low profile, rectangular docking station with smooth curved top and textured metallic panel.",
    product_colors=["Black", "Metallic gray"],
    product_materials=["Plastic", "Metal"]
)


MOCKUP_CONFIG_LIFESTYLE = CampaignConfig(
    product_name="CleanBot Home",
    product_category="Home Appliances - Robot Vacuum",
    target_audience="Young families, first-time homeowners aged 25-40",
    main_benefit="More time with family, less time cleaning",
    brand_color="#FFEBC0",
    brand_tone=BrandTone.CASUAL,
    target_platform=TargetPlatform.TIKTOK,
    website_url="https://cleanbot.example.com",
    scene_vibe=SceneVibeDescription(
        visual_style="Authentic real-world lifestyle moments, relatable and genuine, bright and inviting",
        lighting="Natural light through windows, golden hour warmth, bright and cheerful",
        environment="Real home environment, lived-in spaces, cozy family rooms, authentic settings",
        mood="Warm and relatable, joyful and authentic, real people in real moments",
        specific_inspirations="Lifestyle photography, real family moments, authentic home content",
        avoid="Overly staged scenes, fake smiles, sterile environments, corporate feeling"
    ),
    product_type="Robot vacuum cleaner with docking station",
    product_description="Sleek, modern robot vacuum cleaner with tall docking station. Circular vacuum with low profile, rectangular docking station with smooth curved top and textured metallic panel.",
    product_colors=["Black", "Metallic gray"],
    product_materials=["Plastic", "Metal"]
)


MOCKUP_CONFIG_ENERGETIC = CampaignConfig(
    product_name="CleanBot Active",
    product_category="Home Appliances - Robot Vacuum",
    target_audience="Active millennials, pet owners, busy urban professionals",
    main_benefit="Keep up with your active lifestyle - smart cleaning that works while you're out",
    brand_color="#00D4FF",
    brand_tone=BrandTone.ENERGETIC,
    target_platform=TargetPlatform.YOUTUBE_SHORTS,
    website_url="https://cleanbot.example.com",
    scene_vibe=SceneVibeDescription(
        visual_style="Dynamic and energetic, modern tech-forward, vibrant and colorful",
        lighting="Bright and punchy, high contrast, energetic lighting with colorful accents",
        environment="Modern urban apartment, active lifestyle settings, contemporary spaces",
        mood="Energetic and dynamic, fast-paced and exciting, youthful and vibrant",
        specific_inspirations="Tech product launches, energetic lifestyle ads, modern urban content",
        avoid="Dull colors, slow pacing, traditional home settings, boring compositions"
    ),
    product_type="Robot vacuum cleaner with docking station",
    product_description="Sleek, modern robot vacuum cleaner with tall docking station. Circular vacuum with low profile, rectangular docking station with smooth curved top and textured metallic panel.",
    product_colors=["Black", "Metallic gray"],
    product_materials=["Plastic", "Metal"]
)


def get_mockup_config(style: str = "luxury") -> CampaignConfig:
    """Get a mockup configuration for testing."""
    configs = {
        "luxury": MOCKUP_CONFIG_LUXURY,
        "lifestyle": MOCKUP_CONFIG_LIFESTYLE,
        "energetic": MOCKUP_CONFIG_ENERGETIC
    }
    return configs.get(style.lower(), MOCKUP_CONFIG_LUXURY)
