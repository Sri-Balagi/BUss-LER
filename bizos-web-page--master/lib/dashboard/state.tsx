"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useReducer,
} from "react";

// ---------- Types ----------

export type StageKey =
  | "research"
  | "memory"
  | "knowledge"
  | "reasoning"
  | "decision"
  | "approval"
  | "execution";

export const STAGES: { key: StageKey; label: string }[] = [
  { key: "research", label: "Research" },
  { key: "memory", label: "Memory" },
  { key: "knowledge", label: "Knowledge" },
  { key: "reasoning", label: "Reasoning" },
  { key: "decision", label: "Decision" },
  { key: "approval", label: "Approval" },
  { key: "execution", label: "Execution" },
];

export type AgentStatus = "thinking" | "executing" | "blocked" | "idle";

export type Agent = {
  id: string;
  name: string;
  role: string;
  stage: StageKey;
  status: AgentStatus;
  confidence: number; // 0-1
};

export type MemoryEvent = {
  id: string;
  label: string;
  kind: "write" | "retrieve";
  ts: number;
  x: number;
  y: number;
};

export type KnowledgeNode = {
  id: string;
  label: string;
  group: "policy" | "product" | "customer" | "runbook";
  x: number;
  y: number;
};

export type Decision = {
  id: string;
  title: string;
  reasoning: string;
  confidence: number;
  status: "pending" | "approved" | "rejected";
  ts: number;
};

export type Goal = {
  id: string;
  label: string;
  progress: number;
  children?: Goal[];
};

export type AuditEntry = {
  id: string;
  ts: number;
  type: "agent" | "memory" | "decision" | "infra";
  text: string;
};

export type Infra = {
  cpu: number;
  memory: number;
  queueDepth: number;
  workers: number;
  maxWorkers: number;
};

export type CognitiveState = {
  tick: number;
  stageCounts: Record<StageKey, number>;
  agents: Agent[];
  memoryEvents: MemoryEvent[];
  knowledgeNodes: KnowledgeNode[];
  knowledgeEdges: [string, string][];
  activeEdge: number;
  decisions: Decision[];
  goals: Goal[];
  infra: Infra;
  auditLog: AuditEntry[];
  selectedStage: StageKey | null;
};

// ---------- Seed data ----------

const AGENT_SEED: Omit<Agent, "stage" | "status" | "confidence">[] = [
  { id: "a1", name: "Atlas", role: "Research agent" },
  { id: "a2", name: "Vega", role: "Memory curator" },
  { id: "a3", name: "Orin", role: "Knowledge retriever" },
  { id: "a4", name: "Iris", role: "Reasoning agent" },
  { id: "a5", name: "Nova", role: "Decision agent" },
  { id: "a6", name: "Halo", role: "Approval router" },
  { id: "a7", name: "Kai", role: "Execution agent" },
  { id: "a8", name: "Sable", role: "Research agent" },
];

const KNOWLEDGE_NODE_SEED: Omit<KnowledgeNode, "x" | "y">[] = [
  { id: "k1", label: "Aavin Milk & Ghee SLA", group: "policy" },
  { id: "k2", label: "South Indian Thali Recipe Standard", group: "product" },
  { id: "k3", label: "Kitchen Shift & Roster Runbook", group: "runbook" },
  { id: "k4", label: "FSSAI Food Safety Protocol", group: "policy" },
  { id: "k5", label: "Table 12 VIP Guest Profile", group: "customer" },
  { id: "k6", label: "Swiggy & Zomato POS API", group: "product" },
  { id: "k7", label: "Banquet Hall A Escalation SOP", group: "runbook" },
  { id: "k8", label: "Koyambedu Fresh Vegetables", group: "customer" },
];

const KNOWLEDGE_EDGE_SEED: [string, string][] = [
  ["k1", "k4"],
  ["k1", "k7"],
  ["k2", "k6"],
  ["k3", "k7"],
  ["k5", "k8"],
  ["k4", "k8"],
  ["k2", "k5"],
  ["k6", "k3"],
];

function ringPosition(i: number, total: number, cx: number, cy: number, r: number) {
  const angle = (i / total) * Math.PI * 2 - Math.PI / 2;
  return { x: cx + Math.cos(angle) * r, y: cy + Math.sin(angle) * r };
}

function seedState(): CognitiveState {
  const stageCounts: Record<StageKey, number> = {
    research: 6,
    memory: 4,
    knowledge: 5,
    reasoning: 3,
    decision: 2,
    approval: 2,
    execution: 4,
  };

  const agents: Agent[] = AGENT_SEED.map((a, i) => ({
    ...a,
    stage: STAGES[i % STAGES.length].key,
    status: (["thinking", "executing", "idle"] as AgentStatus[])[i % 3],
    confidence: 0.55 + ((i * 37) % 40) / 100,
  }));

  const knowledgeNodes: KnowledgeNode[] = KNOWLEDGE_NODE_SEED.map((n, i) => ({
    ...n,
    ...ringPosition(i, KNOWLEDGE_NODE_SEED.length, 150, 130, 100),
  }));

  const decisions: Decision[] = [
    {
      id: "d1",
      title: "Auto-Reorder 150L Aavin Milk & 45kg Ghee",
      reasoning: "Stock dropped below 15% threshold ahead of Friday dinner service peak.",
      confidence: 0.96,
      status: "pending",
      ts: Date.now() - 1000 * 60 * 4,
    },
    {
      id: "d2",
      title: "Approve Banquet Hall A Menu (Dr. Radhakrishnan — 65 Guests)",
      reasoning: "Mini Tiffin + Sweet combo verified with Kitchen Head chef Chef Subbu.",
      confidence: 0.92,
      status: "pending",
      ts: Date.now() - 1000 * 60 * 11,
    },
    {
      id: "d3",
      title: "Swiggy POS Order Batching Auto-Compensation Triggered",
      reasoning: "Prep time surpassed 25m during peak hours, ₹50 discount coupon dispatched to customer.",
      confidence: 0.88,
      status: "approved",
      ts: Date.now() - 1000 * 60 * 26,
    },
  ];

  const goals: Goal[] = [
    {
      id: "g1",
      label: "Maintain 100% daily Aavin Milk delivery before 5:00 AM",
      progress: 0.95,
      children: [
        { id: "g1a", label: "Auto-verify dairy temperature log on arrival", progress: 0.98 },
        { id: "g1b", label: "Notify shift manager if delivery delayed by 10 mins", progress: 0.92 },
      ],
    },
    {
      id: "g2",
      label: "Zero customer wait time > 15m for South Indian Thali",
      progress: 0.88,
      children: [
        { id: "g2a", label: "Auto-prep sambar & rasam batches at 11:30 AM", progress: 0.9 },
        { id: "g2b", label: "Batch kitchen display orders during lunch peak", progress: 0.86 },
      ],
    },
    { id: "g3", label: "Banquet Hall A weekend occupancy rate > 90%", progress: 0.92 },
  ];

  const auditLog: AuditEntry[] = [
    { id: "l1", ts: Date.now() - 5000, type: "infra", text: "KDS Kitchen Display server synchronized 4 terminals" },
    { id: "l2", ts: Date.now() - 15000, type: "decision", text: "Swiggy POS surge batching approved by System" },
    { id: "l3", ts: Date.now() - 32000, type: "memory", text: "Recorded Aavin Milk SLA delivery log for Hotel Balagi Bhavan" },
  ];

  return {
    tick: 0,
    stageCounts,
    agents,
    memoryEvents: [],
    knowledgeNodes,
    knowledgeEdges: KNOWLEDGE_EDGE_SEED,
    activeEdge: 0,
    decisions,
    goals,
    infra: { cpu: 0.42, memory: 0.55, queueDepth: 18, workers: 9, maxWorkers: 16 },
    auditLog,
    selectedStage: null,
  };
}

// ---------- Reducer ----------

type Action =
  | { type: "TICK" }
  | { type: "SELECT_STAGE"; stage: StageKey | null }
  | { type: "DECIDE"; id: string; status: "approved" | "rejected" }
  | { type: "TOGGLE_GOAL_NOOP" };

function clamp(n: number, min: number, max: number) {
  return Math.max(min, Math.min(max, n));
}

function reducer(state: CognitiveState, action: Action): CognitiveState {
  switch (action.type) {
    case "SELECT_STAGE":
      return { ...state, selectedStage: action.stage };

    case "DECIDE": {
      const decisions = state.decisions.map((d) =>
        d.id === action.id ? { ...d, status: action.status } : d
      );
      const entry: AuditEntry = {
        id: `l${Date.now()}`,
        ts: Date.now(),
        type: "decision",
        text: `decision ${action.id} ${action.status} by you`,
      };
      return { ...state, decisions, auditLog: [entry, ...state.auditLog].slice(0, 40) };
    }

    case "TICK": {
      const tick = state.tick + 1;

      // Flow one unit forward through the pipeline occasionally
      const stageCounts = { ...state.stageCounts };
      if (tick % 2 === 0) {
        const idx = Math.floor(Math.random() * (STAGES.length - 1));
        const from = STAGES[idx].key;
        const to = STAGES[idx + 1].key;
        if (stageCounts[from] > 1) {
          stageCounts[from] -= 1;
          stageCounts[to] += 1;
        }
      }
      stageCounts.research = clamp(
        stageCounts.research + (Math.random() > 0.6 ? 1 : 0),
        2,
        12
      );

      // Nudge a random agent
      const agents = state.agents.map((a) => ({ ...a }));
      const agentIdx = Math.floor(Math.random() * agents.length);
      const moved = agents[agentIdx];
      const statuses: AgentStatus[] = ["thinking", "executing", "blocked", "idle"];
      if (Math.random() > 0.5) {
        moved.status = statuses[Math.floor(Math.random() * statuses.length)];
      }
      if (Math.random() > 0.6) {
        const curIdx = STAGES.findIndex((s) => s.key === moved.stage);
        const nextIdx = clamp(curIdx + (Math.random() > 0.5 ? 1 : -1), 0, STAGES.length - 1);
        moved.stage = STAGES[nextIdx].key;
      }
      moved.confidence = clamp(moved.confidence + (Math.random() - 0.5) * 0.08, 0.3, 0.99);

      // Occasionally add a memory event (kept short, capped)
      let memoryEvents = state.memoryEvents;
      if (tick % 3 === 0) {
        const labels = [
          "ticket #4821 resolution",
          "customer preference: email only",
          "refund pattern: damaged-in-transit",
          "escalation: billing bug",
          "account renewal date",
        ];
        const ev: MemoryEvent = {
          id: `m${Date.now()}`,
          label: labels[Math.floor(Math.random() * labels.length)],
          kind: Math.random() > 0.5 ? "write" : "retrieve",
          ts: Date.now(),
          x: 20 + Math.random() * 260,
          y: 20 + Math.random() * 200,
        };
        memoryEvents = [ev, ...memoryEvents].slice(0, 14);
      }

      // Cycle the "active" traversal edge in the knowledge graph
      const activeEdge = tick % state.knowledgeEdges.length;

      // Infra jitter
      const infra: Infra = {
        cpu: clamp(state.infra.cpu + (Math.random() - 0.5) * 0.06, 0.15, 0.92),
        memory: clamp(state.infra.memory + (Math.random() - 0.5) * 0.05, 0.2, 0.9),
        queueDepth: Math.max(0, Math.round(state.infra.queueDepth + (Math.random() - 0.5) * 4)),
        workers: clamp(
          Math.round(state.infra.workers + (Math.random() > 0.8 ? (Math.random() > 0.5 ? 1 : -1) : 0)),
          4,
          state.infra.maxWorkers
        ),
        maxWorkers: state.infra.maxWorkers,
      };

      // Audit log — occasional new line describing what just happened
      let auditLog = state.auditLog;
      if (tick % 4 === 0) {
        const lines = [
          `${moved.name} moved to ${moved.stage}`,
          `queue depth now ${infra.queueDepth}`,
          `worker pool at ${infra.workers}/${infra.maxWorkers}`,
          `knowledge traversal: ${state.knowledgeEdges[activeEdge][0]} → ${state.knowledgeEdges[activeEdge][1]}`,
        ];
        const entry: AuditEntry = {
          id: `l${Date.now()}`,
          ts: Date.now(),
          type: tick % 8 === 0 ? "infra" : "agent",
          text: lines[Math.floor(Math.random() * lines.length)],
        };
        auditLog = [entry, ...auditLog].slice(0, 40);
      }

      return {
        ...state,
        tick,
        stageCounts,
        agents,
        memoryEvents,
        activeEdge,
        infra,
        auditLog,
      };
    }

    default:
      return state;
  }
}

// ---------- Context ----------

const StateCtx = createContext<CognitiveState | null>(null);
const DispatchCtx = createContext<React.Dispatch<Action> | null>(null);

export function CognitiveStateProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, undefined, seedState);

  useEffect(() => {
    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const interval = setInterval(() => dispatch({ type: "TICK" }), prefersReduced ? 4000 : 1800);
    return () => clearInterval(interval);
  }, []);

  return (
    <StateCtx.Provider value={state}>
      <DispatchCtx.Provider value={dispatch}>{children}</DispatchCtx.Provider>
    </StateCtx.Provider>
  );
}

export function useCognitiveState() {
  const state = useContext(StateCtx);
  if (!state) throw new Error("useCognitiveState must be used within CognitiveStateProvider");
  return state;
}

export function useCognitiveActions() {
  const dispatch = useContext(DispatchCtx);
  if (!dispatch) throw new Error("useCognitiveActions must be used within CognitiveStateProvider");
  return useMemo(
    () => ({
      selectStage: (stage: StageKey | null) => dispatch({ type: "SELECT_STAGE", stage }),
      decide: (id: string, status: "approved" | "rejected") =>
        dispatch({ type: "DECIDE", id, status }),
    }),
    [dispatch]
  );
}
