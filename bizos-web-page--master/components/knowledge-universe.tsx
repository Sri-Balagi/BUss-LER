"use client";

import { useMemo } from "react";
import {
  ReactFlow,
  Background,
  useNodesState,
  useEdgesState,
  Handle,
  Position,
  NodeProps,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { motion } from "framer-motion";
import { Building2, Utensils, Award, ChefHat, Truck, Sparkles, Users2, Coffee } from "lucide-react";

// Color themes mapping boundary color to matching background, border, and text styles in both light and dark mode
const COLOR_STYLES: Record<string, {
  border: string;
  cardBg: string;
  titleText: string;
  mutedText: string;
  badgeBg: string;
  badgeText: string;
  handleBg: string;
  glow: string;
}> = {
  "#0EA5E9": { // Sky Blue (Main Dining Hall)
    border: "border-sky-500 dark:border-sky-400 border-2",
    cardBg: "bg-sky-50/95 dark:bg-sky-950/80 backdrop-blur-xl shadow-md shadow-sky-500/10",
    titleText: "text-sky-950 dark:text-sky-100",
    mutedText: "text-sky-700 dark:text-sky-300",
    badgeBg: "bg-sky-200/80 dark:bg-sky-900/60 border border-sky-400/40 dark:border-sky-700",
    badgeText: "text-sky-900 dark:text-sky-200",
    handleBg: "#0EA5E9",
    glow: "shadow-[0_0_20px_rgba(14,165,233,0.25)]",
  },
  "#A78BFA": { // Violet / Purple (Balagi Mandapam Banquet)
    border: "border-purple-500 dark:border-purple-400 border-2",
    cardBg: "bg-purple-50/95 dark:bg-purple-950/80 backdrop-blur-xl shadow-md shadow-purple-500/10",
    titleText: "text-purple-950 dark:text-purple-100",
    mutedText: "text-purple-700 dark:text-purple-300",
    badgeBg: "bg-purple-200/80 dark:bg-purple-900/60 border border-purple-400/40 dark:border-purple-700",
    badgeText: "text-purple-900 dark:text-purple-200",
    handleBg: "#A78BFA",
    glow: "shadow-[0_0_20px_rgba(167,139,250,0.25)]",
  },
  "#ED7D27": { // Warm Amber Orange (Central Kitchen & Root)
    border: "border-[#ED7D27] border-2",
    cardBg: "bg-orange-50/95 dark:bg-orange-950/80 backdrop-blur-xl shadow-md shadow-orange-500/10",
    titleText: "text-orange-950 dark:text-orange-100",
    mutedText: "text-orange-800 dark:text-orange-300",
    badgeBg: "bg-orange-200/80 dark:bg-orange-900/60 border border-orange-400/40 dark:border-orange-700",
    badgeText: "text-orange-950 dark:text-orange-200",
    handleBg: "#ED7D27",
    glow: "shadow-[0_0_25px_rgba(237,125,39,0.3)]",
  },
  "#10B981": { // Emerald Green (Supply & Inventory)
    border: "border-emerald-500 dark:border-emerald-400 border-2",
    cardBg: "bg-emerald-50/95 dark:bg-emerald-950/80 backdrop-blur-xl shadow-md shadow-emerald-500/10",
    titleText: "text-emerald-950 dark:text-emerald-100",
    mutedText: "text-emerald-700 dark:text-emerald-300",
    badgeBg: "bg-emerald-200/80 dark:bg-emerald-900/60 border border-emerald-400/40 dark:border-emerald-700",
    badgeText: "text-emerald-900 dark:text-emerald-200",
    handleBg: "#10B981",
    glow: "shadow-[0_0_20px_rgba(16,185,129,0.25)]",
  },
};

// Custom Styled Node Component for Hotel Balagi Bhavan Knowledge Tree
function BalagiNode({ data }: NodeProps) {
  const level = (data.level as number) || 1;
  const color = (data.color as string) || "#ED7D27";
  const icon = data.iconName;

  const theme = COLOR_STYLES[color] || COLOR_STYLES["#ED7D27"];

  const IconComponent = useMemo(() => {
    switch (icon) {
      case "hotel": return Building2;
      case "hall": return Users2;
      case "banquet": return Award;
      case "kitchen": return ChefHat;
      case "supply": return Truck;
      case "food": return Utensils;
      case "coffee": return Coffee;
      case "special": return Sparkles;
      default: return Utensils;
    }
  }, [icon]);

  // Root Node (Top Tier — Hotel Balagi Bhavan HQ)
  if (level === 0) {
    return (
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className={`relative px-7 py-5 rounded-2xl ${theme.cardBg} ${theme.border} ${theme.glow} flex flex-col items-center gap-2 min-w-[340px] text-center group cursor-pointer transition-all duration-300`}
      >
        <Handle type="source" position={Position.Bottom} className="!w-3 !h-3 !border-2 !border-white dark:!border-black" style={{ background: theme.handleBg }} />

        <div className={`flex items-center gap-2.5 px-3.5 py-1 rounded-full ${theme.badgeBg}`}>
          <Building2 className="w-4 h-4" style={{ color }} />
          <span className={`font-mono text-[10px] font-bold uppercase tracking-[0.2em] ${theme.badgeText}`}>
            Root Entity · Headquarters
          </span>
        </div>

        <h2 className={`font-display text-xl font-bold tracking-wide ${theme.titleText}`}>
          Hotel Balagi Bhavan
        </h2>
        <p className={`font-mono text-[11px] ${theme.mutedText}`}>
          Central Knowledge Graph · Authentic Indian Restaurant
        </p>

        <div className="flex items-center gap-3 mt-1 pt-2 border-t border-orange-200 dark:border-orange-800/40 w-full justify-center">
          <span className="font-mono text-[10px] font-semibold text-emerald-700 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-950/60 px-2.5 py-0.5 rounded-full border border-emerald-300 dark:border-emerald-700">
            ● Active Operations
          </span>
          <span className={`font-mono text-[10px] ${theme.mutedText}`}>
            312 Sub-entities
          </span>
        </div>
      </motion.div>
    );
  }

  // Tier 1 Nodes (Main Sections / Halls / Kitchen)
  if (level === 1) {
    return (
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className={`relative px-5 py-3.5 rounded-xl ${theme.cardBg} ${theme.border} ${theme.glow} flex flex-col items-start gap-1.5 min-w-[245px] group hover:scale-[1.02] transition-all duration-300`}
      >
        <Handle type="target" position={Position.Top} className="!w-2.5 !h-2.5 !border-none" style={{ background: theme.handleBg }} />
        <Handle type="source" position={Position.Bottom} className="!w-2.5 !h-2.5 !border-none" style={{ background: theme.handleBg }} />

        <div className="flex items-center gap-2 w-full justify-between">
          <div className="flex items-center gap-2">
            <div className={`p-1.5 rounded-lg ${theme.badgeBg}`}>
              <IconComponent className="w-4 h-4" style={{ color }} strokeWidth={2} />
            </div>
            <span className={`font-mono text-[10px] font-bold uppercase tracking-wider ${theme.mutedText}`}>
              {data.category as string}
            </span>
          </div>
          <span className={`font-mono text-[9px] px-2 py-0.5 rounded-full ${theme.badgeBg} ${theme.badgeText} font-bold`}>
            {data.count as string}
          </span>
        </div>

        <span className={`font-display text-sm font-semibold mt-1 ${theme.titleText}`}>
          {data.label as string}
        </span>

        {typeof data.detail === "string" && (
          <span className={`font-mono text-[10.5px] ${theme.mutedText} leading-snug`}>
            {data.detail}
          </span>
        )}
      </motion.div>
    );
  }

  // Tier 2 Nodes (Child Details / Specific Stations / Outlets / Vendors)
  return (
    <motion.div
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className={`relative px-4 py-2.5 rounded-lg ${theme.cardBg} ${theme.border} flex flex-col items-start gap-1 min-w-[190px] max-w-[210px] hover:scale-[1.02] transition-all duration-200`}
    >
      <Handle type="target" position={Position.Top} className="!w-2 !h-2 !border-none" style={{ background: theme.handleBg }} />
      <Handle type="source" position={Position.Bottom} className="!w-2 !h-2 !border-none" style={{ background: theme.handleBg }} />

      <div className="flex items-center gap-1.5">
        <span className="w-2 h-2 rounded-full shrink-0 shadow-sm" style={{ background: color }} />
        <span className={`font-mono text-[9.5px] uppercase tracking-wider font-semibold ${theme.mutedText}`}>
          {data.category as string}
        </span>
      </div>

      <span className={`font-mono text-xs font-semibold leading-snug ${theme.titleText}`}>
        {data.label as string}
      </span>

      {typeof data.status === "string" && (
        <span className={`font-mono text-[9px] font-bold mt-0.5 ${theme.mutedText}`}>
          ✓ {data.status}
        </span>
      )}
    </motion.div>
  );
}

const nodeTypes = {
  balagi: BalagiNode,
};

// Tree-based Node Array specifically mapped for Hotel Balagi Bhavan
const initialNodes = [
  // Tier 0: Root Entity
  {
    id: "root-balagi",
    type: "balagi",
    position: { x: 500, y: 20 },
    data: {
      label: "Hotel Balagi Bhavan",
      level: 0,
      iconName: "hotel",
      color: "#ED7D27",
    },
  },

  // Tier 1: Main Branches / Halls / Operations
  {
    id: "branch-dining",
    type: "balagi",
    position: { x: 30, y: 200 },
    data: {
      label: "Main Dining Hall (AC & Non-AC)",
      category: "Dining Area",
      detail: "120 Seats · Express Tiffin Counter",
      count: "15 Tables",
      color: "#0EA5E9",
      level: 1,
      iconName: "hall",
    },
  },
  {
    id: "branch-banquet",
    type: "balagi",
    position: { x: 340, y: 200 },
    data: {
      label: "Balagi Mandapam (Banquet)",
      category: "Event Hall",
      detail: "250 Pax · Marriage & Catering",
      count: "Hall A & B",
      color: "#A78BFA",
      level: 1,
      iconName: "banquet",
    },
  },
  {
    id: "branch-kitchen",
    type: "balagi",
    position: { x: 650, y: 200 },
    data: {
      label: "Central Kitchen & Tandoor",
      category: "Culinary Core",
      detail: "Chef Venkatesh · Biryani Counters",
      count: "4 Stations",
      color: "#ED7D27",
      level: 1,
      iconName: "kitchen",
    },
  },
  {
    id: "branch-supply",
    type: "balagi",
    position: { x: 960, y: 200 },
    data: {
      label: "Supply & Inventory Pantry",
      category: "Sourcing",
      detail: "Srinivas Traders · Cold Storage",
      count: "22 Vendors",
      color: "#10B981",
      level: 1,
      iconName: "supply",
    },
  },

  // Tier 2: Sub-entities for Dining Hall (Sky Blue Theme)
  {
    id: "sub-family-section",
    type: "balagi",
    position: { x: -20, y: 390 },
    data: {
      label: "Family Section (Tables 1-10)",
      category: "Dining",
      status: "80% Occupied",
      color: "#0EA5E9",
      level: 2,
    },
  },
  {
    id: "sub-tiffin-counter",
    type: "balagi",
    position: { x: 180, y: 390 },
    data: {
      label: "Express Dosa & Coffee Bar",
      category: "Counter",
      status: "High Speed",
      color: "#0EA5E9",
      level: 2,
    },
  },

  // Tier 2: Sub-entities for Banquet Hall (Violet Theme)
  {
    id: "sub-corporate-event",
    type: "balagi",
    position: { x: 340, y: 390 },
    data: {
      label: "Sharma Corporate Lunch",
      category: "Event (80 Pax)",
      status: "Confirmed Sat",
      color: "#A78BFA",
      level: 2,
    },
  },
  {
    id: "sub-puja-catering",
    type: "balagi",
    position: { x: 500, y: 390 },
    data: {
      label: "Puja Thali Catering Order",
      category: "Special Order",
      status: "Prepped",
      color: "#A78BFA",
      level: 2,
    },
  },

  // Tier 2: Sub-entities for Central Kitchen (Orange Theme)
  {
    id: "sub-dum-biryani",
    type: "balagi",
    position: { x: 660, y: 390 },
    data: {
      label: "Hyderabadi Biryani Station",
      category: "Specialty",
      status: "Chef Venkatesh",
      color: "#ED7D27",
      level: 2,
    },
  },
  {
    id: "sub-south-meals",
    type: "balagi",
    position: { x: 820, y: 390 },
    data: {
      label: "South Indian Thali Section",
      category: "Daily Meal",
      status: "Active Batch",
      color: "#ED7D27",
      level: 2,
    },
  },

  // Tier 2: Sub-entities for Supply (Emerald Green Theme)
  {
    id: "sub-srinivas-vendor",
    type: "balagi",
    position: { x: 980, y: 390 },
    data: {
      label: "Srinivas Traders (Rice/Spice)",
      category: "Vendor #1",
      status: "Verified",
      color: "#10B981",
      level: 2,
    },
  },
  {
    id: "sub-dairy-storage",
    type: "balagi",
    position: { x: 1140, y: 390 },
    data: {
      label: "Fresh Dairy & Milk Co-op",
      category: "Daily Supply",
      status: "Delivered 6 AM",
      color: "#10B981",
      level: 2,
    },
  },
];

// Tree Edges linking Hotel Balagi Bhavan to Main Halls and Sub-entities
const initialEdges = [
  // Root to Tier 1 Branches
  {
    id: "e-root-dining",
    source: "root-balagi",
    target: "branch-dining",
    animated: true,
    style: { stroke: "#0EA5E9", strokeWidth: 2.5 },
    markerEnd: { type: MarkerType.ArrowClosed, color: "#0EA5E9" },
  },
  {
    id: "e-root-banquet",
    source: "root-balagi",
    target: "branch-banquet",
    animated: true,
    style: { stroke: "#A78BFA", strokeWidth: 2.5 },
    markerEnd: { type: MarkerType.ArrowClosed, color: "#A78BFA" },
  },
  {
    id: "e-root-kitchen",
    source: "root-balagi",
    target: "branch-kitchen",
    animated: true,
    style: { stroke: "#ED7D27", strokeWidth: 2.5 },
    markerEnd: { type: MarkerType.ArrowClosed, color: "#ED7D27" },
  },
  {
    id: "e-root-supply",
    source: "root-balagi",
    target: "branch-supply",
    animated: true,
    style: { stroke: "#10B981", strokeWidth: 2.5 },
    markerEnd: { type: MarkerType.ArrowClosed, color: "#10B981" },
  },

  // Tier 1 to Tier 2 Children
  {
    id: "e-dining-family",
    source: "branch-dining",
    target: "sub-family-section",
    style: { stroke: "#0EA5E9", strokeWidth: 1.5, strokeDasharray: "4 4" },
  },
  {
    id: "e-dining-tiffin",
    source: "branch-dining",
    target: "sub-tiffin-counter",
    style: { stroke: "#0EA5E9", strokeWidth: 1.5, strokeDasharray: "4 4" },
  },
  {
    id: "e-banquet-sharma",
    source: "branch-banquet",
    target: "sub-corporate-event",
    style: { stroke: "#A78BFA", strokeWidth: 1.5, strokeDasharray: "4 4" },
  },
  {
    id: "e-banquet-puja",
    source: "branch-banquet",
    target: "sub-puja-catering",
    style: { stroke: "#A78BFA", strokeWidth: 1.5, strokeDasharray: "4 4" },
  },
  {
    id: "e-kitchen-biryani",
    source: "branch-kitchen",
    target: "sub-dum-biryani",
    style: { stroke: "#ED7D27", strokeWidth: 1.5, strokeDasharray: "4 4" },
  },
  {
    id: "e-kitchen-meals",
    source: "branch-kitchen",
    target: "sub-south-meals",
    style: { stroke: "#ED7D27", strokeWidth: 1.5, strokeDasharray: "4 4" },
  },
  {
    id: "e-supply-srinivas",
    source: "branch-supply",
    target: "sub-srinivas-vendor",
    style: { stroke: "#10B981", strokeWidth: 1.5, strokeDasharray: "4 4" },
  },
  {
    id: "e-supply-dairy",
    source: "branch-supply",
    target: "sub-dairy-storage",
    style: { stroke: "#10B981", strokeWidth: 1.5, strokeDasharray: "4 4" },
  },
];

export function KnowledgeUniverseVisualizer() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div className="w-full h-full absolute inset-0">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.5}
        maxZoom={1.5}
        className="bg-[#FAF7F2] dark:bg-deep-space transition-colors duration-300"
        proOptions={{ hideAttribution: true }}
      >
        <Background color="rgba(237,125,39,0.12)" gap={36} size={1.2} />
      </ReactFlow>
    </div>
  );
}
