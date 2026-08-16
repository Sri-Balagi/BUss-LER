"use client";

import { useMemo, useRef, useState, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Stars, Html } from "@react-three/drei";
import * as THREE from "three";
import { motion as framerMotion } from "framer-motion";

interface MemoryNode {
  id: string;
  label: string;
  category: string;
  size: number;
  pos: [number, number, number];
  color: string;
  emissive: string;
  detail: string;
}

const MEMORY_NODES: MemoryNode[] = [
  {
    id: "core",
    label: "Balagi Bhavan Core Memory Vault",
    category: "core",
    size: 3.2,
    pos: [0, 0, 0],
    color: "#FF8C00",
    emissive: "#FF4500",
    detail: "Primary cognitive memory store for Hotel Balagi Bhavan — 45 staff, 4 halls, 14-item Thali SOPs.",
  },
  // Recipe Cluster
  {
    id: "rec_1",
    label: "14-Item South Indian Thali SOP",
    category: "recipe",
    size: 1.8,
    pos: [-26, 16, -12],
    color: "#FFA500",
    emissive: "#FF6600",
    detail: "Standardized Sambar, Rasam, Kara Kuzhambu, Kootu & Payasam batch recipes.",
  },
  {
    id: "rec_2",
    label: "Aavin Milk & Ghee Batch Ratio",
    category: "recipe",
    size: 1.3,
    pos: [-38, 24, -20],
    color: "#FFB732",
    emissive: "#FF8C00",
    detail: "Exact 150L daily milk boil & 45kg ghee allocation for filter coffee and sweets.",
  },
  {
    id: "rec_3",
    label: "Ghee Roast Dosa Batter SOP",
    category: "recipe",
    size: 1.1,
    pos: [-34, 8, -4],
    color: "#FFCC44",
    emissive: "#FFA500",
    detail: "Fermentation temperature triggers and soaking ratios for morning breakfast rush.",
  },
  {
    id: "rec_4",
    label: "Filter Coffee Decoction Engine",
    category: "recipe",
    size: 1.0,
    pos: [-20, 28, -16],
    color: "#FFD700",
    emissive: "#FFA500",
    detail: "Chicory to coffee powder ratio & boil time monitoring for 300 cups daily.",
  },
  // Supplier Cluster
  {
    id: "sup_1",
    label: "Aavin Milk 150L Daily SLA",
    category: "supplier",
    size: 1.8,
    pos: [28, 18, -14],
    color: "#FF7F00",
    emissive: "#FF4500",
    detail: "Contractual daily delivery window at 05:30 AM IST with fat content verification.",
  },
  {
    id: "sup_2",
    label: "Koyambedu Veggie Auction Feed",
    category: "supplier",
    size: 1.3,
    pos: [40, 28, -22],
    color: "#FFA040",
    emissive: "#FF6600",
    detail: "Daily wholesale vegetable pricing index and automated bulk re-order trigger.",
  },
  {
    id: "sup_3",
    label: "45kg Pure Ghee Reserve Monitor",
    category: "supplier",
    size: 1.1,
    pos: [36, 8, -6],
    color: "#FFBB55",
    emissive: "#FFA500",
    detail: "15% low-stock threshold auto-alert to procurement manager.",
  },
  // POS Cluster
  {
    id: "pos_1",
    label: "Swiggy & Zomato Realtime Stream",
    category: "pos",
    size: 1.7,
    pos: [-22, -18, 16],
    color: "#FF6A00",
    emissive: "#FF2200",
    detail: "Live order stream dispatching kitchen prep under 12-minute SLA for all orders.",
  },
  {
    id: "pos_2",
    label: "Pine Labs POS Terminal #4",
    category: "pos",
    size: 1.2,
    pos: [-34, -26, 24],
    color: "#FF8C44",
    emissive: "#FF6600",
    detail: "Counter UPI + Cash reconciliation, posting daily to profit & loss ledger.",
  },
  {
    id: "pos_3",
    label: "Kitchen Display Queue Feed",
    category: "pos",
    size: 1.1,
    pos: [-32, -10, 8],
    color: "#FFA055",
    emissive: "#FF7700",
    detail: "Priority queue mapping dining hall tables to chef stations in realtime.",
  },
  // Customer Cluster
  {
    id: "cust_1",
    label: "WhatsApp Sentiment & Feedback AI",
    category: "customer",
    size: 1.7,
    pos: [26, -16, 18],
    color: "#FFB300",
    emissive: "#FF8C00",
    detail: "AI response bot analyzing dining feedback and resolving complaints automatically.",
  },
  {
    id: "cust_2",
    label: "Banquet Hall Event Reservations",
    category: "customer",
    size: 1.2,
    pos: [36, -26, 26],
    color: "#FFC844",
    emissive: "#FFAA00",
    detail: "Weekend 120-seat family event calendar with catering configuration builder.",
  },
  {
    id: "cust_3",
    label: "Google Maps 4.8 ★ Sentiment Feed",
    category: "customer",
    size: 1.1,
    pos: [32, -8, 8],
    color: "#FFD050",
    emissive: "#FFB300",
    detail: "Realtime rating aggregator across all 4 dining branches.",
  },
  // Operations Cluster
  {
    id: "ops_1",
    label: "45-Staff Shift Roster Index",
    category: "ops",
    size: 1.5,
    pos: [0, 28, 20],
    color: "#FF9500",
    emissive: "#FF6600",
    detail: "Daily shift manager scheduling head chefs, captains & stewards across halls.",
  },
  {
    id: "ops_2",
    label: "4 Dining Hall Seating Sensor",
    category: "ops",
    size: 1.1,
    pos: [8, 36, 12],
    color: "#FFAB30",
    emissive: "#FF8C00",
    detail: "Realtime table occupancy monitoring for peak lunch & dinner queue waits.",
  },
];

const MEMORY_EDGES = [
  ["core", "rec_1"],
  ["core", "sup_1"],
  ["core", "pos_1"],
  ["core", "cust_1"],
  ["core", "ops_1"],
  ["rec_1", "rec_2"],
  ["rec_1", "rec_3"],
  ["rec_1", "rec_4"],
  ["sup_1", "sup_2"],
  ["sup_1", "sup_3"],
  ["pos_1", "pos_2"],
  ["pos_1", "pos_3"],
  ["cust_1", "cust_2"],
  ["cust_1", "cust_3"],
  ["ops_1", "ops_2"],
  ["rec_2", "sup_1"],
  ["pos_1", "cust_1"],
  ["rec_1", "ops_1"],
  ["pos_3", "ops_2"],
  ["rec_4", "sup_1"],
];

function CoreGlowRing() {
  const ringRef = useRef<THREE.Mesh>(null);
  useFrame(({ clock }) => {
    if (ringRef.current) {
      ringRef.current.rotation.x = clock.getElapsedTime() * 0.3;
      ringRef.current.rotation.z = clock.getElapsedTime() * 0.15;
    }
  });
  return (
    <mesh ref={ringRef} position={[0, 0, 0]}>
      <torusGeometry args={[7.5, 0.25, 16, 80]} />
      <meshStandardMaterial color="#FFD700" emissive="#FF8C00" emissiveIntensity={0.8} roughness={0.1} metalness={1} />
    </mesh>
  );
}

function CoreGlowRing2() {
  const ringRef = useRef<THREE.Mesh>(null);
  useFrame(({ clock }) => {
    if (ringRef.current) {
      ringRef.current.rotation.y = clock.getElapsedTime() * 0.2;
      ringRef.current.rotation.x = Math.PI / 3;
    }
  });
  return (
    <mesh ref={ringRef} position={[0, 0, 0]}>
      <torusGeometry args={[9.5, 0.15, 16, 80]} />
      <meshStandardMaterial color="#FFA500" emissive="#FF6600" emissiveIntensity={0.6} roughness={0.1} metalness={1} />
    </mesh>
  );
}

function GoldenEdges() {
  const lineGeometry = useMemo(() => {
    const points: THREE.Vector3[] = [];
    const nodeMap = new Map<string, THREE.Vector3>();
    MEMORY_NODES.forEach((n) => nodeMap.set(n.id, new THREE.Vector3(...n.pos)));
    MEMORY_EDGES.forEach(([a, b]) => {
      const src = nodeMap.get(a);
      const tgt = nodeMap.get(b);
      if (src && tgt) points.push(src, tgt);
    });
    return new THREE.BufferGeometry().setFromPoints(points);
  }, []);

  const matRef = useRef<THREE.LineBasicMaterial>(null);
  useFrame(({ clock }) => {
    if (matRef.current) {
      matRef.current.opacity = 0.3 + Math.sin(clock.getElapsedTime() * 1.5) * 0.15;
    }
  });

  return (
    <lineSegments geometry={lineGeometry}>
      <lineBasicMaterial ref={matRef} color="#FFB300" transparent opacity={0.45} />
    </lineSegments>
  );
}

function MemoryNodeMesh({
  node,
  isSelected,
  onSelect,
  isDark,
}: {
  node: MemoryNode;
  isSelected: boolean;
  onSelect: (node: MemoryNode) => void;
  isDark: boolean;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (meshRef.current) {
      const t = clock.getElapsedTime();
      const pulse = Math.sin(t * 2.5 + node.pos[0] * 0.2) * 0.07 + 1;
      meshRef.current.scale.set(pulse, pulse, pulse);
    }
    if (glowRef.current) {
      const t = clock.getElapsedTime();
      glowRef.current.scale.setScalar(1.2 + Math.sin(t * 2 + node.pos[1] * 0.3) * 0.1);
      (glowRef.current.material as THREE.MeshBasicMaterial).opacity =
        isSelected ? 0.25 + Math.sin(t * 3) * 0.08 : 0.1;
    }
  });

  return (
    <group position={node.pos}>
      <mesh ref={glowRef}>
        <sphereGeometry args={[node.size * 1.5, 24, 24]} />
        <meshBasicMaterial color={node.emissive} transparent opacity={0.1} side={THREE.BackSide} />
      </mesh>

      <mesh ref={meshRef} onClick={(e) => { e.stopPropagation(); onSelect(node); }}>
        <sphereGeometry args={[node.size, 36, 36]} />
        <meshStandardMaterial
          color={node.color}
          emissive={node.emissive}
          emissiveIntensity={isSelected ? 1.0 : 0.5}
          roughness={0.05}
          metalness={0.95}
        />
      </mesh>

      <mesh rotation={[Math.PI / 2 + node.pos[1] * 0.05, 0, 0]}>
        <torusGeometry args={[node.size * 1.35, node.size * 0.05, 12, 48]} />
        <meshBasicMaterial color={node.color} transparent opacity={isSelected ? 0.8 : 0.35} />
      </mesh>

      <Html position={[0, node.size + 2.2, 0]} center distanceFactor={65} style={{ pointerEvents: "none" }}>
        <div
          style={{
            background: isSelected
              ? (isDark
                  ? "linear-gradient(135deg, rgba(255,140,0,0.4), rgba(255,69,0,0.3))"
                  : "linear-gradient(135deg, rgba(255,140,0,0.2), rgba(255,180,0,0.15))")
              : (isDark ? "rgba(20,8,2,0.88)" : "rgba(255,255,255,0.92)"),
            border: `1px solid ${isSelected ? "#FFB300" : (isDark ? "rgba(255,140,0,0.35)" : "rgba(200,120,0,0.3)")}`,
            borderRadius: "10px",
            padding: "5px 10px",
            whiteSpace: "nowrap",
            fontFamily: "monospace",
            fontSize: "11px",
            fontWeight: 700,
            color: isSelected ? (isDark ? "#FFD700" : "#92400E") : (isDark ? "#FFAA44" : "#78350F"),
            backdropFilter: "blur(8px)",
            boxShadow: isSelected
              ? (isDark ? "0 0 16px rgba(255,165,0,0.5)" : "0 0 12px rgba(200,120,0,0.25)")
              : "0 2px 8px rgba(0,0,0,0.1)",
            transform: isSelected ? "scale(1.1)" : "scale(1)",
            transition: "all 0.2s ease",
          }}
        >
          {node.label}
        </div>
      </Html>
    </group>
  );
}

function GoldenDustCloud({ count = 600 }: { count?: number }) {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const particles = useMemo(() => {
    return Array.from({ length: count }, () => ({
      pos: new THREE.Vector3(
        (Math.random() - 0.5) * 100,
        (Math.random() - 0.5) * 100,
        (Math.random() - 0.5) * 100
      ),
      scale: Math.random() * 0.25 + 0.08,
      speed: Math.random() * 0.4 + 0.1,
    }));
  }, [count]);

  const dummy = useMemo(() => new THREE.Object3D(), []);

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    const t = clock.getElapsedTime();
    particles.forEach((p, i) => {
      dummy.position.copy(p.pos);
      dummy.position.y += Math.sin(t * p.speed + i) * 0.3;
      dummy.position.applyAxisAngle(new THREE.Vector3(0, 1, 0), t * 0.025);
      dummy.scale.setScalar(p.scale);
      dummy.updateMatrix();
      meshRef.current!.setMatrixAt(i, dummy.matrix);
    });
    meshRef.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <instancedMesh ref={meshRef} args={[undefined, undefined, count]}>
      <sphereGeometry args={[0.22, 8, 8]} />
      <meshBasicMaterial color="#FFB300" transparent opacity={0.4} />
    </instancedMesh>
  );
}

// ── Main Export ───────────────────────────────────────────────────────────────
export function MemoryGalaxyVisualizer() {
  const [selectedNode, setSelectedNode] = useState<MemoryNode | null>(MEMORY_NODES[0]);
  const [isDark, setIsDark] = useState(false);

  // Sync with document dark class (Tailwind dark mode)
  useEffect(() => {
    const check = () => setIsDark(document.documentElement.classList.contains("dark"));
    check();

    const observer = new MutationObserver(check);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
    return () => observer.disconnect();
  }, []);

  // Background — dark mode: deep ember space | light mode: pure white
  const canvasBg = isDark
    ? "radial-gradient(ellipse at 40% 40%, #2d1200 0%, #1a0900 40%, #0f0600 75%, #0a0400 100%)"
    : "#ffffff";

  const cardBg = isDark
    ? "linear-gradient(135deg, rgba(30,15,0,0.96), rgba(20,8,0,0.96))"
    : "linear-gradient(135deg, rgba(255,255,255,0.98), rgba(255,251,235,0.98))";

  const cardBorder = isDark ? "rgba(255,165,0,0.4)" : "rgba(210,140,0,0.35)";
  const cardShadow = isDark
    ? "0 8px 40px rgba(255,100,0,0.25), inset 0 1px 0 rgba(255,200,0,0.1)"
    : "0 8px 28px rgba(180,100,0,0.14), inset 0 1px 0 rgba(255,220,100,0.4)";

  const pillBg = isDark ? "rgba(30,12,0,0.92)" : "rgba(255,255,255,0.95)";
  const pillBorder = isDark ? "rgba(255,140,0,0.35)" : "rgba(200,140,0,0.3)";
  const pillTextColor = isDark ? "#FFD700" : "#78350F";
  const pillSubColor = isDark ? "rgba(255,165,0,0.5)" : "rgba(120,70,0,0.45)";

  return (
    <div className="w-full h-full absolute inset-0 cursor-grab active:cursor-grabbing">
      <Canvas
        camera={{ position: [0, 30, 100], fov: 46 }}
        style={{ background: canvasBg }}
      >
        {/* Warm golden lighting — brighter in light mode */}
        <ambientLight intensity={isDark ? 0.3 : 0.7} color="#FF8C00" />
        <pointLight position={[0, 0, 0]} intensity={isDark ? 4 : 6} color="#FFA500" distance={80} decay={2} />
        <pointLight position={[40, 50, 30]} intensity={isDark ? 2 : 3} color="#FFD700" distance={120} decay={2} />
        <pointLight position={[-40, -40, -30]} intensity={isDark ? 1.5 : 2} color="#FF6600" distance={100} decay={2} />
        <pointLight position={[0, -60, 0]} intensity={isDark ? 1 : 1.5} color="#FF4500" distance={100} decay={2} />

        <CoreGlowRing />
        <CoreGlowRing2 />
        <GoldenEdges />

        {MEMORY_NODES.map((node) => (
          <MemoryNodeMesh
            key={node.id}
            node={node}
            isSelected={selectedNode?.id === node.id}
            onSelect={setSelectedNode}
            isDark={isDark}
          />
        ))}

        <GoldenDustCloud />

        <Stars radius={130} depth={60} count={isDark ? 2500 : 800} factor={4} saturation={0.8} fade speed={0.8} />

        <OrbitControls
          enablePan={true}
          enableZoom={true}
          maxDistance={160}
          minDistance={12}
          autoRotate
          autoRotateSpeed={0.5}
        />
      </Canvas>

      {/* Node Inspector Card */}
      {selectedNode && (
        <framerMotion.div
          key={selectedNode.id}
          initial={{ opacity: 0, x: -20, scale: 0.95 }}
          animate={{ opacity: 1, x: 0, scale: 1 }}
          transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
          className="absolute top-24 left-6 sm:left-28 z-30 max-w-xs"
          style={{
            background: cardBg,
            border: `1px solid ${cardBorder}`,
            borderRadius: "18px",
            padding: "20px",
            backdropFilter: "blur(20px)",
            boxShadow: cardShadow,
          }}
        >
          <div className="flex items-center justify-between mb-3">
            <span
              className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold uppercase tracking-widest text-black"
              style={{ background: `linear-gradient(90deg, ${selectedNode.color}, ${selectedNode.emissive})` }}
            >
              {selectedNode.category}
            </span>
            <span className="font-mono text-[10px]" style={{ color: isDark ? "rgba(255,165,0,0.5)" : "rgba(160,80,0,0.5)" }}>
              #{selectedNode.id}
            </span>
          </div>

          <h3 className="font-display text-sm font-bold mb-2" style={{ color: isDark ? "#FFD700" : "#92400E" }}>
            {selectedNode.label}
          </h3>
          <p className="text-xs leading-relaxed font-mono mb-3" style={{ color: isDark ? "rgba(255,180,80,0.8)" : "rgba(120,60,0,0.8)" }}>
            {selectedNode.detail}
          </p>

          <div className="flex items-center justify-between text-[10px] font-mono font-semibold" style={{ color: isDark ? "#FF8C00" : "#B45309" }}>
            <span>⬡ Qdrant Vector Indexed</span>
            <span>1,024-dim</span>
          </div>

          <div className="mt-2 h-1 rounded-full overflow-hidden" style={{ background: isDark ? "rgba(255,100,0,0.15)" : "rgba(200,100,0,0.1)" }}>
            <framerMotion.div
              className="h-full rounded-full"
              style={{ background: `linear-gradient(90deg, ${selectedNode.emissive}, ${selectedNode.color})` }}
              initial={{ width: 0 }}
              animate={{ width: "82%" }}
              transition={{ duration: 0.8, ease: "easeOut" }}
            />
          </div>
          <p className="text-[9px] font-mono mt-1" style={{ color: isDark ? "rgba(255,150,0,0.5)" : "rgba(160,80,0,0.4)" }}>
            Vector similarity: 0.82
          </p>
        </framerMotion.div>
      )}

      {/* Category Legend */}
      <framerMotion.div
        className="absolute bottom-8 right-6 sm:right-8 z-20 flex flex-col gap-1.5"
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.4 }}
      >
        {[
          { label: "Recipe SOPs", color: "#FFD700" },
          { label: "Suppliers", color: "#FF7F00" },
          { label: "POS / Delivery", color: "#FF6A00" },
          { label: "Customer AI", color: "#FFB300" },
          { label: "Operations", color: "#FF9500" },
        ].map((c) => (
          <div key={c.label} className="flex items-center gap-2">
            <div className="w-2.5 h-2.5 rounded-full shadow-lg" style={{ backgroundColor: c.color, boxShadow: `0 0 6px ${c.color}` }} />
            <span className="font-mono text-[10px]" style={{ color: isDark ? "rgba(255,180,80,0.7)" : "rgba(120,60,0,0.7)" }}>
              {c.label}
            </span>
          </div>
        ))}
      </framerMotion.div>

      {/* Bottom status pill */}
      <framerMotion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2 z-20 flex items-center gap-3 px-5 py-2.5 rounded-full font-mono text-xs"
        style={{
          background: pillBg,
          border: `1px solid ${pillBorder}`,
          backdropFilter: "blur(16px)",
          boxShadow: "0 4px 24px rgba(200,100,0,0.12)",
        }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <span className="relative flex h-2 w-2">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full opacity-75" style={{ backgroundColor: "#FF8C00" }} />
          <span className="relative inline-flex h-2 w-2 rounded-full" style={{ backgroundColor: "#FFB300" }} />
        </span>
        <span className="tracking-widest uppercase font-semibold" style={{ color: pillTextColor }}>
          Golden Memory Vault Active
        </span>
        <span style={{ color: pillSubColor }}>|</span>
        <span style={{ color: pillSubColor }}>Click any node to inspect</span>
      </framerMotion.div>
    </div>
  );
}
