import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, ContactShadows, useGLTF, Center, Html, useProgress } from '@react-three/drei';

function Loader() {
  const { progress } = useProgress();
  return (
    <Html center>
      <div className="text-indigo-400 font-bold bg-gray-900/80 px-4 py-2 rounded-lg whitespace-nowrap">
        Loading 3D Model: {progress.toFixed(0)}%
      </div>
    </Html>
  );
}

function Model({ url }) {
  if (!url) return null;
  const { scene } = useGLTF(url);
  
  return (
    <Center>
      <primitive object={scene} scale={2} />
    </Center>
  );
}

export default function ModelViewer({ modelUrl }) {
  return (
    <div className="w-full h-full min-h-[400px] rounded-2xl overflow-hidden bg-gradient-to-b from-gray-900 to-[#050505] border border-white/10 shadow-2xl relative">
      <Canvas camera={{ position: [0, 2, 6], fov: 50 }}>
        <color attach="background" args={['#0a0a0c']} />
        
        <ambientLight intensity={1.5} />
        <spotLight position={[10, 10, 10]} angle={0.2} penumbra={1} intensity={2} castShadow />
        <pointLight position={[-10, -10, -10]} intensity={1} />
        
        <Suspense fallback={<Loader />}>
          <Model url={modelUrl} />
          <Environment preset="city" />
          <ContactShadows position={[0, -1.5, 0]} opacity={0.5} scale={15} blur={2} far={4} />
        </Suspense>
        
        <OrbitControls 
          autoRotate 
          autoRotateSpeed={2} 
          enablePan={false} 
          minPolarAngle={Math.PI / 4} 
          maxPolarAngle={Math.PI / 1.5} 
        />
      </Canvas>
      <div className="absolute bottom-4 left-4 right-4 text-center pointer-events-none">
        <p className="text-gray-400 text-sm font-medium tracking-wider">INTERACTIVE 3D PREVIEW</p>
      </div>
    </div>
  );
}
