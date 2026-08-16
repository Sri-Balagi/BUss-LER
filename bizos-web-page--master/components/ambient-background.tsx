"use client";

import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";

function Particles({ count = 500 }) {
  const mesh = useRef<THREE.InstancedMesh>(null);
  const light = useRef<THREE.PointLight>(null);

  const particles = useMemo(() => {
    const temp = [];
    for (let i = 0; i < count; i++) {
      const time = Math.random() * 100;
      const factor = Math.random() * 100;
      const speed = 0.01 + Math.random() / 200;
      const x = Math.random() * 200 - 100;
      const y = Math.random() * 200 - 100;
      const z = Math.random() * 200 - 100;

      temp.push({ time, factor, speed, x, y, z });
    }
    return temp;
  }, [count]);

  const dummy = useMemo(() => new THREE.Object3D(), []);

  useFrame(() => {
    if (mesh.current) {
      const isDark = document.documentElement.classList.contains("dark");
      (mesh.current.material as THREE.MeshStandardMaterial).color.set(isDark ? "#ECE2D2" : "#141414");

      particles.forEach((particle, i) => {
        let { time, factor, speed, x, y, z } = particle;

        time = particle.time += speed / 2;
        const currentX = x + Math.cos(time) * factor;
        const currentY = y + Math.sin(time) * factor;
        const currentZ = z + Math.sin(time) * factor;

        dummy.position.set(currentX, currentY, currentZ);
        dummy.updateMatrix();

        mesh.current!.setMatrixAt(i, dummy.matrix);
      });
      mesh.current.instanceMatrix.needsUpdate = true;
    }
  });

  return (
    <>
      <pointLight ref={light} distance={100} intensity={0.5} color="#00F0FF" />
      <instancedMesh ref={mesh} args={[undefined, undefined, count]}>
        <sphereGeometry args={[0.2, 8, 8]} />
        <meshStandardMaterial color="#141414" transparent opacity={0.4} roughness={1} />
      </instancedMesh>
    </>
  );
}

export function AmbientBackground() {
  return (
    <div className="fixed inset-0 z-[-1] bg-deep-space pointer-events-none">
      <Canvas camera={{ position: [0, 0, 50], fov: 60 }} gl={{ alpha: true, antialias: false }}>
        <ambientLight intensity={0.2} />
        <Particles count={600} />
      </Canvas>
    </div>
  );
}
