"use client";

import { useCallback } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  useNodesState,
  useEdgesState,
  Handle,
  Position,
  NodeProps,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { motion } from "framer-motion";

// Custom Neural Node
function NeuralNode({ data }: NodeProps) {
  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="relative flex items-center justify-center p-4 rounded-xl border border-white/[0.05] bg-deep-space backdrop-blur-xl  group"
    >
      <Handle type="target" position={Position.Top} className="!w-2 !h-2 !bg-cognition-knowledge !border-none" />
      
      <div className="flex flex-col items-center gap-2">
        <div className="w-3 h-3 rounded-full bg-cognition-knowledge  group-hover:scale-125 transition-transform" />
        <span className="font-mono text-xs text-primary">{data.label as string}</span>
      </div>

      <Handle type="source" position={Position.Bottom} className="!w-2 !h-2 !bg-cognition-knowledge !border-none" />
    </motion.div>
  );
}

const nodeTypes = {
  neural: NeuralNode,
};

const initialNodes = [
  { id: "1", type: "neural", position: { x: 250, y: 50 }, data: { label: "Root Knowledge" } },
  { id: "2", type: "neural", position: { x: 100, y: 200 }, data: { label: "Semantic Sub-Graph A" } },
  { id: "3", type: "neural", position: { x: 400, y: 200 }, data: { label: "Semantic Sub-Graph B" } },
  { id: "4", type: "neural", position: { x: 50, y: 350 }, data: { label: "Entity: User Profile" } },
  { id: "5", type: "neural", position: { x: 200, y: 350 }, data: { label: "Entity: Auth Rules" } },
  { id: "6", type: "neural", position: { x: 400, y: 350 }, data: { label: "Entity: Metrics" } },
];

const initialEdges = [
  { id: "e1-2", source: "1", target: "2", animated: true, style: { stroke: "var(--text-primary)", strokeWidth: 2, opacity: 0.5 } },
  { id: "e1-3", source: "1", target: "3", animated: true, style: { stroke: "var(--text-primary)", strokeWidth: 2, opacity: 0.5 } },
  { id: "e2-4", source: "2", target: "4", animated: true, style: { stroke: "var(--text-primary)", strokeWidth: 2, opacity: 0.5 } },
  { id: "e2-5", source: "2", target: "5", animated: true, style: { stroke: "var(--text-primary)", strokeWidth: 2, opacity: 0.5 } },
  { id: "e3-6", source: "3", target: "6", animated: true, style: { stroke: "var(--text-primary)", strokeWidth: 2, opacity: 0.5 } },
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
        className="bg-deep-space"
        proOptions={{ hideAttribution: true }}
      >
        <Background color="rgba(255,255,255,0.05)" gap={40} size={1} />
      </ReactFlow>
    </div>
  );
}
