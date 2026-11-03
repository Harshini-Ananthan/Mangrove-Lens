import React from 'react';
import { AreaChart, Area, Tooltip, ResponsiveContainer } from 'recharts';

export const TrendChart = ({ data = [] }) => {
  return (
    <div className="bg-white p-4 rounded-[20px] shadow-sm border border-gray-100 flex flex-col gap-2">
      <div className="flex justify-between items-end">
        <div>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">NDVI Trend</h3>
          <p className="text-[10px] text-gray-400">Historical Health Index</p>
        </div>
        <span className="text-xs font-bold text-accent">+0.01 (Since 2020)</span>
      </div>
      <div className="h-24 w-full mt-2">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorNdvi" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#22C55E" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#22C55E" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <Tooltip 
              contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              labelStyle={{ fontSize: '12px', fontWeight: 'bold', color: '#6b7280' }}
              itemStyle={{ fontSize: '12px', color: '#0F766E' }}
            />
            <Area type="monotone" dataKey="ndvi" stroke="#22C55E" strokeWidth={2} fillOpacity={1} fill="url(#colorNdvi)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
