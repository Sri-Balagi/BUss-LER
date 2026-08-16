"use client";

import { useMemo, useRef, useState, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { motion } from "framer-motion";

function NeuralNetwork() {
  const groupRef = useRef<THREE.Group>(null);
  const particleCount = 150;
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    setIsDark(document.documentElement.classList.contains("dark"));
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.classList.contains("dark"));
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
    return () => observer.disconnect();
  }, []);

  const { particles, lines } = useMemo(() => {
    const p = new Float32Array(particleCount * 3);
    const positions = [];
    for (let i = 0; i < particleCount; i++) {
      const x = (Math.random() - 0.5) * 35;
      const y = (Math.random() - 0.5) * 35;
      const z = (Math.random() - 0.5) * 35;
      p[i * 3] = x;
      p[i * 3 + 1] = y;
      p[i * 3 + 2] = z;
      positions.push(new THREE.Vector3(x, y, z));
    }
    
    const l = [];
    for (let i = 0; i < particleCount; i++) {
      for (let j = i + 1; j < particleCount; j++) {
        if (positions[i].distanceTo(positions[j]) < 9) {
          l.push(positions[i].x, positions[i].y, positions[i].z);
          l.push(positions[j].x, positions[j].y, positions[j].z);
        }
      }
    }
    
    return { particles: p, lines: new Float32Array(l) };
  }, [particleCount]);

  const pGeo = useMemo(() => {
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(particles, 3));
    return geo;
  }, [particles]);
  
  const lGeo = useMemo(() => {
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(lines, 3));
    return geo;
  }, [lines]);

  useFrame(({ clock, mouse, camera }) => {
    const time = clock.getElapsedTime() * 0.02;
    
    if (groupRef.current) {
      groupRef.current.rotation.y = time;
      groupRef.current.rotation.x = time * 0.5;
    }
    
    camera.position.x += (mouse.x * 3 - camera.position.x) * 0.02;
    camera.position.y += (mouse.y * 3 - camera.position.y) * 0.02;
    camera.lookAt(0, 0, 0);
  });

  return (
    <group ref={groupRef}>
      <points geometry={pGeo}>
        <pointsMaterial size={0.15} color={isDark ? "#ECE2D2" : "#141414"} transparent opacity={0.5} />
      </points>
      <lineSegments geometry={lGeo}>
        <lineBasicMaterial color={isDark ? "#ECE2D2" : "#141414"} transparent opacity={0.1} />
      </lineSegments>
      <mesh>
        <sphereGeometry args={[1.5, 32, 32]} />
        <meshBasicMaterial color="#ED7D27" transparent opacity={0.8} />
      </mesh>
    </group>
  );
}

export function LiveCognitiveGraph() {
  return (
    <div className="w-full h-full relative bg-deep-space">
      <Canvas camera={{ position: [0, 0, 40], fov: 45 }} gl={{ alpha: true, antialias: true }}>
        <NeuralNetwork />
      </Canvas>
      <div className="absolute bottom-6 left-6 pointer-events-none">
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5, duration: 1 }}
          className="flex items-center gap-3"
        >
          <div className="w-2 h-2 rounded-full bg-accent animate-pulse-slow" />
          <span className="font-mono text-xs uppercase tracking-widest text-secondary">
            Live Cognitive Topology
          </span>
        </motion.div>
      </div>
      <div className="absolute inset-0 pointer-events-none rounded-2xl shadow-[inset_0_0_40px_rgba(0,0,0,0.02)] dark:shadow-[inset_0_0_40px_rgba(0,0,0,0.2)] transition-shadow" />
    </div>
  );
}
