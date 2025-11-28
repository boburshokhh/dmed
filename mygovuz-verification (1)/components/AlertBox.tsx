import React, { useState } from 'react';
import { X } from 'lucide-react';
import { useLanguage } from '../LanguageContext';

export const AlertBox: React.FC = () => {
  const [isVisible, setIsVisible] = useState(true);
  const { t } = useLanguage();

  if (!isVisible) return null;

  return (
    <div className="bg-[#FCF8E3] border border-[#FFE58F] rounded-md p-[11px] mb-5 relative shadow-sm">
      <div className="pr-6 text-[14px] text-[#8A6D3B] leading-6 font-normal" style={{ fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif' }}>
        {t.alert.text} <a href="#" className="text-[#1890ff] hover:text-[#40a9ff] hover:underline transition-colors">{t.alert.link}</a>
      </div>
      <button 
        onClick={() => setIsVisible(false)}
        className="absolute top-3 right-3 text-gray-400 hover:text-gray-600 transition-colors"
      >
        <X size={18} />
      </button>
    </div>
  );
};