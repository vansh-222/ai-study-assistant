import React from 'react';
import UploadPDF from '../components/UploadPDF';

const Home = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col items-center justify-center p-6">
      <div className="text-center mb-10">
        <h1 className="text-5xl font-extrabold text-indigo-700 mb-3">🎓 AI Study Assistant</h1>
        <p className="text-gray-600 text-lg max-w-xl mx-auto">
          Upload your study PDF and let AI generate predicted questions, flashcards, a study plan, and a mock test for you!
        </p>
      </div>
      <UploadPDF />
    </div>
  );
};

export default Home;