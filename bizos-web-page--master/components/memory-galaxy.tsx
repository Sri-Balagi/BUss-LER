"use client";

import { useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Stars, Text } from "@react-three/drei";
import * as THREE from "three";
import { motion } from "framer-motion-3d";
import { motion as framerMotion } from "framer-motion";

function MemoryClusters({ count = 2000 }) {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  
  const particles = useMemo(() => {
    const temp = [];
    
    for (let i = 0; i < count; i++) {
      // Create clusters
      const cluster = Math.floor(Math.random() * 5);
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos((Math.random() * 2) - 1);
      const r = 20 + Math.random() * 30 + (cluster * 15);
      
      const x = r * Math.sin(phi) * Math.cos(theta);
      const y = r * Math.sin(phi) * Math.sin(theta);
      const z = r * Math.cos(phi);
      
      const scale = Math.random() * 0.5 + 0.1;
      
      temp.push({ position: new THREE.Vector3(x, y, z), scale });
    }
    return temp;
  }, [count]);

  const dummy = useMemo(() => new THREE.Object3D(), []);

  useFrame(({ clock }) => {
    if (meshRef.current) {
      const time = clock.getElapsedTime() * 0.1;
      
      particles.forEach((particle, i) => {
        // Slow rotation around origin
        dummy.position.copy(particle.position);
        dummy.position.applyAxisAngle(new THREE.Vector3(0, 1, 0), time + i * 0.001);
        
        // Gentle breathing scale
        const pulse = Math.sin(time * 5 + i) * 0.1 + 1;
        dummy.scale.set(particle.scale * pulse, particle.scale * pulse, particle.scale * pulse);
        
        dummy.updateMatrix();
        meshRef.current!.setMatrixAt(i, dummy.matrix);
      });
      meshRef.current.instanceMatrix.needsUpdate = true;
    }
  });

  return (
    <instancedMesh ref={meshRef} args={[undefined, undefined, count]}>
      <sphereGeometry args={[0.5, 16, 16]} />
      <meshBasicMaterial color="#ED7D27" transparent opacity={0.6} />
    </instancedMesh>
  );
}

function ConstellationLines() {
  const lineRef = useRef<THREE.LineSegments>(null);
  
  const points = useMemo(() => {
    const pts = [];
    for (let i = 0; i < 50; i++) {
      const r = 30;
      pts.push(
        new THREE.Vector3((Math.random() - 0.5) * r, (Math.random() - 0.5) * r, (Math.random() - 0.5) * r),
        new THREE.Vector3((Math.random() - 0.5) * r, (Math.random() - 0.5) * r, (Math.random() - 0.5) * r)
      );
    }
    return pts;
  }, []);
  
  const geometry = useMemo(() => new THREE.BufferGeometry().setFromPoints(points), [points]);
  
  useFrame(({ clock }) => {
    if (lineRef.current) {
      lineRef.current.rotation.y = clock.getElapsedTime() * 0.05;
      // Read theme from body class (black for light mode, white for dark mode)
      const isDark = document.documentElement.classList.contains("dark");
      (lineRef.current.material as THREE.LineBasicMaterial).color.set(isDark ? "#ECE2D2" : "#141414");
    }
  });

  return (
    <lineSegments ref={lineRef} geometry={geometry}>
      <lineBasicMaterial color="#141414" transparent opacity={0.25} />
    </lineSegments>
  );
}

export function MemoryGalaxyVisualizer() {
  return (
    <div className="w-full h-full absolute inset-0 cursor-move">
      <Canvas camera={{ position: [0, 20, 80], fov: 45 }}>
        <ambientLight intensity={0.2} />
        <MemoryClusters />
        <ConstellationLines />
        <Stars radius={100} depth={50} count={3000} factor={4} saturation={0} fade speed={1} />
        
        <OrbitControls 
          enablePan={false}
          enableZoom={true}
          maxDistance={100}
          minDistance={10}
          autoRotate
          autoRotateSpeed={0.5}
        />
      </Canvas>

      <framerMotion.div 
        className="absolute bottom-10 left-1/2 -translate-x-1/2 glass-panel px-6 py-3 rounded-full flex items-center gap-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1 }}
      >
        <div className="w-2 h-2 rounded-full bg-cognition-memory  animate-pulse-slow" />
        <span className="font-mono text-sm tracking-widest text-primary uppercase">
          Semantic Clusters Linked
        </span>
        <span className="font-mono text-xs text-secondary">|</span>
        <span className="font-mono text-xs text-secondary">Scroll to traverse</span>
      </framerMotion.div>
    </div>
  );
}
