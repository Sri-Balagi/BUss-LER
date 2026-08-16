"use client";

import { useCallback, useState, useEffect } from "react";
import {
  ReactFlow,
  useNodesState,
  useEdgesState,
  Handle,
  Position,
  NodeProps,
  addEdge,
  Connection,
  EdgeProps,
  getBezierPath,
  MarkerType,
  Background,
  BackgroundVariant,
  Controls,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { motion, AnimatePresence } from "framer-motion";

// ─── Types ────────────────────────────────────────────────────────────────────
type ND = {
  label: string;
  sub?: string;
  detail?: string;
  metrics?: { v: string; l: string }[];
  color: string;
  accent: string;
  textColor: string;
  icon: string;
  level: number;
  badge?: string;
};

// ─── Palette ──────────────────────────────────────────────────────────────────
const P = {
  root:  { color: "#7C3AED", accent: "#A855F7", textColor: "#fff" },
  rec:   { color: "#D97706", accent: "#F59E0B", textColor: "#fff" },
  sup:   { color: "#059669", accent: "#10B981", textColor: "#fff" },
  pos:   { color: "#2563EB", accent: "#3B82F6", textColor: "#fff" },
  cust:  { color: "#DB2777", accent: "#EC4899", textColor: "#fff" },
  ops:   { color: "#DC2626", accent: "#EF4444", textColor: "#fff" },
};

// ─── Custom gradient bezier edge ─────────────────────────────────────────────
function KGEdge({ sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition, data }: EdgeProps) {
  const d = data as { color: string };
  const [edgePath] = getBezierPath({ sourceX, sourceY, sourcePosition, targetX, targetY, targetPosition, curvature: 0.35 });
  const uid = `eg-${Math.abs(Math.round(sourceX * 10 + targetY * 10))}`;
  return (
    <>
      <defs>
        <linearGradient id={uid} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor={d.color} stopOpacity="1" />
          <stop offset="100%" stopColor={d.color} stopOpacity="0.3" />
        </linearGradient>
      </defs>
      {/* glow */}
      <path d={edgePath} stroke={d.color} strokeWidth={6} fill="none" opacity={0.08} />
      {/* main line */}
      <path d={edgePath} stroke={`url(#${uid})`} strokeWidth={2} fill="none" opacity={0.85} />
    </>
  );
}

// ─── ROOT NODE ────────────────────────────────────────────────────────────────
function RootNode({ data, selected }: NodeProps) {
  const d = data as unknown as ND;
  return (
    <motion.div
      initial={{ scale: 0.6, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      style={{
        background: `linear-gradient(135deg, ${d.color} 0%, ${d.accent} 100%)`,
        borderRadius: 24,
        padding: "20px 28px",
        minWidth: 260,
        textAlign: "center",
        boxShadow: `0 0 0 8px ${d.color}1A, 0 20px 60px ${d.color}50, 0 8px 24px rgba(0,0,0,0.18)`,
        border: selected ? "2px solid white" : "2px solid transparent",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* inner shine */}
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: "50%", background: "rgba(255,255,255,0.15)", borderRadius: "24px 24px 60% 60%" }} />
      <Handle type="source" position={Position.Bottom} style={{ background: "#fff", border: `2px solid ${d.color}`, width: 12, height: 12, bottom: -7 }} />
      <div style={{ fontSize: 26, marginBottom: 8, position: "relative" }}>{d.icon}</div>
      <div style={{ fontFamily: "'Inter', monospace", fontSize: 16, fontWeight: 900, color: "#fff", letterSpacing: "-0.02em", position: "relative" }}>
        {d.label}
      </div>
      {d.sub && (
        <div style={{ fontFamily: "monospace", fontSize: 10.5, color: "rgba(255,255,255,0.75)", marginTop: 6, lineHeight: 1.6, position: "relative" }}>
          {d.sub}
        </div>
      )}
      {d.metrics && (
        <div style={{ display: "flex", gap: 8, justifyContent: "center", marginTop: 12, flexWrap: "wrap", position: "relative" }}>
          {d.metrics.map((m) => (
            <div key={m.l} style={{
              background: "rgba(255,255,255,0.2)",
              backdropFilter: "blur(8px)",
              borderRadius: 8,
              padding: "4px 10px",
              fontFamily: "monospace", fontSize: 11,
            }}>
              <span style={{ color: "rgba(255,255,255,0.65)", fontSize: 9 }}>{m.l} </span>
              <strong style={{ color: "#fff" }}>{m.v}</strong>
            </div>
          ))}
        </div>
      )}
    </motion.div>
  );
}

// ─── DOMAIN NODE ──────────────────────────────────────────────────────────────
function DomainNode({ data, selected }: NodeProps) {
  const d = data as unknown as ND;
  return (
    <motion.div
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.38, ease: [0.16, 1, 0.3, 1] }}
      style={{
        background: `linear-gradient(135deg, ${d.color} 0%, ${d.accent} 100%)`,
        borderRadius: 18,
        padding: "14px 18px",
        minWidth: 185,
        boxShadow: selected
          ? `0 0 0 3px white, 0 0 0 5px ${d.color}, 0 16px 40px ${d.color}55`
          : `0 12px 36px ${d.color}40, 0 4px 12px rgba(0,0,0,0.12)`,
        position: "relative",
        overflow: "hidden",
        transition: "all 0.2s ease",
      }}
    >
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: "45%", background: "rgba(255,255,255,0.12)", borderRadius: "18px 18px 60% 60%" }} />
      <Handle type="target" position={Position.Top} style={{ background: "#fff", border: `2px solid ${d.color}`, width: 10, height: 10, top: -6 }} />
      <Handle type="source" position={Position.Bottom} style={{ background: "#fff", border: `2px solid ${d.color}`, width: 10, height: 10, bottom: -6 }} />
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6, position: "relative" }}>
        <span style={{ fontSize: 15 }}>{d.icon}</span>
        {d.badge && (
          <span style={{
            background: "rgba(255,255,255,0.25)",
            color: "#fff", borderRadius: 6, padding: "1px 8px",
            fontSize: 9, fontFamily: "monospace", fontWeight: 800, letterSpacing: "0.1em",
          }}>{d.badge}</span>
        )}
      </div>
      <div style={{ fontFamily: "'Inter', monospace", fontSize: 13, fontWeight: 800, color: "#fff", lineHeight: 1.3, position: "relative" }}>{d.label}</div>
      {d.sub && <div style={{ fontFamily: "monospace", fontSize: 10, color: "rgba(255,255,255,0.72)", marginTop: 4, lineHeight: 1.5, position: "relative" }}>{d.sub}</div>}
    </motion.div>
  );
}

// ─── LEAF NODE ────────────────────────────────────────────────────────────────
function LeafNode({ data, selected }: NodeProps) {
  const d = data as unknown as ND;
  return (
    <motion.div
      initial={{ y: 14, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
      style={{
        background: "#fff",
        border: `2px solid ${selected ? d.color : d.color + "35"}`,
        borderTop: `4px solid ${d.color}`,
        borderRadius: 14,
        padding: "12px 14px",
        minWidth: 172,
        maxWidth: 215,
        boxShadow: selected
          ? `0 0 0 3px ${d.color}20, 0 12px 32px rgba(0,0,0,0.12)`
          : `0 4px 20px rgba(0,0,0,0.07), 0 1px 4px rgba(0,0,0,0.04)`,
        transition: "all 0.2s ease",
      }}
    >
      <Handle type="target" position={Position.Top} style={{ background: d.color, border: "2px solid white", width: 8, height: 8, top: -5 }} />
      <div style={{ fontFamily: "monospace", fontSize: 11.5, fontWeight: 800, color: "#111", lineHeight: 1.35, marginBottom: 4 }}>{d.label}</div>
      {d.sub && <div style={{ fontFamily: "monospace", fontSize: 9.5, color: "#6B7280", lineHeight: 1.55, marginBottom: 4 }}>{d.sub}</div>}
      {d.detail && (
        <div style={{
          fontFamily: "monospace", fontSize: 9, fontWeight: 600,
          color: d.color, marginTop: 3,
          background: `${d.color}0F`, borderRadius: 5, padding: "2px 6px",
          display: "inline-block",
        }}>→ {d.detail}</div>
      )}
      {d.metrics && (
        <div style={{ display: "flex", gap: 5, marginTop: 8, flexWrap: "wrap" }}>
          {d.metrics.map((m) => (
            <div key={m.l} style={{
              background: `${d.color}12`, border: `1px solid ${d.color}30`,
              borderRadius: 6, padding: "2px 7px",
              fontFamily: "monospace", fontSize: 9.5, fontWeight: 700, color: d.color,
            }}>{m.v}</div>
          ))}
        </div>
      )}
    </motion.div>
  );
}

const nodeTypes = { root: RootNode, domain: DomainNode, leaf: LeafNode };
const edgeTypes = { kg: KGEdge };

// ─── Layout ────────────────────────────────────────────────────────────────────
const ROW = 180;
const initialNodes = [
  // ROOT
  { id: "root", type: "root", position: { x: 940, y: 0 },
    data: { ...P.root, icon: "🏨", level: 0,
      label: "Hotel Balagi Bhavan",
      sub: "Enterprise Knowledge Graph · 5 Domains",
      metrics: [{ l: "Staff", v: "45" }, { l: "Halls", v: "4" }, { l: "Menu", v: "14 items" }],
    },
  },

  // DOMAIN HUBS
  { id: "rec",  type: "domain", position: { x: 60,   y: ROW },
    data: { ...P.rec,  icon: "🍛", level: 1, badge: "KITCHEN",  label: "Culinary Recipes",       sub: "Thali SOPs · Breakfast · Specials" } },
  { id: "sup",  type: "domain", position: { x: 500,  y: ROW },
    data: { ...P.sup,  icon: "🚚", level: 1, badge: "SUPPLY",   label: "Vendor & SLA Network",   sub: "3 suppliers · Daily deliveries" } },
  { id: "pos",  type: "domain", position: { x: 940,  y: ROW },
    data: { ...P.pos,  icon: "📱", level: 1, badge: "CHANNELS", label: "POS & Delivery",         sub: "Swiggy · Zomato · Counter POS" } },
  { id: "cust", type: "domain", position: { x: 1380, y: ROW },
    data: { ...P.cust, icon: "💬", level: 1, badge: "CX AI",    label: "Customer Experience",    sub: "WhatsApp AI · Maps · Events" } },
  { id: "ops",  type: "domain", position: { x: 1820, y: ROW },
    data: { ...P.ops,  icon: "⚙️", level: 1, badge: "OPS",      label: "Staff & Operations",     sub: "45 staff · 4 halls · Audit" } },

  // CULINARY LEAVES
  { id: "r1", type: "leaf", position: { x: -60,  y: ROW * 2 },
    data: { ...P.rec, level: 2, label: "South Indian Thali SOP",
      sub: "200-person batch · 9:30 AM trigger",
      detail: "Sambar, Rasam, Kuzhambu, Payasam",
      metrics: [{ l: "", v: "200 pax" }, { l: "", v: "₹82/plate" }],
    },
  },
  { id: "r2", type: "leaf", position: { x: 150,  y: ROW * 2 },
    data: { ...P.rec, level: 2, label: "Breakfast Menu",
      sub: "7–10 AM · Idli, Dosa, Pongal, Upma",
      detail: "150 plates avg · 50/hr",
    },
  },
  { id: "r3", type: "leaf", position: { x: 350,  y: ROW * 2 },
    data: { ...P.rec, level: 2, label: "Filter Coffee SOP",
      sub: "5:45 AM · Chicory 30% · 300 cups",
      detail: "6-min boil trigger",
      metrics: [{ l: "", v: "300 cups/day" }],
    },
  },

  // SUPPLIER LEAVES
  { id: "s1", type: "leaf", position: { x: 400,  y: ROW * 2 },
    data: { ...P.sup, level: 2, label: "Aavin Milk 150L SLA",
      sub: "05:30 AM · Fat ≥ 3.5%",
      detail: "Reject if after 06:00 AM",
      metrics: [{ l: "", v: "150 L/day" }],
    },
  },
  { id: "s2", type: "leaf", position: { x: 590,  y: ROW * 2 },
    data: { ...P.sup, level: 2, label: "Agmark Ghee 45 kg",
      sub: "Monthly bulk · Alert at 15% stock",
      detail: "1.5 kg/day avg consumption",
    },
  },
  { id: "s3", type: "leaf", position: { x: 780,  y: ROW * 2 },
    data: { ...P.sup, level: 2, label: "Koyambedu Veggie",
      sub: "Daily auction feed · 6:00 AM",
      detail: "Auto reorder on 3-day avg",
    },
  },

  // POS LEAVES
  { id: "p1", type: "leaf", position: { x: 820,  y: ROW * 2 },
    data: { ...P.pos, level: 2, label: "Swiggy Live Stream",
      sub: "< 12-min prep SLA · ONDC",
      detail: "80 orders/day peak",
      metrics: [{ l: "", v: "SLA: 12 min" }],
    },
  },
  { id: "p2", type: "leaf", position: { x: 1010, y: ROW * 2 },
    data: { ...P.pos, level: 2, label: "Zomato Delivery",
      sub: "3.2 km radius · ETA optimizer",
      detail: "Auto-pause on 0 riders",
    },
  },
  { id: "p3", type: "leaf", position: { x: 1200, y: ROW * 2 },
    data: { ...P.pos, level: 2, label: "Pine Labs POS #4",
      sub: "UPI + Cash + Card",
      detail: "₹42K avg daily turnover",
      metrics: [{ l: "", v: "3 modes" }],
    },
  },

  // CUSTOMER LEAVES
  { id: "c1", type: "leaf", position: { x: 1270, y: ROW * 2 },
    data: { ...P.cust, level: 2, label: "WhatsApp AI Bot",
      sub: "Tamil + Hindi · < 2-min SLA",
      detail: "Auto-resolution engine",
      metrics: [{ l: "", v: "SLA: 2 min" }],
    },
  },
  { id: "c2", type: "leaf", position: { x: 1460, y: ROW * 2 },
    data: { ...P.cust, level: 2, label: "Google Maps 4.8 ★",
      sub: "4-branch rating aggregator",
      detail: "Auto-reply to < 3★ reviews",
    },
  },
  { id: "c3", type: "leaf", position: { x: 1650, y: ROW * 2 },
    data: { ...P.cust, level: 2, label: "Banquet Reservations",
      sub: "120-seat · 3-day advance min",
      detail: "Catering config builder",
    },
  },

  // OPS LEAVES
  { id: "o1", type: "leaf", position: { x: 1710, y: ROW * 2 },
    data: { ...P.ops, level: 2, label: "Shift Roster Manager",
      sub: "3 shifts · Conflict detection",
      detail: "45 staff · biometric sync",
      metrics: [{ l: "", v: "3 shifts/day" }],
    },
  },
  { id: "o2", type: "leaf", position: { x: 1910, y: ROW * 2 },
    data: { ...P.ops, level: 2, label: "FSSAI Hygiene Audit",
      sub: "23 checkpoints · AM + PM",
      detail: "SMS alert on any fail",
    },
  },
];

// ─── Edges ────────────────────────────────────────────────────────────────────
const mk = (id: string, s: string, t: string, color: string, animated = false) => ({
  id, source: s, target: t, type: "kg", animated,
  markerEnd: { type: MarkerType.ArrowClosed, width: 16, height: 16, color },
  data: { color },
  style: { stroke: color },
});

const initialEdges = [
  mk("r-rec",  "root", "rec",  P.rec.color,  true),
  mk("r-sup",  "root", "sup",  P.sup.color,  true),
  mk("r-pos",  "root", "pos",  P.pos.color,  true),
  mk("r-cust", "root", "cust", P.cust.color, true),
  mk("r-ops",  "root", "ops",  P.ops.color,  true),
  mk("r-r1", "rec", "r1", P.rec.color),
  mk("r-r2", "rec", "r2", P.rec.color),
  mk("r-r3", "rec", "r3", P.rec.color),
  mk("s-s1", "sup", "s1", P.sup.color),
  mk("s-s2", "sup", "s2", P.sup.color),
  mk("s-s3", "sup", "s3", P.sup.color),
  mk("p-p1", "pos", "p1", P.pos.color),
  mk("p-p2", "pos", "p2", P.pos.color),
  mk("p-p3", "pos", "p3", P.pos.color),
  mk("c-c1", "cust", "c1", P.cust.color),
  mk("c-c2", "cust", "c2", P.cust.color),
  mk("c-c3", "cust", "c3", P.cust.color),
  mk("o-o1", "ops", "o1", P.ops.color),
  mk("o-o2", "ops", "o2", P.ops.color),
];

// ─── Main export ──────────────────────────────────────────────────────────────
export function KnowledgeUniverseVisualizer() {
  const [isDark, setIsDark] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>("root");

  useEffect(() => {
    const check = () => setIsDark(document.documentElement.classList.contains("dark"));
    check();
    const obs = new MutationObserver(check);
    obs.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
    return () => obs.disconnect();
  }, []);

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const selNode = nodes.find((n) => n.id === selectedId);
  const selData = selNode?.data as unknown as ND | undefined;

  const bg     = isDark ? "#0D0B14" : "#ffffff";
  const dotCol = isDark ? "rgba(255,255,255,0.04)" : "rgba(0,0,0,0.05)";
  const panBg  = isDark ? "rgba(15,12,25,0.97)" : "rgba(255,255,255,0.98)";
  const panBdr = (c: string) => isDark ? `${c}55` : `${c}55`;
  const subTxt = isDark ? "rgba(200,180,240,0.5)" : "#9CA3AF";
  const legBg  = isDark ? "rgba(15,12,25,0.95)" : "rgba(255,255,255,0.97)";
  const legBdr = isDark ? "rgba(120,80,200,0.18)" : "rgba(0,0,0,0.08)";

  return (
    <div className="w-full h-full absolute inset-0">
      <ReactFlow
        nodes={nodes.map((n) => ({ ...n, selected: n.id === selectedId }))}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={(_, node) => setSelectedId(node.id)}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        fitViewOptions={{ padding: 0.12 }}
        proOptions={{ hideAttribution: true }}
        style={{ background: bg }}
      >
        <Background color={dotCol} gap={24} size={1} variant={BackgroundVariant.Dots} />
        <Controls style={{
          background: panBg, border: `1px solid ${legBdr}`,
          borderRadius: 12, boxShadow: "0 2px 12px rgba(0,0,0,0.06)",
        }} />
      </ReactFlow>

      {/* ── Inspector ──────────────────────────────────────────────────────────── */}
      <AnimatePresence mode="wait">
        {selNode && selData && (
          <motion.div
            key={selNode.id}
            initial={{ opacity: 0, y: 12, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.97 }}
            transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="absolute top-6 left-6 z-30"
            style={{
              background: panBg,
              border: `1.5px solid ${panBdr(selData.color)}`,
              borderTop: `4px solid ${selData.color}`,
              borderRadius: 18,
              padding: 20,
              backdropFilter: "blur(24px)",
              boxShadow: `0 16px 48px rgba(0,0,0,0.1), 0 0 0 1px ${selData.color}18`,
              minWidth: 260, maxWidth: 300,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
              <span style={{
                background: `linear-gradient(135deg, ${selData.color}, ${selData.accent})`,
                color: "#fff", borderRadius: 7, padding: "2px 10px",
                fontFamily: "monospace", fontSize: 9, fontWeight: 800, letterSpacing: "0.1em",
              }}>
                {selData.badge ?? `LEVEL ${selData.level}`}
              </span>
              <span style={{ fontFamily: "monospace", fontSize: 9, color: subTxt }}>#{selNode.id}</span>
            </div>

            <div style={{ fontSize: 20, marginBottom: 6 }}>{selData.icon}</div>
            <div style={{ fontFamily: "monospace", fontSize: 14, fontWeight: 900, color: selData.color, marginBottom: 4, lineHeight: 1.3 }}>
              {selData.label}
            </div>
            {selData.sub && (
              <div style={{ fontFamily: "monospace", fontSize: 10.5, color: isDark ? "rgba(200,180,240,0.7)" : "#6B7280", lineHeight: 1.6, marginBottom: 5 }}>
                {selData.sub}
              </div>
            )}
            {selData.detail && (
              <div style={{
                fontFamily: "monospace", fontSize: 10, color: selData.color, fontWeight: 700,
                background: `${selData.color}10`, borderRadius: 7, padding: "4px 10px",
                marginBottom: 8, display: "inline-block",
              }}>
                → {selData.detail}
              </div>
            )}
            {selData.metrics && selData.metrics.length > 0 && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 8 }}>
                {selData.metrics.map((m) => (
                  <span key={m.l + m.v} style={{
                    background: `${selData.color}18`, border: `1px solid ${selData.color}35`,
                    borderRadius: 8, padding: "3px 10px",
                    fontFamily: "monospace", fontSize: 10, color: selData.color, fontWeight: 700,
                  }}>{m.v}</span>
                ))}
              </div>
            )}

            {/* depth bar */}
            <div style={{ marginTop: 14 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
                <span style={{ fontFamily: "monospace", fontSize: 9, color: subTxt }}>Tree Depth</span>
                <span style={{ fontFamily: "monospace", fontSize: 9, color: selData.color, fontWeight: 700 }}>
                  {selData.level === 0 ? "Root" : selData.level === 1 ? "Domain" : "Detail"}
                </span>
              </div>
              <div style={{ height: 4, borderRadius: 2, background: isDark ? "rgba(255,255,255,0.06)" : "#F3F4F6" }}>
                <motion.div
                  style={{ height: "100%", borderRadius: 2, background: `linear-gradient(90deg, ${selData.color}, ${selData.accent})` }}
                  initial={{ width: 0 }}
                  animate={{ width: `${((selData.level + 1) / 3) * 100}%` }}
                  transition={{ duration: 0.5, ease: "easeOut" }}
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Legend ──────────────────────────────────────────────────────────────── */}
      <motion.div
        className="absolute bottom-6 right-6 z-20"
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        style={{
          background: legBg, border: `1px solid ${legBdr}`,
          borderRadius: 16, padding: "14px 18px",
          backdropFilter: "blur(20px)",
          boxShadow: "0 8px 32px rgba(0,0,0,0.06)",
          display: "flex", flexDirection: "column", gap: 8,
        }}
      >
        <div style={{ fontFamily: "monospace", fontSize: 9, fontWeight: 800, letterSpacing: "0.12em", color: subTxt, marginBottom: 2 }}>
          DOMAINS
        </div>
        {[
          { label: "Culinary",      ...P.rec  },
          { label: "Vendor & SLA", ...P.sup  },
          { label: "POS / Delivery",...P.pos  },
          { label: "Customer CX",  ...P.cust },
          { label: "Operations",   ...P.ops  },
        ].map((d) => (
          <div key={d.label} style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{
              width: 28, height: 8, borderRadius: 4,
              background: `linear-gradient(90deg, ${d.color}, ${d.accent})`,
              boxShadow: `0 0 6px ${d.color}60`,
            }} />
            <span style={{ fontFamily: "monospace", fontSize: 10.5, color: isDark ? "rgba(210,200,240,0.7)" : "#374151", fontWeight: 600 }}>
              {d.label}
            </span>
          </div>
        ))}
      </motion.div>

      {/* ── Bottom pill ──────────────────────────────────────────────────────────── */}
      <motion.div
        className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20 flex items-center gap-3 px-6 py-3 rounded-full"
        style={{
          background: legBg, border: `1px solid ${legBdr}`,
          backdropFilter: "blur(16px)",
          boxShadow: "0 8px 32px rgba(0,0,0,0.08)",
          fontFamily: "monospace", fontSize: 11,
        }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.35 }}
      >
        <span className="relative flex h-2.5 w-2.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full opacity-60" style={{ backgroundColor: P.root.color }} />
          <span className="relative inline-flex h-2.5 w-2.5 rounded-full" style={{ backgroundColor: P.root.color }} />
        </span>
        <span style={{ fontWeight: 800, letterSpacing: "0.06em", textTransform: "uppercase", color: isDark ? "#A78BFA" : P.root.color }}>
          Decision Knowledge Tree
        </span>
        <span style={{ color: subTxt }}>·</span>
        <span style={{ color: subTxt }}>Click to inspect · Scroll to zoom</span>
      </motion.div>
    </div>
  );
}
