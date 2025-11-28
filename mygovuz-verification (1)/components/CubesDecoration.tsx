import React from 'react';

export const CubesDecoration: React.FC = () => {
  return (
    <div className="hidden 2xl:block absolute right-[-100px] top-[100px] z-0 pointer-events-none w-[500px] h-[500px]">
      <svg width="100%" height="100%" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" className="opacity-100">
        <defs>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="5" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
        </defs>

        {/* Group transformed to scale and position */}
        <g transform="translate(50, 50) scale(1.2)">
            
            {/* Back Right Cube (Light Blue) */}
            <g transform="translate(180, 20)">
                {/* Top */}
                <path d="M0 30 L50 0 L100 30 L50 60 Z" fill="#E0F2FE" stroke="#BAE6FD" />
                {/* Left */}
                <path d="M0 30 L50 60 L50 120 L0 90 Z" fill="#BAE6FD" stroke="#7DD3FC" />
                {/* Right */}
                <path d="M50 60 L100 30 L100 90 L50 120 Z" fill="#7DD3FC" stroke="#38BDF8" />
            </g>

            {/* Front Left Cube (Greenish) */}
             <g transform="translate(0, 100)">
                {/* Top */}
                <path d="M0 30 L50 0 L100 30 L50 60 Z" fill="#ECFDF5" stroke="#A7F3D0" />
                {/* Left */}
                <path d="M0 30 L50 60 L50 120 L0 90 Z" fill="#D1FAE5" stroke="#6EE7B7" />
                {/* Right */}
                <path d="M50 60 L100 30 L100 90 L50 120 Z" fill="#6EE7B7" stroke="#34D399" />
            </g>

             {/* Main Large Center Cube (Blue) */}
            <g transform="translate(80, 80)">
                {/* Top */}
                <path d="M0 60 L100 0 L200 60 L100 120 Z" fill="#EFF6FF" stroke="#DBEAFE" />
                {/* Left */}
                <path d="M0 60 L100 120 L100 240 L0 180 Z" fill="#DBEAFE" stroke="#BFDBFE" />
                {/* Right */}
                <path d="M100 120 L200 60 L200 180 L100 240 Z" fill="#BFDBFE" stroke="#93C5FD" />
                
                {/* Checkmark-ish Highlight on face */}
                <path d="M80 140 L100 160 L140 100" fill="none" stroke="white" strokeWidth="8" strokeLinecap="round" opacity="0.6" />
            </g>

        </g>
      </svg>
    </div>
  );
};