// Appels centralisés vers le backend AgentRelay (FastAPI).
// VITE_API_BASE est défini dans .env.local côté frontend.

export const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined)?.replace(/\/$/, "") ??
  "http://localhost:8000";

export type AgentStatus = "active" | "idle" | "exhausted";
export type EventKind =
  | "BRAIN"
  | "RULES"
  | "ROUTE"
  | "CALL"
  | "LAUNCH"
  | "LIMIT"
  | "QUOTA"
  | "FALLBACK"
  | "HANDOFF"
  | "CHECKPOINT"
  | "DONE"
  | "OK"
  | "ERROR";

export interface AgentInfo {
  name: string;
  description?: string;
  status: AgentStatus;
  quota?: number;
}

export interface Event {
  time: string;
  event: EventKind;
  agent: string;
  detail: string;
}

export interface Decision {
  agent?: string;
  task?: string;
  reason?: string;
  source?: string;
  at?: string;
  done?: boolean;
}

export interface Session {
  goal?: string;
  mode: "manual" | "auto";
  current_agent?: string | null;
  awaiting_user?: boolean;
  done?: boolean;
  started_at?: string;
  steps_count?: number;
}

export interface Status {
  session: Session;
  last_decision?: Decision | null;
  pending_step?: Decision | null;
  agents: AgentInfo[];
  history: Array<Record<string, unknown>>;
  events: Event[];
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "content-type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    throw new Error(`${init?.method ?? "GET"} ${path} → ${res.status}`);
  }
  return (await res.json()) as T;
}

export const api = {
  async getStatus(): Promise<Status> {
    return request<Status>("/api/status");
  },
  async start(goal: string, auto = false) {
    return request<{ ok: boolean; state: unknown }>("/api/start", {
      method: "POST",
      body: JSON.stringify({ goal, auto }),
    });
  },
  async next(output?: string) {
    return request<{ ok: boolean; state: unknown }>("/api/next", {
      method: "POST",
      body: JSON.stringify({ output: output ?? null }),
    });
  },
  async takeover(agent: string, task?: string) {
    return request<{ ok: boolean; state: unknown }>(`/api/takeover/${encodeURIComponent(agent)}`, {
      method: "POST",
      body: JSON.stringify({ task: task ?? null }),
    });
  },
  async setMode(mode: "manual" | "auto") {
    return request<{ ok: boolean; state: unknown }>("/api/mode", {
      method: "POST",
      body: JSON.stringify({ mode }),
    });
  },
  async stop() {
    return request<{ ok: boolean; state: unknown }>("/api/stop", { method: "POST" });
  },
  async health(): Promise<boolean> {
    try {
      await request<{ status: string }>("/api/health");
      return true;
    } catch {
      return false;
    }
  },
};
