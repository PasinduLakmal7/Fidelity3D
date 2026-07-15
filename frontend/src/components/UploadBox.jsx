import React, { useState } from 'react';
import { UploadCloud, Image as ImageIcon, X } from 'lucide-react';

export default function UploadBox({ onUpload, isLoading }) {
  const [files, setFiles] = useState([]);
  
  const handleFileChange = (e) => {
    const selected = Array.from(e.target.files);
    if (files.length + selected.length > 4) {
      alert("You can only upload up to 4 images (Front, Back, Left, Right).");
      return;
    }
    setFiles((prev) => [...prev, ...selected].slice(0, 4));
  };
  
  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };
  
  const handleSubmit = () => {
    if (files.length !== 4) {
      alert("Please upload exactly 4 images.");
      return;
    }
    onUpload(files);
  };
  
  const placeholders = ["Front", "Back", "Left", "Right"];
  
  return (
    <div className="w-full max-w-3xl mx-auto p-8 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-md shadow-2xl">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">Upload Reference Images</h2>
        <p className="text-gray-400">Provide 4 angles of your character/object to generate a 3D model.</p>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {placeholders.map((label, idx) => (
          <div key={label} className="relative aspect-square rounded-xl border-2 border-dashed border-gray-600 flex flex-col items-center justify-center overflow-hidden bg-black/20 group">
            {files[idx] ? (
              <>
                <img src={URL.createObjectURL(files[idx])} alt={label} className="absolute inset-0 w-full h-full object-cover" />
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <button onClick={() => removeFile(idx)} className="p-2 bg-red-500 rounded-full text-white hover:bg-red-600 transition-colors">
                    <X size={20} />
                  </button>
                </div>
              </>
            ) : (
              <>
                <ImageIcon className="text-gray-500 mb-2" size={32} />
                <span className="text-sm text-gray-500 font-medium">{label}</span>
              </>
            )}
          </div>
        ))}
      </div>
      
      {files.length < 4 && (
        <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-indigo-500/50 rounded-xl cursor-pointer bg-indigo-500/5 hover:bg-indigo-500/10 transition-colors mb-6 group">
          <UploadCloud className="text-indigo-400 mb-2 group-hover:scale-110 transition-transform" size={36} />
          <span className="text-indigo-300 font-medium">Click to browse or drag images here</span>
          <span className="text-xs text-indigo-300/60 mt-1">JPEG, PNG up to 10MB</span>
          <input type="file" className="hidden" multiple accept="image/*" onChange={handleFileChange} />
        </label>
      )}
      
      <button 
        onClick={handleSubmit} 
        disabled={files.length !== 4 || isLoading}
        className="w-full py-4 rounded-xl font-bold text-lg bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-500 hover:to-purple-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(79,70,229,0.3)] hover:shadow-[0_0_30px_rgba(79,70,229,0.5)] transform hover:-translate-y-0.5 flex items-center justify-center"
      >
        {isLoading ? (
          <>
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Uploading & Processing...
          </>
        ) : (
          "Generate 3D Model"
        )}
      </button>
    </div>
  );
}
