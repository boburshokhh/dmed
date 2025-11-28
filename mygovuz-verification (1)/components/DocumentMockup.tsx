import React from 'react';

export const DocumentMockup: React.FC = () => {
  return (
    <div className="relative w-full max-w-[420px] mx-auto bg-white shadow-[0_10px_30px_rgba(0,0,0,0.1)] border border-gray-100 p-8 md:p-10 aspect-[0.7] transform hover:scale-[1.02] transition-transform duration-500">
      
      {/* Header Area */}
      <div className="flex justify-between items-start mb-8 relative z-10">
        <div className="flex flex-col gap-2">
             {/* Small Logo Replica */}
            <div className="flex items-center gap-1.5 mb-1 opacity-90">
                <div className="w-6 h-6 bg-[#0060B9] rounded flex items-center justify-center">
                     <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="20 6 9 17 4 12"></polyline>
                     </svg>
                </div>
                <span className="text-[#0060B9] text-[10px] font-bold">my.gov.uz</span>
            </div>
            <div className="text-[7px] text-[#0060B9] leading-tight font-medium">
                Единый Портал Интерактивных<br/>Государственных Услуг
            </div>
        </div>
        
        {/* Emblem Replica (Uzbekistan Coat of Arms style) */}
        <div className="absolute left-1/2 transform -translate-x-1/2 top-0">
             <div className="w-16 h-16 rounded-full bg-gradient-to-br from-[#1ea54d] to-[#128139] p-0.5 shadow-md flex items-center justify-center">
                 <div className="w-full h-full rounded-full border-[1.5px] border-yellow-400 bg-white flex items-center justify-center overflow-hidden relative">
                    {/* Abstract representation of bird/sun */}
                    <div className="absolute bottom-0 w-16 h-8 bg-blue-100 rounded-t-full opacity-50"></div>
                    <div className="w-8 h-8 rounded-full bg-yellow-100 border border-yellow-300"></div>
                    <div className="absolute top-1 w-10 h-6 border-b-2 border-green-600 rounded-full"></div>
                 </div>
             </div>
        </div>

        {/* Top Right Lines */}
        <div className="flex flex-col gap-1.5 items-end mt-1">
            <div className="w-24 h-2.5 bg-gray-200 rounded-sm"></div>
            <div className="w-16 h-2.5 bg-gray-200 rounded-sm"></div>
        </div>
      </div>

      {/* Main Title Block */}
      <div className="w-3/4 mx-auto h-5 bg-gray-300 mb-10 rounded-sm mt-4"></div>

      {/* Text Lines */}
      <div className="space-y-3 mb-16">
        {[...Array(7)].map((_, i) => (
          <div key={i} className="w-full h-2.5 bg-gray-200 rounded-sm"></div>
        ))}
        <div className="w-2/3 h-2.5 bg-gray-200 rounded-sm"></div>
      </div>

      {/* Footer / QR Area */}
      <div className="absolute bottom-10 right-10 flex flex-col items-center">
        
        {/* The Arrow */}
        <div className="absolute -top-12 -left-12 text-[#FF0000] z-20">
             <svg width="48" height="48" viewBox="0 0 54 54" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="transform rotate-12">
                <path d="M4 4 L30 30" />
                <path d="M30 4 L30 30 L4 30" />
            </svg>
        </div>

        <div className="flex gap-2 items-end">
             {/* Red Box with Vertical Text */}
             <div className="border-[2.5px] border-[#FF0000] bg-white px-1 py-1.5 h-[84px] flex flex-col items-center justify-center shadow-sm z-10">
                 <div className="transform -rotate-90 origin-center whitespace-nowrap text-xs font-bold text-gray-800 tracking-widest leading-none">
                     XYZA
                 </div>
             </div>

            {/* QR Code Placeholder */}
            <div className="w-[84px] h-[84px] bg-gray-900 p-1 flex flex-wrap content-center justify-center gap-0.5">
                {[...Array(81)].map((_, i) => (
                    <div key={i} className={`w-2 h-2 ${Math.random() > 0.4 ? 'bg-white' : 'bg-transparent'}`}></div>
                ))}
            </div>
        </div>
      </div>

      {/* Bottom Lines */}
       <div className="absolute bottom-10 left-10 w-1/3 space-y-2">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="w-full h-2 bg-gray-200 rounded-sm"></div>
        ))}
      </div>
    </div>
  );
};