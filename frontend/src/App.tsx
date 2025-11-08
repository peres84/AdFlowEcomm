import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';

function App() {
  useEffect(() => {
    // Initialize session ID if not exists
    if (!localStorage.getItem('sessionId')) {
      localStorage.setItem('sessionId', uuidv4());
    }
  }, []);

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<div className="p-8 text-center">
            <h1 className="text-4xl font-bold text-brand-blue">ProductFlow</h1>
            <p className="mt-4 text-gray-600">AI-powered product video generator</p>
          </div>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
