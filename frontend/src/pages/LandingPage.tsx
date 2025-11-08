import { useNavigate } from 'react-router-dom';
import logo from '../assets/logo.png';

const LandingPage = () => {
  const navigate = useNavigate();

  const handleCreateVideo = () => {
    navigate('/onboarding');
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section with Video Background */}
      <section className="relative min-h-[700px] flex items-center justify-center overflow-hidden">
        {/* Video Background */}
        <div className="absolute inset-0 z-0">
          <video
            autoPlay
            loop
            muted
            playsInline
            className="w-full h-full object-cover"
            onError={(e) => {
              const target = e.target as HTMLVideoElement;
              target.style.display = 'none';
            }}
          >
            <source src="/images/landing-page-video.mp4" type="video/mp4" />
          </video>
          {/* Fallback gradient background */}
          <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900"></div>
        </div>
        
        {/* Dark overlay for better text readability */}
        <div className="absolute inset-0 bg-black/60 z-10"></div>
        
        {/* Gradient overlay with brand colors */}
        <div className="absolute inset-0 bg-gradient-to-r from-brand-blue/20 to-brand-green/20 z-10"></div>
        
        {/* Content - Centered */}
        <div className="container mx-auto px-6 py-20 relative z-20">
          <div className="max-w-4xl mx-auto text-center text-white">
            {/* Logo */}
            <div className="flex items-center justify-center gap-4 mb-8">
              <img 
                src={logo} 
                alt="ProductFlow Logo" 
                className="h-20 w-20 object-contain"
              />
              <span className="text-3xl font-bold">ProductFlow</span>
            </div>
            
            {/* Main Heading */}
            <h1 className="text-5xl md:text-7xl font-bold leading-tight mb-6">
              Turn product images into{' '}
              <span className="bg-gradient-to-r from-brand-blue to-brand-green bg-clip-text text-transparent">
                ad videos
              </span>{' '}
              effortlessly
            </h1>
            
            {/* Tagline */}
            <p className="text-2xl md:text-3xl text-gray-200 mb-12 leading-relaxed font-light">
              There are endless products online, but few that truly shine.
            </p>
            
            {/* CTA Button */}
            <button
              onClick={handleCreateVideo}
              className="bg-brand-blue hover:bg-blue-600 text-white font-bold text-xl px-12 py-5 rounded-full shadow-2xl hover:shadow-brand-blue/50 transform hover:scale-105 transition-all duration-300 inline-flex items-center gap-3"
            >
              Create Your Video
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </button>
            
            {/* Feature badges */}
            <div className="flex items-center justify-center gap-6 mt-12">
              <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-6 py-3 rounded-full">
                <svg className="w-5 h-5 text-brand-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="font-semibold">30 sec videos</span>
              </div>
              <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-6 py-3 rounded-full">
                <svg className="w-5 h-5 text-brand-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span className="font-semibold">AI-Powered</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Solution Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-6">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
                How It Works
              </h2>
              <p className="text-xl text-gray-600">
                Transform your product into a professional ad in minutes
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {/* Main Point 1 */}
              <div className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all hover:-translate-y-1 duration-300">
                <div className="w-16 h-16 bg-gradient-to-br from-brand-blue to-blue-600 rounded-2xl flex items-center justify-center mb-6 mx-auto">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-3 text-center">
                  Intelligent Product Analysis
                </h3>
                <p className="text-gray-600 leading-relaxed text-center">
                  AI understands your product's features, context, and audience.
                </p>
              </div>

              {/* Main Point 2 */}
              <div className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all hover:-translate-y-1 duration-300">
                <div className="w-16 h-16 bg-gradient-to-br from-brand-green to-green-600 rounded-2xl flex items-center justify-center mb-6 mx-auto">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-3 text-center">
                  Automated Scene Generation
                </h3>
                <p className="text-gray-600 leading-relaxed text-center">
                  Creates realistic use-case visuals and ad-ready scenes in seconds.
                </p>
              </div>

              {/* Main Point 3 */}
              <div className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all hover:-translate-y-1 duration-300">
                <div className="w-16 h-16 bg-gradient-to-br from-brand-blue to-brand-green rounded-2xl flex items-center justify-center mb-6 mx-auto">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-3 text-center">
                  Instant Video Production
                </h3>
                <p className="text-gray-600 leading-relaxed text-center">
                  Stitches everything into a polished 30-second ad, ready to share.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Process Section - Improved */}
      <section className="py-24 bg-white relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute top-0 right-0 w-1/3 h-full bg-gradient-to-l from-brand-blue/5 to-transparent"></div>
        
        <div className="container mx-auto px-6 relative z-10">
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-20">
              <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
                Simple 4-Step Process
              </h2>
              <p className="text-xl text-gray-600">
                From product image to professional ad in minutes
              </p>
            </div>

            <div className="relative">
              {/* Connecting line */}
              <div className="hidden md:block absolute left-[29px] top-16 bottom-16 w-0.5 bg-gradient-to-b from-brand-blue via-brand-green to-brand-blue"></div>
              
              <div className="space-y-12">
                {/* Step 1 */}
                <div className="relative flex gap-8 items-start group">
                  <div className="flex-shrink-0 w-[60px] h-[60px] bg-gradient-to-br from-brand-blue to-blue-600 text-white rounded-2xl flex items-center justify-center font-bold text-2xl shadow-lg group-hover:scale-110 transition-transform duration-300 relative z-10">
                    1
                  </div>
                  <div className="flex-1 bg-white p-8 rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-brand-blue/20">
                    <h3 className="text-2xl font-bold text-gray-900 mb-3">
                      Upload Product Image
                    </h3>
                    <p className="text-gray-600 text-lg leading-relaxed">
                      Users start by uploading a single product image through the web interface. Our system accepts all common image formats and optimizes them automatically.
                    </p>
                  </div>
                </div>

                {/* Step 2 */}
                <div className="relative flex gap-8 items-start group">
                  <div className="flex-shrink-0 w-[60px] h-[60px] bg-gradient-to-br from-brand-green to-green-600 text-white rounded-2xl flex items-center justify-center font-bold text-2xl shadow-lg group-hover:scale-110 transition-transform duration-300 relative z-10">
                    2
                  </div>
                  <div className="flex-1 bg-white p-8 rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-brand-green/20">
                    <h3 className="text-2xl font-bold text-gray-900 mb-3">
                      AI Product Analysis
                    </h3>
                    <p className="text-gray-600 text-lg leading-relaxed">
                      The system analyzes visuals and extracts key marketing attributes automatically. Our AI identifies product features, target audience, and optimal messaging angles.
                    </p>
                  </div>
                </div>

                {/* Step 3 */}
                <div className="relative flex gap-8 items-start group">
                  <div className="flex-shrink-0 w-[60px] h-[60px] bg-gradient-to-br from-brand-blue to-blue-600 text-white rounded-2xl flex items-center justify-center font-bold text-2xl shadow-lg group-hover:scale-110 transition-transform duration-300 relative z-10">
                    3
                  </div>
                  <div className="flex-1 bg-white p-8 rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-brand-blue/20">
                    <h3 className="text-2xl font-bold text-gray-900 mb-3">
                      Generate Visual Scenes
                    </h3>
                    <p className="text-gray-600 text-lg leading-relaxed">
                      AI creates use-case images and dynamic scenes tailored to the product. Each scene is designed to showcase your product in real-world contexts that resonate with your audience.
                    </p>
                  </div>
                </div>

                {/* Step 4 */}
                <div className="relative flex gap-8 items-start group">
                  <div className="flex-shrink-0 w-[60px] h-[60px] bg-gradient-to-br from-brand-green to-green-600 text-white rounded-2xl flex items-center justify-center font-bold text-2xl shadow-lg group-hover:scale-110 transition-transform duration-300 relative z-10">
                    4
                  </div>
                  <div className="flex-1 bg-white p-8 rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-brand-green/20">
                    <h3 className="text-2xl font-bold text-gray-900 mb-3">
                      Produce Final Video
                    </h3>
                    <p className="text-gray-600 text-lg leading-relaxed">
                      All scenes are stitched into a polished 30-second ad ready for download. The final video includes professional transitions, music, and optimized formatting for all social platforms.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-brand-blue to-brand-green text-white">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-4xl lg:text-5xl font-bold mb-6">
            Ready to Create Your First Video?
          </h2>
          <p className="text-xl mb-10 max-w-2xl mx-auto opacity-90">
            Join thousands of marketers creating professional product videos with AI
          </p>
          <button
            onClick={handleCreateVideo}
            className="bg-white text-brand-blue hover:bg-gray-100 font-bold text-lg px-10 py-4 rounded-full shadow-2xl transform hover:scale-105 transition-all duration-300 inline-flex items-center gap-3"
          >
            Get Started Now
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-8">
        <div className="container mx-auto px-6 text-center">
          <p className="text-sm">
            © 2025 ProductFlow. AI-powered product video generation.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
