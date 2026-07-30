import React from 'react';

export const TopRightLogo = () => {
  return (
    <div className="absolute top-0 right-0 z-[1000] pointer-events-none flex justify-end items-start w-[260px] h-[100px]">
      {/* Wavy Background SVG */}
      <svg 
        viewBox="0 0 260 100" 
        preserveAspectRatio="none" 
        className="absolute top-0 right-0 w-full h-full z-0 drop-shadow-sm"
      >
        {/* Light teal shadow/border */}
        <path 
          d="M 260 0 L 260 100 C 160 100 80 60 0 0 Z" 
          fill="#C4E4E1" 
        />
        {/* Dark teal main shape */}
        <path 
          d="M 260 0 L 260 90 C 160 90 85 50 0 0 Z" 
          fill="#0F766E" 
        />
      </svg>

      {/* Logo Content */}
      <div className="relative z-10 flex items-center gap-2.5 pr-6 pt-5 pointer-events-auto">
        {/* Dotted Circle Icon */}
        <div className="relative w-[32px] h-[40px] flex flex-col items-center justify-center">
          <svg viewBox="0 0 40 50" className="w-full h-full fill-white">
            <circle cx="20" cy="5" r="4.5" />
            <circle cx="31" cy="11" r="3.5" />
            <circle cx="36" cy="22" r="3" />
            <circle cx="33" cy="33" r="2.5" />
            <circle cx="26" cy="41" r="2.5" />
            <circle cx="20" cy="46" r="2.5" />
            <circle cx="14" cy="41" r="2.5" />
            <circle cx="7" cy="33" r="2.5" />
            <circle cx="4" cy="22" r="3" />
            <circle cx="9" cy="11" r="3.5" />
          </svg>
        </div>

        {/* Text */}
        <div className="flex flex-col text-white font-bold leading-[1.1] tracking-wide text-[15px] mt-0.5">
          <span>MANGROVE</span>
          <span>LENS</span>
        </div>
      </div>
    </div>
  );
};
