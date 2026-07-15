import React from 'react';
import { Sparkles, CheckCircle2, ArrowRight } from 'lucide-react';

export default function Paywall({ onUpgrade, isUpgrading }) {
  return (
    <div className="p-8 rounded-2xl bg-gradient-to-br from-indigo-900/40 to-purple-900/40 border border-indigo-500/30 backdrop-blur-md h-full flex flex-col relative overflow-hidden">
      {/* Glowing background effects */}
      <div className="absolute -top-10 -right-10 w-40 h-40 bg-purple-500/20 blur-3xl rounded-full pointer-events-none"></div>
      <div className="absolute -bottom-10 -left-10 w-40 h-40 bg-indigo-500/20 blur-3xl rounded-full pointer-events-none"></div>

      <div className="flex items-center justify-between mb-6 relative z-10">
        <h3 className="text-2xl font-bold text-white flex items-center gap-2">
          <Sparkles className="text-yellow-400" /> Premium Quality
        </h3>
        <span className="px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 font-semibold text-sm border border-indigo-500/30">
          $2.00
        </span>
      </div>
      
      <p className="text-gray-300 mb-6 flex-grow relative z-10 text-sm leading-relaxed">
        You're currently viewing the Free Tier (Low-Poly). Upgrade now to unlock our High-Fidelity processing pipeline.
      </p>
      
      <ul className="space-y-3 mb-8 relative z-10">
        {[
          "4K PBR Textures (Albedo, Normal, Roughness)",
          "Clean AI Retopology (Quad Mesh)",
          "Mixamo-ready Skeletal Rig",
          "Export to .FBX, .GLB, .OBJ"
        ].map((feature, idx) => (
          <li key={idx} className="flex items-center gap-3 text-sm text-gray-200">
            <CheckCircle2 className="text-green-400 shrink-0" size={18} />
            {feature}
          </li>
        ))}
      </ul>
      
      <button 
        onClick={onUpgrade}
        disabled={isUpgrading}
        className="relative z-10 group w-full py-4 rounded-xl font-bold text-lg bg-gradient-to-r from-yellow-500 to-amber-600 text-black hover:from-yellow-400 hover:to-amber-500 transition-all disabled:opacity-50 flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(234,179,8,0.3)] hover:shadow-[0_0_30px_rgba(234,179,8,0.5)] transform hover:-translate-y-0.5"
      >
        {isUpgrading ? (
          <span className="animate-pulse">Processing Payment...</span>
        ) : (
          <>
            Upgrade to High Quality
            <ArrowRight className="group-hover:translate-x-1 transition-transform" size={20} />
          </>
        )}
      </button>
    </div>
  );
}
