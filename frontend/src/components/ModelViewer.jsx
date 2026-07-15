import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, ContactShadows, useGLTF } from '@react-three/drei';

function Model({ url }) {
  // In a real scenario, uncomment the hook below to load the GLTF from the server
  // const { scene } = useGLTF(url);
  // return <primitive object={scene} />;
  
  // For the sake of this mock/demo, we render a default mesh representing the 3D generation
  return (
    <group>
      <mesh position={[0, 1, 0]} castShadow>
        <torusKnotGeometry args={[0.8, 0.25, 128, 32]} />
        <meshStandardMaterial color="#6366f1" metalness={0.7} roughness={0.2} />
      </mesh>
    </group>
  );
}

export default function ModelViewer({ modelUrl }) {
  return (
    <div className="w-full h-full min-h-[400px] rounded-2xl overflow-hidden bg-gradient-to-b from-gray-900 to-[#050505] border border-white/10 shadow-2xl relative">
      <Canvas camera={{ position: [0, 2, 5], fov: 50 }}>
        <color attach="background" args={['#0a0a0c']} />
        
        <ambientLight intensity={0.5} />
        <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={1} castShadow />
        <pointLight position={[-10, -10, -10]} intensity={0.5} />
        
        <Suspense fallback={null}>
          <Model url={modelUrl} />
          <Environment preset="city" />
          <ContactShadows position={[0, 0, 0]} opacity={0.4} scale={10} blur={2} far={4} />
        </Suspense>
        
        <OrbitControls 
          autoRotate 
          autoRotateSpeed={2} 
          enablePan={false} 
          minPolarAngle={Math.PI / 4} 
          maxPolarAngle={Math.PI / 2} 
        />
      </Canvas>
      <div className="absolute bottom-4 left-4 right-4 text-center pointer-events-none">
        <p className="text-gray-400 text-sm font-medium tracking-wider">INTERACTIVE 3D PREVIEW</p>
      </div>
    </div>
  );
}
