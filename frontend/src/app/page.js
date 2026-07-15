"use client";

import React, { useState, useEffect } from 'react';
import UploadBox from '@/components/UploadBox';
import ModelViewer from '@/components/ModelViewer';
import Paywall from '@/components/Paywall';
import { uploadImages, checkJobStatus, triggerPremiumUpgrade } from '@/utils/api';

export default function Home() {
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isUpgrading, setIsUpgrading] = useState(false);
  const [modelUrl, setModelUrl] = useState(null);

  // Polling mechanism
  useEffect(() => {
    let intervalId;
    const activeStates = ['FREE_PENDING', 'FREE_PROCESSING', 'PAID_PENDING', 'PAID_PROCESSING'];
    
    if (jobId && activeStates.includes(status)) {
      intervalId = setInterval(async () => {
        try {
          const data = await checkJobStatus(jobId);
          setStatus(data.status);
          if (data.output_file_path) {
            setModelUrl(data.output_file_path);
          }
        } catch (error) {
          console.error("Error polling status:", error);
        }
      }, 3000);
    }
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [jobId, status]);

  const handleUpload = async (files) => {
    setIsLoading(true);
    try {
      const data = await uploadImages(files);
      setJobId(data.job_id);
      setStatus(data.status);
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Failed to upload images. Ensure the backend is running.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpgrade = async () => {
    setIsUpgrading(true);
    try {
      await triggerPremiumUpgrade(jobId);
      setStatus('PAID_PROCESSING');
    } catch (error) {
      console.error("Upgrade failed:", error);
      alert("Payment failed.");
    } finally {
      setIsUpgrading(false);
    }
  };

  const isModelReady = ['FREE_COMPLETED', 'PAID_COMPLETED'].includes(status);
  const isProcessing = ['FREE_PENDING', 'FREE_PROCESSING', 'PAID_PENDING', 'PAID_PROCESSING'].includes(status);

  return (
    <main className="min-h-screen bg-[#0a0a0c] text-white selection:bg-indigo-500/30 overflow-x-hidden relative">
      {/* Background glow effects */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-5xl h-96 bg-indigo-600/10 blur-[120px] rounded-[100%] pointer-events-none"></div>
      
      <div className="container mx-auto px-4 py-16 relative z-10 flex flex-col min-h-screen">
        <header className="mb-12 text-center">
          <div className="inline-block mb-4 px-4 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-xs font-semibold tracking-wide uppercase">
            v1.0 BETA
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white to-gray-500">
            Fidelity<span className="text-indigo-500">3D</span>
          </h1>
          <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto font-light leading-relaxed">
            Transform 2D reference images into fully animated 3D models in seconds. Powered by state-of-the-art AI.
          </p>
        </header>

        <div className="flex-grow flex flex-col justify-center">
          {!jobId && (
            <div className="w-full transition-all duration-1000 ease-out transform">
              <UploadBox onUpload={handleUpload} isLoading={isLoading} />
            </div>
          )}

          {jobId && (
            <div className="max-w-6xl mx-auto w-full transition-all duration-500 ease-in">
              {/* Status Indicator */}
              <div className="mb-8 p-5 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-between shadow-lg backdrop-blur-sm">
                <div>
                  <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-1">Job ID: {jobId}</p>
                  <div className="flex items-center gap-3">
                    <span className="relative flex h-3 w-3">
                      {isProcessing && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>}
                      <span className={`relative inline-flex rounded-full h-3 w-3 ${isModelReady ? 'bg-green-500' : 'bg-indigo-500'}`}></span>
                    </span>
                    <p className="font-semibold text-lg text-white">Status: <span className="text-indigo-400">{status}</span></p>
                  </div>
                </div>
              </div>

              {/* Viewer & Paywall Layout */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:h-[600px]">
                <div className="lg:col-span-2 aspect-square lg:aspect-auto h-[400px] lg:h-full relative rounded-2xl overflow-hidden ring-1 ring-white/10 shadow-2xl">
                  {isProcessing && !isModelReady && (
                    <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-900/60 backdrop-blur-md z-10">
                      <div className="w-16 h-16 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin mb-4 shadow-[0_0_15px_rgba(99,102,241,0.5)]"></div>
                      <p className="text-indigo-300 font-medium animate-pulse tracking-wide">Generating your 3D Model...</p>
                    </div>
                  )}
                  <ModelViewer modelUrl={modelUrl} />
                </div>
                
                <div className="lg:col-span-1 h-full">
                  {status === 'FREE_COMPLETED' ? (
                    <div className="h-full transition-all duration-700 ease-out transform">
                      <Paywall onUpgrade={handleUpgrade} isUpgrading={isUpgrading} />
                    </div>
                  ) : status === 'PAID_COMPLETED' ? (
                     <div className="h-full p-8 rounded-2xl bg-gradient-to-br from-green-900/20 to-emerald-900/20 border border-green-500/30 flex flex-col items-center justify-center text-center backdrop-blur-md">
                        <div className="w-20 h-20 rounded-full bg-green-500/20 flex items-center justify-center mb-6 border border-green-500/50 shadow-[0_0_30px_rgba(34,197,94,0.3)]">
                          <svg className="w-10 h-10 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <h4 className="text-2xl font-bold text-white mb-2">Premium Unlocked</h4>
                        <p className="text-green-300/80 mb-6">High-Fidelity 3D model generated successfully.</p>
                        <button className="w-full py-3 rounded-xl font-bold bg-white/10 hover:bg-white/20 text-white transition-colors border border-white/10">
                          Download .GLB
                        </button>
                     </div>
                  ) : (
                    <div className="h-full p-8 rounded-2xl bg-white/5 border border-white/10 flex flex-col items-center justify-center text-center backdrop-blur-md">
                      <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mb-4 ring-1 ring-white/10">
                        <svg className="w-8 h-8 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                        </svg>
                      </div>
                      <h4 className="text-xl font-bold text-gray-300 mb-2">Premium Upgrade</h4>
                      <p className="text-sm text-gray-500">Wait for the free tier to complete to unlock premium high-fidelity generation.</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
