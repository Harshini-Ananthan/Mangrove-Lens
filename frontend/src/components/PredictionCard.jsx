import React from 'react';
import { motion } from 'framer-motion';

export const PredictionCard = ({ riskScore = 0 }) => {
  const percentage = Math.max(0, Math.min(100, Number(riskScore) || 0));
  const circumference = 2 * Math.PI * 24; // r=24
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="bg-gradient-to-br from-primary to-secondary p-5 rounded-[20px] text-white shadow-md relative overflow-hidden">
      {/* Decorative background circle */}
      <div className="absolute -right-8 -top-8 w-32 h-32 bg-white/10 rounded-full blur-2xl"></div>
      
      <div className="relative z-10 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold opacity-90 mb-1">Decision Risk</h3>
          <p className="text-xs opacity-75">Explainable rule score</p>
        </div>
        
        {/* Circular Progress */}
        <div className="relative w-16 h-16 flex items-center justify-center">
          <svg className="transform -rotate-90 w-16 h-16">
            {/* Background circle */}
            <circle
              cx="32"
              cy="32"
              r="24"
              stroke="rgba(255,255,255,0.2)"
              strokeWidth="4"
              fill="none"
            />
            {/* Progress circle */}
            <motion.circle
              cx="32"
              cy="32"
              r="24"
              stroke="white"
              strokeWidth="4"
              fill="none"
              strokeLinecap="round"
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset }}
              transition={{ duration: 1.5, ease: "easeOut" }}
            />
          </svg>
          <span className="absolute text-sm font-bold">{percentage.toFixed(0)}%</span>
        </div>
      </div>
    </div>
  );
};
