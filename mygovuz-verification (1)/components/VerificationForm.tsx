import React, { useState } from 'react';
import { AlertBox } from './AlertBox';
import { useLanguage } from '../LanguageContext';

export const VerificationForm: React.FC = () => {
  const [pin, setPin] = useState('');
  const { t } = useLanguage();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Verifying PIN:', pin);
    // Add verification logic here
  };

  return (
    <div className="container mx-auto px-[15px] py-8 md:py-16 relative overflow-x-hidden md:overflow-visible max-w-7xl">
      <div className="flex flex-col lg:flex-row gap-16 xl:gap-32 items-start justify-between relative z-10">
        
        {/* Left Column: Form - Boxed on Desktop */}
        <div className="w-full lg:w-[500px] flex-shrink-0 lg:border lg:border-[#E0E0E0] lg:rounded-xl lg:p-10 lg:shadow-[0_10px_40px_rgba(0,0,0,0.03)] bg-white">
          <AlertBox />
          
          <div className="mb-0">
            <h1 className="text-[14px] md:text-[22px]  text-black mb-8 leading-tight">
              {t.form.title}
            </h1>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <label htmlFor="pin" className="block text-[15px] font-bold text-gray-800">
                  {t.form.label}
                </label>
                <input
                  id="pin"
                  type="text"
                  value={pin}
                  onChange={(e) => setPin(e.target.value)}
                  className="w-full bg-white border border-gray-300 rounded-[4px] px-3 py-2 text-[#495057] text-base focus:outline-none focus:border-[#80bdff] focus:shadow-[0_0_0_0.2rem_rgba(0,123,255,.25)] transition-shadow"
                  placeholder=""
                />
              </div>

              <button
                type="submit"
                className="w-full bg-[#28a745] hover:bg-[#218838] text-white font-medium py-2.5 rounded-[4px] shadow-sm transition-colors duration-200 text-[16px]"
              >
                {t.form.button}
              </button>
            </form>

            <div className="mt-5 mb-[0px]">
              <h3 className="text-[#3877B0] text-[14px] font-normal leading-relaxed" style={{ fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif' }}>
                {t.form.helper}
              </h3>
            </div>
          </div>
        </div>

        {/* Right Column: Document Preview */}
        <div className="w-full flex-grow flex justify-center lg:justify-start lg:pl-10 relative">
          <div className="relative w-[166px] md:w-full max-w-[420px] mx-auto md:mx-auto lg:mx-0 mt-[10px] md:mt-0 mr-[81.7px] md:mr-auto lg:mr-0 shadow-[0_10px_30px_rgba(0,0,0,0.1)]">
             <img 
                src="https://repository.gov.uz/img/pin_code_document.jpg" 
                alt="Образец документа" 
                className="w-[166px] h-[222px] md:w-full md:h-auto block object-contain"
             />
          </div>
        </div>

      </div>
    </div>
  );
};