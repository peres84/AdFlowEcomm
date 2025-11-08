import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { formApi } from '../services/api';
import type { FormData, ApiError } from '../types';

// Dropdown options
const CATEGORIES = [
  'Electronics',
  'Fashion & Apparel',
  'Home & Garden',
  'Beauty & Personal Care',
  'Sports & Outdoors',
  'Food & Beverage',
  'Toys & Games',
  'Books & Media',
  'Health & Wellness',
  'Automotive',
  'Other',
];

const TARGET_AUDIENCES = [
  'Young Adults (18-24)',
  'Adults (25-34)',
  'Middle-aged (35-54)',
  'Seniors (55+)',
  'Parents',
  'Professionals',
  'Students',
  'Entrepreneurs',
  'General Consumers',
];

const BRAND_TONES = [
  'Professional',
  'Casual',
  'Playful',
  'Luxurious',
  'Minimalist',
  'Bold',
  'Friendly',
  'Sophisticated',
  'Energetic',
];

const TARGET_PLATFORMS = [
  'Instagram',
  'Facebook',
  'TikTok',
  'YouTube',
  'LinkedIn',
  'Twitter/X',
  'Multiple Platforms',
];

interface BrandColors {
  primary: string;
  accent: string;
  secondary: string;
}

const OnboardingForm = () => {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [brandColors, setBrandColors] = useState<BrandColors>({
    primary: '',
    accent: '',
    secondary: '',
  });

  const [formData, setFormData] = useState<FormData>({
    product_name: '',
    category: '',
    target_audience: '',
    main_benefit: '',
    brand_colors: [],
    brand_tone: '',
    target_platform: '',
    website_url: '',
    scene_description: '',
  });

  const [validationErrors, setValidationErrors] = useState<Partial<Record<keyof FormData, string>>>({});
  const [colorErrors, setColorErrors] = useState<Partial<Record<keyof BrandColors, string>>>({});

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear validation error for this field
    if (validationErrors[name as keyof FormData]) {
      setValidationErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const isValidHexColor = (color: string): boolean => {
    return /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/.test(color);
  };

  const handleColorChange = (colorType: keyof BrandColors, value: string) => {
    setBrandColors((prev) => ({ ...prev, [colorType]: value }));
    
    // Clear error for this color field
    if (colorErrors[colorType]) {
      setColorErrors((prev) => ({ ...prev, [colorType]: undefined }));
    }
    
    // Clear general brand_colors validation error
    if (validationErrors.brand_colors) {
      setValidationErrors((prev) => ({ ...prev, brand_colors: undefined }));
    }
  };

  const validateForm = (): boolean => {
    const errors: Partial<Record<keyof FormData, string>> = {};
    const colErrors: Partial<Record<keyof BrandColors, string>> = {};

    if (!formData.product_name.trim()) {
      errors.product_name = 'Product name is required';
    }

    if (!formData.category) {
      errors.category = 'Please select a category';
    }

    if (!formData.target_audience) {
      errors.target_audience = 'Please select a target audience';
    }

    if (!formData.main_benefit.trim()) {
      errors.main_benefit = 'Main benefit is required';
    }

    // Validate brand colors
    if (!brandColors.primary.trim()) {
      colErrors.primary = 'Primary color is required';
    } else if (!isValidHexColor(brandColors.primary)) {
      colErrors.primary = 'Invalid hex color (e.g., #FF5733)';
    }

    if (brandColors.accent.trim() && !isValidHexColor(brandColors.accent)) {
      colErrors.accent = 'Invalid hex color (e.g., #FF5733)';
    }

    if (brandColors.secondary.trim() && !isValidHexColor(brandColors.secondary)) {
      colErrors.secondary = 'Invalid hex color (e.g., #FF5733)';
    }

    // Build brand_colors array for submission
    const colors: string[] = [];
    if (brandColors.primary.trim()) colors.push(brandColors.primary);
    if (brandColors.accent.trim()) colors.push(brandColors.accent);
    if (brandColors.secondary.trim()) colors.push(brandColors.secondary);

    if (colors.length === 0) {
      errors.brand_colors = 'At least primary color is required';
    }

    if (!formData.brand_tone) {
      errors.brand_tone = 'Please select a brand tone';
    }

    if (!formData.target_platform) {
      errors.target_platform = 'Please select a target platform';
    }

    if (!formData.scene_description.trim()) {
      errors.scene_description = 'Scene description is required';
    }

    setValidationErrors(errors);
    setColorErrors(colErrors);
    return Object.keys(errors).length === 0 && Object.keys(colErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!validateForm()) {
      return;
    }

    // Build brand_colors array from individual color inputs
    const colors: string[] = [];
    if (brandColors.primary.trim()) colors.push(brandColors.primary);
    if (brandColors.accent.trim()) colors.push(brandColors.accent);
    if (brandColors.secondary.trim()) colors.push(brandColors.secondary);

    const submissionData = {
      ...formData,
      brand_colors: colors,
    };

    setIsSubmitting(true);

    try {
      await formApi.submit(submissionData);
      navigate('/upload');
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.message || 'Failed to submit form. Please try again.');
      console.error('Form submission error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-6">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-10">
            <h1 className="text-4xl font-bold text-gray-900 mb-3">
              Tell Us About Your Product
            </h1>
            <p className="text-lg text-gray-600">
              Help us create the perfect video by providing some details about your product
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span>{error}</span>
              </div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-lg p-8 space-y-6">
            {/* Product Name */}
            <div>
              <label htmlFor="product_name" className="block text-sm font-semibold text-gray-700 mb-2">
                Product Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="product_name"
                name="product_name"
                value={formData.product_name}
                onChange={handleInputChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-brand-blue focus:border-transparent transition-all ${
                  validationErrors.product_name ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="e.g., Wireless Bluetooth Headphones"
              />
              {validationErrors.product_name && (
                <p className="mt-1 text-sm text-red-500">{validationErrors.product_name}</p>
              )}
            </div>

            {/* Category */}
            <div>
              <label htmlFor="category" className="block text-sm font-semibold text-gray-700 mb-2">
                Product Category <span className="text-red-500">*</span>
              </label>
              <select
                id="category"
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-brand-blue focus:border-transparent transition-all ${
                  validationErrors.category ? 'border-red-500' : 'border-gray-300'
                }`}
              >
                <option value="">Select a category</option>
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
              {validationErrors.category && (
                <p className="mt-1 text-sm text-red-500">{validationErrors.category}</p>
              )}
            </div>

            {/* Target Audience */}
            <div>
              <label htmlFor="target_audience" className="block text-sm font-semibold text-gray-700 mb-2">
                Target Audience <span className="text-red-500">*</span>
              </label>
              <select
                id="target_audience"
                name="target_audience"
                value={formData.target_audience}
                onChange={handleInputChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-brand-blue focus:border-transparent transition-all ${
                  validationErrors.target_audience ? 'border-red-500' : 'border-gray-300'
                }`}
              >
                <option value="">Select target audience</option>
                {TARGET_AUDIENCES.map((audience) => (
                  <option key={audience} value={audience}>
                    {audience}
                  </option>
                ))}
              </select>
              {validationErrors.target_audience && (
                <p className="mt-1 text-sm text-red-500">{validationErrors.target_audience}</p>
              )}
            </div>

            {/* Main Benefit */}
            <div>
              <label htmlFor="main_benefit" className="block text-sm font-semibold text-gray-700 mb-2">
                Main Benefit <span className="text-red-500">*</span>
              </label>
              <textarea
                id="main_benefit"
                name="main_benefit"
                value={formData.main_benefit}
                onChange={handleInputChange}
                rows={3}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-brand-blue focus:border-transparent transition-all ${
                  validationErrors.main_benefit ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="What's the key benefit your product provides? e.g., Crystal-clear sound with 30-hour battery life"
              />
              {validationErrors.main_benefit && (
                <p className="mt-1 text-sm text-red-500">{validationErrors.main_benefit}</p>
              )}
            </div>

            {/* Brand Color Palette */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Brand Color Palette <span className="text-red-500">*</span>
              </label>
              <p className="text-sm text-gray-500 mb-4">Enter hex color codes for your brand colors</p>
              
              <div className="space-y-4">
                {/* Primary Color */}
                <div>
                  <label htmlFor="primary_color" className="block text-sm font-medium text-gray-700 mb-2">
                    Primary Color <span className="text-red-500">*</span>
                  </label>
                  <div className="flex gap-3 items-start">
                    <div className="flex-1">
                      <input
                        type="text"
                        id="primary_color"
                        value={brandColors.primary}
                        onChange={(e) => handleColorChange('primary', e.target.value)}
                        className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-brand-blue focus:border-transparent transition-all ${
                          colorErrors.primary ? 'border-red-500' : 'border-gray-300'
                        }`}
                        placeholder="#FF5733"
                      />
                      {colorErrors.primary && (
                        <p className="mt-1 text-sm text-red-500">{colorErrors.primary}</p>
                      )}
                    </div>
                    {brandColors.primary && isValidHexColor(brandColors.primary) && (
                      <div
                        className="w-16 h-12 rounded-lg border-2 border-gray-300 flex-shrink-0"
                        style={{ backgroundColor: brandColors.primary }}
                      />
                    )}
                  </div>
                </div>

                {/* Accent Color */}
                <div>
                  <label htmlFor="accent_color" className="block text-sm font-medium text-gray-700 mb-2">
                    Accent Color <span className="text-gray-400">(Optional)</span>
                  </label>
                  <div className="flex gap-3 items-start">
                    <div className="flex-1">
                      <input
                        type="text"
                        id="accent_color"
                        value={brandColors.accent}
                        onChange={(e) => handleColorChange('accent', e.target.value)}
                        className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-brand-blue focus:border-transparent transition-all ${
                          colorErrors.accent ? 'border-red-500' : 'border-gray-300'
                        }`}
                        placeholder="#33C3FF"
                      />
                      {colorErrors.accent && (
                        <p className="mt-1 text-sm text-red-500">{colorErrors.accent}</p>
                      )}
                    </div>
                    {brandColors.accent && isValidHexColor(brandColors.accent) && (
                      <div
                        className="w-16 h-12 rounded-lg border-2 border-gray-300 flex-shrink-0"
                        style={{ backgroundColor: brandColors.accent }}
                      />
                    )}
                  </div>
                </div>

                {/* Secondary Color */}
                <div>
                  <label htmlFor="secondary_color" className="block text-sm font-medium text-gray-700 mb-2">
                    Secondary Color <span className="text-gray-400">(Optional)</span>
                  </label>
                  <div className="flex gap-3 items-start">
                    <div className="flex-1">
                      <input
                        type="text"
                        id="secondary_color"
                        value={brandColors.secondary}
                        onChange={(e) => handleColorChange('secondary', e.target.value)}
                        className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-brand-blue focus:border-transparent transition-all ${
                          colorErrors.secondary ? 'border-red-500' : 'border-gray-300'
                        }`}
                        placeholder="#FFC300"
                      />
                      {colorErrors.secondary && (
                        <p className="mt-1 text-sm text-red-500">{colorErrors.secondary}</p>
                      )}
                    </div>
                    {brandColors.secondary && isValidHexColor(brandColors.secondary) && (
                      <div
                        className="w-16 h-12 rounded-lg border-2 border-gray-300 flex-shrink-0"
                        style={{ backgroundColor: brandColors.secondary }}
                      />
                    )}
                  </div>
                </div>
              </div>
              
              {validationErrors.brand_colors && (
                <p className="mt-2 text-sm text-red-500">{validationErrors.brand_colors}</p>
              )}
            </div>

            {/* Brand Tone */}
            <div>
              <label htmlFor="brand_tone" className="block text-sm font-semibold text-gray-700 mb-2">
                Brand Tone <span className="text-red-500">*</span>
              </label>
              <select
                id="brand_tone"
                name="brand_tone"
                value={formData.brand_tone}
                onChange={handleInputChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-brand-blue focus:border-transparent transition-all ${
                  validationErrors.brand_tone ? 'border-red-500' : 'border-gray-300'
                }`}
              >
                <option value="">Select brand tone</option>
                {BRAND_TONES.map((tone) => (
                  <option key={tone} value={tone}>
                    {tone}
                  </option>
                ))}
              </select>
              {validationErrors.brand_tone && (
                <p className="mt-1 text-sm text-red-500">{validationErrors.brand_tone}</p>
              )}
            </div>

            {/* Target Platform */}
            <div>
              <label htmlFor="target_platform" className="block text-sm font-semibold text-gray-700 mb-2">
                Target Platform <span className="text-red-500">*</span>
              </label>
              <select
                id="target_platform"
                name="target_platform"
                value={formData.target_platform}
                onChange={handleInputChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-brand-blue focus:border-transparent transition-all ${
                  validationErrors.target_platform ? 'border-red-500' : 'border-gray-300'
                }`}
              >
                <option value="">Select target platform</option>
                {TARGET_PLATFORMS.map((platform) => (
                  <option key={platform} value={platform}>
                    {platform}
                  </option>
                ))}
              </select>
              {validationErrors.target_platform && (
                <p className="mt-1 text-sm text-red-500">{validationErrors.target_platform}</p>
              )}
            </div>

            {/* Website URL */}
            <div>
              <label htmlFor="website_url" className="block text-sm font-semibold text-gray-700 mb-2">
                Website URL <span className="text-gray-400">(Optional)</span>
              </label>
              <input
                type="url"
                id="website_url"
                name="website_url"
                value={formData.website_url}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-blue focus:border-transparent transition-all"
                placeholder="https://www.yourwebsite.com"
              />
            </div>

            {/* Scene Description */}
            <div>
              <label htmlFor="scene_description" className="block text-sm font-semibold text-gray-700 mb-2">
                Scene Description <span className="text-red-500">*</span>
              </label>
              <p className="text-sm text-gray-500 mb-3">
                Describe the visual style, atmosphere, and aesthetic you want for your video
              </p>
              <textarea
                id="scene_description"
                name="scene_description"
                value={formData.scene_description}
                onChange={handleInputChange}
                rows={5}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-brand-blue focus:border-transparent transition-all ${
                  validationErrors.scene_description ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Examples:&#10;• Modern minimalist studio with soft natural lighting and clean white background&#10;• Vibrant outdoor setting with bright sunlight and energetic atmosphere&#10;• Cozy home environment with warm lighting and comfortable ambiance&#10;• Professional office space with sleek design and contemporary feel"
              />
              {validationErrors.scene_description && (
                <p className="mt-1 text-sm text-red-500">{validationErrors.scene_description}</p>
              )}
            </div>

            {/* Submit Button */}
            <div className="flex gap-4 pt-6">
              <button
                type="button"
                onClick={() => navigate('/')}
                className="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition-all"
              >
                Back
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex-1 px-6 py-3 bg-brand-blue text-white font-semibold rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
              >
                {isSubmitting ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Submitting...
                  </span>
                ) : (
                  'Continue to Upload'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default OnboardingForm;
