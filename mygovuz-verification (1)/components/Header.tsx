import React, { useState, useRef, useEffect } from 'react';
import { Menu, X, ChevronDown } from 'lucide-react';
import { useLanguage } from '../LanguageContext';
import { Language } from '../translations';
import RU from 'country-flag-icons/react/3x2/RU';
import GB from 'country-flag-icons/react/3x2/GB';
import UZ from 'country-flag-icons/react/3x2/UZ';

const languageOptions: Array<{ code: Language; label: string; flag: React.ComponentType<{ className?: string }> }> = [
  { code: 'ru', label: 'RU', flag: RU },
  { code: 'en', label: 'EN', flag: GB },
  { code: 'uz', label: 'UZ', flag: UZ },
];

export const Header: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLangMenuOpen, setIsLangMenuOpen] = useState(false);
  const { language, setLanguage, t } = useLanguage();
  const langMenuRef = useRef<HTMLDivElement>(null);
  
  const currentLanguage = languageOptions.find(lang => lang.code === language) || languageOptions[0];
  const FlagIcon = currentLanguage.flag;

  // Close language dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (langMenuRef.current && !langMenuRef.current.contains(event.target as Node)) {
        setIsLangMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <header className="border-b border-gray-200 bg-white sticky top-0 z-50">
      <div className="container mx-auto px-[15px] h-[72px] flex items-center justify-between">
        {/* Logo Section */}
        <div className="flex items-center">
            <a href="#" className="block">
                {/* Desktop Logo */}
                <img 
                    src="https://repository.gov.uz/img/new/logotype.svg" 
                    alt="my.gov.uz" 
                    className="hidden md:block h-10 w-auto"
                />
                {/* Mobile Logo */}
                <img 
                    src="https://repository.gov.uz/img/logo_mobile.png" 
                    alt="my.gov.uz" 
                    className="md:hidden h-10 w-auto"
                />
            </a>
        </div>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-8 text-[#0060B9] font-medium">
          <a href="#" className="hover:text-blue-700 transition-colors text-[15px]">{t.header.home}</a>
          
          {/* Language Selector Desktop */}
          <div className="relative" ref={langMenuRef}>
            <button
              type="button"
              onClick={() => setIsLangMenuOpen(!isLangMenuOpen)}
              className={`flex items-center gap-1.5 bg-[#F0F7FF] px-2.5 py-1 rounded hover:bg-blue-100 transition-all duration-200 select-none ${
                isLangMenuOpen ? 'bg-blue-100' : ''
              }`}
            >
              <FlagIcon className="w-4 h-3 rounded-sm flex-shrink-0" />
              <span className="font-semibold text-sm text-[#0060B9]">{currentLanguage.label}</span>
              <ChevronDown 
                size={12} 
                strokeWidth={2.5} 
                className={`text-[#0060B9] transition-transform duration-200 ${isLangMenuOpen ? 'rotate-180' : ''}`}
              />
            </button>
            
            {isLangMenuOpen && (
              <div 
                className="absolute top-full right-0 mt-1.5 bg-white border border-gray-200 shadow-lg rounded-md py-1 min-w-[90px] z-50 overflow-hidden"
                style={{
                  animation: 'fadeInDown 0.15s ease-out forwards',
                }}
              >
                {languageOptions.map((lang) => {
                  const LangFlag = lang.flag;
                  const isActive = language === lang.code;
                  return (
                    <button 
                      key={lang.code}
                      type="button"
                      onClick={() => { setLanguage(lang.code); setIsLangMenuOpen(false); }} 
                      className={`flex items-center gap-2 w-full text-left px-3 py-1.5 text-xs transition-all duration-150 ${
                        isActive 
                          ? 'font-semibold text-[#0060B9] bg-[#F0F7FF]' 
                          : 'text-gray-700 hover:bg-gray-50 hover:text-[#0060B9]'
                      }`}
                    >
                      <LangFlag className={`w-4 h-3 rounded-sm flex-shrink-0 ${isActive ? 'opacity-100' : 'opacity-75'}`} />
                      <span>{lang.label}</span>
                      {isActive && (
                        <span className="ml-auto text-[#0060B9] text-xs">✓</span>
                      )}
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          <a href="#" className="flex items-center gap-1 hover:text-blue-700 transition-colors text-[15px] font-semibold">
            <span>{t.header.login}</span>
          </a>
        </div>

        {/* Mobile Language Selector and Menu Button */}
        <div className="md:hidden flex items-center gap-2">
          {/* Language Selector Mobile */}
          <div className="relative" ref={langMenuRef}>
            <button
              type="button"
              onClick={() => setIsLangMenuOpen(!isLangMenuOpen)}
              className={`flex items-center gap-1 bg-[#F0F7FF] px-2 py-1 rounded hover:bg-blue-100 transition-all duration-200 select-none ${
                isLangMenuOpen ? 'bg-blue-100' : ''
              }`}
            >
              <FlagIcon className="w-4 h-3 rounded-sm flex-shrink-0" />
              <span className="font-semibold text-xs text-[#0060B9]">{currentLanguage.label}</span>
              <ChevronDown 
                size={10} 
                strokeWidth={2.5} 
                className={`text-[#0060B9] transition-transform duration-200 ${isLangMenuOpen ? 'rotate-180' : ''}`}
              />
            </button>
            
            {isLangMenuOpen && (
              <div 
                className="absolute top-full right-0 mt-1.5 bg-white border border-gray-200 shadow-lg rounded-md py-1 min-w-[80px] z-50 overflow-hidden"
                style={{
                  animation: 'fadeInDown 0.15s ease-out forwards',
                }}
              >
                {languageOptions.map((lang) => {
                  const LangFlag = lang.flag;
                  const isActive = language === lang.code;
                  return (
                    <button 
                      key={lang.code}
                      type="button"
                      onClick={() => { setLanguage(lang.code); setIsLangMenuOpen(false); }} 
                      className={`flex items-center gap-1.5 w-full text-left px-2.5 py-1.5 text-xs transition-all duration-150 ${
                        isActive 
                          ? 'font-semibold text-[#0060B9] bg-[#F0F7FF]' 
                          : 'text-gray-700 hover:bg-gray-50 hover:text-[#0060B9]'
                      }`}
                    >
                      <LangFlag className={`w-3.5 h-2.5 rounded-sm flex-shrink-0 ${isActive ? 'opacity-100' : 'opacity-75'}`} />
                      <span>{lang.label}</span>
                      {isActive && (
                        <span className="ml-auto text-[#0060B9] text-xs">✓</span>
                      )}
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button 
            className={`p-2 rounded-[5px] transition-colors flex items-center justify-center h-10 w-10 ${
              isMenuOpen 
                ? 'bg-[#0088CC] text-white' 
                : 'bg-transparent text-[#0088CC]'
            }`}
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X size={24} strokeWidth={2.5} /> : <Menu size={24} strokeWidth={2.5} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {isMenuOpen && (
        <div className="md:hidden bg-white border-t border-gray-300 shadow-lg absolute w-full left-0 top-[72px] z-50">
          <div className="another_wrap">
            <nav className="flex items-center justify-center gap-4 py-0 px-[15px]">
              <a href="#" className="text-[#0060B9] font-medium text-[15px]">{t.header.home}</a>
              <a href="#" className="text-[#0060B9] font-medium text-[15px]">
                {t.header.login}
              </a>
            </nav>
          </div>
        </div>
      )}
    </header>
  );
};