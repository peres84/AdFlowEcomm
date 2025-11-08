import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { getSessionId, setSessionId, hasSessionId } from './utils/session';
import LandingPage from './pages/LandingPage';

// Placeholder components for routes (to be implemented in future tasks)

const OnboardingForm = () => (
  <div className="p-8 text-center">
    <h2 className="text-2xl font-bold text-brand-blue">Onboarding Form</h2>
    <p className="mt-2 text-sm text-gray-500">To be implemented</p>
  </div>
);

const UploadPage = () => (
  <div className="p-8 text-center">
    <h2 className="text-2xl font-bold text-brand-blue">Upload Page</h2>
    <p className="mt-2 text-sm text-gray-500">To be implemented</p>
  </div>
);

const ImageGallery = () => (
  <div className="p-8 text-center">
    <h2 className="text-2xl font-bold text-brand-blue">Image Gallery</h2>
    <p className="mt-2 text-sm text-gray-500">To be implemented</p>
  </div>
);

const SceneDescriptionReview = () => (
  <div className="p-8 text-center">
    <h2 className="text-2xl font-bold text-brand-blue">Scene Description Review</h2>
    <p className="mt-2 text-sm text-gray-500">To be implemented</p>
  </div>
);

const VideoSceneReview = () => (
  <div className="p-8 text-center">
    <h2 className="text-2xl font-bold text-brand-blue">Video Scene Review</h2>
    <p className="mt-2 text-sm text-gray-500">To be implemented</p>
  </div>
);

const FinalVideoPreview = () => (
  <div className="p-8 text-center">
    <h2 className="text-2xl font-bold text-brand-blue">Final Video Preview</h2>
    <p className="mt-2 text-sm text-gray-500">To be implemented</p>
  </div>
);

function App() {
  useEffect(() => {
    // Initialize session ID if not exists
    if (!hasSessionId()) {
      const sessionId = uuidv4();
      setSessionId(sessionId);
      console.log('Session ID initialized:', sessionId);
    } else {
      console.log('Existing session ID:', getSessionId());
    }
  }, []);

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/onboarding" element={<OnboardingForm />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/images" element={<ImageGallery />} />
          <Route path="/scenes" element={<SceneDescriptionReview />} />
          <Route path="/videos" element={<VideoSceneReview />} />
          <Route path="/final" element={<FinalVideoPreview />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
