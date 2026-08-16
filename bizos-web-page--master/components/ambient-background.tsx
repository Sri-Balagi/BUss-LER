"use client";

import { useRef, useMemo, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";

function Particles({ count = 380 }) {
  const mesh = useRef<THREE.InstancedMesh>(null);
  
  const particles = useMemo(() => {
    const temp = [];
    const colors = [
      new THREE.Color("#FFFFFF"), // White
      new THREE.Color("#E7E2D9"), // Warm Beige
      new THREE.Color("#F4B27D"), // Soft Orange
      new THREE.Color("#7DD3FC"), // Soft Blue
    ];
    for (let i = 0; i < count; i++) {
      const time = Math.random() * 100;
      const factor = 10 + Math.random() * 40;
      const speed = 0.002 + Math.random() / 600;
      const x = Math.random() * 160 - 80;
      const y = Math.random() * 120 - 60;
      const z = Math.random() * 60 - 30;
      const scale = 0.25 + Math.random() * 0.8;
      const color = colors[Math.floor(Math.random() * colors.length)];

      temp.push({ time, factor, speed, x, y, z, scale, color });
    }
    return temp;
  }, [count]);

  useEffect(() => {
    if (mesh.current) {
      particles.forEach((p, i) => {
        mesh.current!.setColorAt(i, p.color);
      });
      if (mesh.current.instanceColor) {
        mesh.current.instanceColor.needsUpdate = true;
      }
    }
  }, [particles]);

  const dummy = useMemo(() => new THREE.Object3D(), []);

  useFrame((state) => {
    const pointer = state.pointer;
    const mX = pointer.x * 50;
    const mY = pointer.y * 30;

    if (mesh.current) {
      const isDark = document.documentElement.classList.contains("dark");
      (mesh.current.material as THREE.MeshStandardMaterial).opacity = isDark ? 0.20 : 0.28;

      particles.forEach((particle, i) => {
        let { time, factor, speed, x, y, z, scale } = particle;

        time = particle.time += speed;
        let currentX = x + Math.cos(time) * (factor * 0.15);
        let currentY = y + Math.sin(time) * (factor * 0.15);
        let currentZ = z + Math.sin(time) * (factor * 0.15);

        // Subtly push particles away from cursor
        const dx = mX - currentX;
        const dy = mY - currentY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 25) {
          const force = (25 - dist) / 25;
          currentX -= (dx / dist) * force * 3;
          currentY -= (dy / dist) * force * 3;
        }

        dummy.position.set(currentX, currentY, currentZ);
        dummy.scale.setScalar(scale);
        dummy.updateMatrix();

        mesh.current!.setMatrixAt(i, dummy.matrix);
      });
      mesh.current.instanceMatrix.needsUpdate = true;
    }
  });

  return (
    <>
      <ambientLight intensity={0.8} />
      <instancedMesh ref={mesh} args={[undefined, undefined, count]}>
        <sphereGeometry args={[0.2, 8, 8]} />
        <meshStandardMaterial transparent opacity={0.16} roughness={0.8} />
      </instancedMesh>
    </>
  );
}

export function AmbientBackground() {
  return (
    <div className="fixed inset-0 z-0 pointer-events-none mix-blend-normal overflow-hidden">
      {/* Subtle low-opacity radial ambient lighting */}
      <div className="absolute -top-[20%] left-1/4 h-[600px] w-[600px] rounded-full bg-[radial-gradient(circle,rgba(232,123,42,0.06)_0%,transparent_70%)] blur-3xl pointer-events-none" />
      <div className="absolute top-1/3 -right-[10%] h-[600px] w-[600px] rounded-full bg-[radial-gradient(circle,rgba(56,189,248,0.05)_0%,transparent_70%)] blur-3xl pointer-events-none" />
      <div className="absolute -bottom-[20%] left-1/3 h-[700px] w-[700px] rounded-full bg-[radial-gradient(circle,rgba(232,123,42,0.04)_0%,transparent_70%)] blur-3xl pointer-events-none" />

      <Canvas camera={{ position: [0, 0, 50], fov: 60 }} gl={{ alpha: true, antialias: true }}>
        <Particles count={380} />
      </Canvas>
    </div>
  );
}
