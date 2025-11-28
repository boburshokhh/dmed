import React from 'react';
import { Header } from './components/Header';
import { VerificationForm } from './components/VerificationForm';
import { LanguageProvider } from './LanguageContext';
import { CubesDecoration } from './components/CubesDecoration';

const App: React.FC = () => {
  return (
    <LanguageProvider>
      <div className="min-h-screen flex flex-col bg-white relative  px-[11px] pb-[20px]">
        <Header />
        <main className="flex-grow">
          <VerificationForm />
        </main>
        
        <footer className="hidden md:block py-6 mt-auto relative z-10">
          <div className="container mx-auto px-4 md:px-8">
             <p className="text-[#999999] text-[13px]">© UZINFOCOM 2025</p>
          </div>
        </footer>

        {/* Decorative Cubes */}
        <CubesDecoration />
      </div>
    </LanguageProvider>
  );
};

export default App;