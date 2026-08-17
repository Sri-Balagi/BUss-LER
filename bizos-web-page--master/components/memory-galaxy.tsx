"use client";

import { useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Html } from "@react-three/drei";
import * as THREE from "three";

// 12 Clean, Distinct Memory Nodes for Hotel Balagi Bhavan
export const MEMORY_NODES = [
  { id: 0, label: "Hotel Balagi Bhavan Master Hub", position: new THREE.Vector3(0, 0, 0), size: 2.4, isMaster: true, category: "Core Hub" },
  { id: 1, label: "Aavin Milk & Ghee SLA", position: new THREE.Vector3(-24, 14, -10), size: 1.6, isMaster: false, category: "Procurement" },
  { id: 2, label: "Koyambedu Fresh Vegetables", position: new THREE.Vector3(-16, 22, 12), size: 1.5, isMaster: false, category: "Procurement" },
  { id: 3, label: "South Indian Thali Recipe Standard", position: new THREE.Vector3(24, 12, -14), size: 1.7, isMaster: false, category: "Kitchen SOP" },
  { id: 4, label: "Mini Tiffin & Ghee Roast Dosa", position: new THREE.Vector3(16, 20, 10), size: 1.5, isMaster: false, category: "Kitchen SOP" },
  { id: 5, label: "Table 12 VIP Guest Preferences", position: new THREE.Vector3(-26, -12, 14), size: 1.6, isMaster: false, category: "Guest Desk" },
  { id: 6, label: "Banquet Hall A Bookings", position: new THREE.Vector3(-14, -20, -12), size: 1.6, isMaster: false, category: "Banquet Sales" },
  { id: 7, label: "Swiggy & Zomato Delivery POS", position: new THREE.Vector3(26, -10, 16), size: 1.7, isMaster: false, category: "POS Gateway" },
  { id: 8, label: "Pine Labs POS Settlement", position: new THREE.Vector3(14, -20, -14), size: 1.5, isMaster: false, category: "POS Gateway" },
  { id: 9, label: "FSSAI Cold Storage Telemetry", position: new THREE.Vector3(0, 26, -6), size: 1.6, isMaster: false, category: "Safety Audit" },
  { id: 10, label: "45-Staff Shift Roster", position: new THREE.Vector3(-6, -26, 6), size: 1.5, isMaster: false, category: "Staffing" },
  { id: 11, label: "Daily POS Revenue Ledger", position: new THREE.Vector3(20, 0, 24), size: 1.6, isMaster: false, category: "Finance" },
];

export const CONNECTED_PAIRS: [number, number][] = [
  // Connect Master Hub to all major nodes
  [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [0, 8], [0, 9], [0, 10], [0, 11],
  // Constellation web inter-connections
  [1, 2], [1, 3], [3, 4], [4, 7], [5, 6], [7, 8], [9, 1], [9, 3], [10, 6], [11, 7], [11, 8]
];

function TravelingPulsePackets() {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const dummy = useMemo(() => new THREE.Object3D(), []);

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    const time = clock.getElapsedTime() * 0.4;

    CONNECTED_PAIRS.forEach((pair, idx) => {
      const src = MEMORY_NODES[pair[0]].position;
      const dst = MEMORY_NODES[pair[1]].position;

      // Calculate position along line based on time loop
      const progress = (time + idx * 0.12) % 1;
      const currentPos = new THREE.Vector3().lerpVectors(src, dst, progress);

      dummy.position.copy(currentPos);
      dummy.scale.setScalar(0.4 + Math.sin(progress * Math.PI) * 0.3);
      dummy.updateMatrix();
      meshRef.current!.setMatrixAt(idx, dummy.matrix);
    });

    meshRef.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <instancedMesh ref={meshRef} args={[undefined, undefined, CONNECTED_PAIRS.length]}>
      <sphereGeometry args={[0.4, 16, 16]} />
      <meshBasicMaterial color="#ED7D27" transparent opacity={0.9} />
    </instancedMesh>
  );
}

function CleanObsidianGraph({ onNodeClick }: { onNodeClick?: (node: any) => void }) {
  const groupRef = useRef<THREE.Group>(null);
  const linesRef = useRef<THREE.LineSegments>(null);
  const aurasRef = useRef<THREE.Group>(null);

  // Build connecting line geometry
  const linePositions = useMemo(() => {
    const coords: number[] = [];
    CONNECTED_PAIRS.forEach(([srcIdx, dstIdx]) => {
      const src = MEMORY_NODES[srcIdx].position;
      const dst = MEMORY_NODES[dstIdx].position;
      coords.push(src.x, src.y, src.z);
      coords.push(dst.x, dst.y, dst.z);
    });
    return new Float32Array(coords);
  }, []);

  const lineGeometry = useMemo(() => {
    const geom = new THREE.BufferGeometry();
    geom.setAttribute("position", new THREE.BufferAttribute(linePositions, 3));
    return geom;
  }, [linePositions]);

  // Smooth rotation & gentle breathing of node aura halos
  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();

    if (groupRef.current) {
      groupRef.current.rotation.y = t * 0.08;
      groupRef.current.rotation.x = Math.sin(t * 0.04) * 0.05;
    }

    if (aurasRef.current) {
      aurasRef.current.children.forEach((child, i) => {
        const pulse = 1 + Math.sin(t * 3 + i * 0.5) * 0.12;
        child.scale.setScalar(pulse);
      });
    }
  });

  return (
    <group ref={groupRef}>
      {/* Crisp Warm Orange Line Edges */}
      <lineSegments ref={linesRef} geometry={lineGeometry}>
        <lineBasicMaterial color="#ED7D27" transparent opacity={0.5} linewidth={2} />
      </lineSegments>

      {/* Traveling Energy Pulse Packets */}
      <TravelingPulsePackets />

      {/* Breathing Aura Rings around Nodes */}
      <group ref={aurasRef}>
        {MEMORY_NODES.map((node) => (
          <mesh key={`aura-${node.id}`} position={node.position}>
            <sphereGeometry args={[node.size * 1.35, 24, 24]} />
            <meshBasicMaterial color="#ED7D27" transparent opacity={0.12} wireframe />
          </mesh>
        ))}
      </group>

      {/* 12 Polished Node Spheres with Clearcoat Gloss */}
      {MEMORY_NODES.map((node) => (
        <mesh
          key={node.id}
          position={node.position}
          onClick={(e) => {
            e.stopPropagation();
            if (onNodeClick) onNodeClick(node);
          }}
        >
          <sphereGeometry args={[node.size, 32, 32]} />
          <meshPhysicalMaterial
            color="#ED7D27"
            emissive="#ED7D27"
            emissiveIntensity={node.isMaster ? 0.9 : 0.45}
            roughness={0.1}
            metalness={0.2}
            clearcoat={1.0}
            clearcoatRoughness={0.1}
          />
        </mesh>
      ))}

      {/* Floating 3D Node Labels */}
      {MEMORY_NODES.map((node) => (
        <group key={node.id} position={node.position}>
          <Html distanceFactor={52} center className="pointer-events-none select-none">
            <div
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-full border shadow-xl whitespace-nowrap backdrop-blur-md transition-transform hover:scale-105 ${
                node.isMaster
                  ? "border-amber-500 bg-amber-500/25 dark:bg-amber-900/50 text-amber-600 dark:text-amber-300 font-bold"
                  : "border-[#ED7D27]/40 bg-[#FAF7F2]/95 dark:bg-zinc-900/95 text-ink font-semibold"
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-[#ED7D27] animate-pulse" />
              <span className="font-mono text-[11.5px] tracking-wider">
                {node.label}
              </span>
            </div>
          </Html>
        </group>
      ))}
    </group>
  );
}

export function MemoryGalaxyVisualizer({ onNodeClick }: { onNodeClick?: (node: any) => void }) {
  return (
    <div className="w-full h-full absolute inset-0 cursor-move">
      <Canvas camera={{ position: [0, 20, 75], fov: 50 }}>
        <ambientLight intensity={0.8} />
        <pointLight position={[50, 50, 50]} intensity={1.5} color="#ED7D27" />
        <directionalLight position={[-30, 30, 20]} intensity={0.8} />

        <CleanObsidianGraph onNodeClick={onNodeClick} />

        <OrbitControls
          enablePan={true}
          enableZoom={true}
          maxDistance={120}
          minDistance={15}
          autoRotate
          autoRotateSpeed={0.45}
        />
      </Canvas>
    </div>
  );
}
