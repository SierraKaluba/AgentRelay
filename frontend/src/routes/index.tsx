import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { Bot, CheckCircle2, Clock, Code2, Repeat, Terminal, ArrowRight, Plus, X, Zap, type LucideIcon } from "lucide-react";
import { useAgentRelay } from "@/hooks/use-agentrelay";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "AgentRelay — orchestrateur d'agents de dev" },
      { name: "description", content: "Continuez votre travail quand Claude Code, Codex ou OpenCode atteint son quota." },
    ],
  }),
  component: Dashboard,
});

type Kind = "BRAIN" | "RULES" | "ROUTE" | "CALL" | "LAUNCH" | "LIMIT" | "QUOTA" | "FALLBACK" | "HANDOFF" | "CHECKPOINT" | "DONE" | "OK" | "ERROR";
const kindColor: Record<string, string> = {
  BRAIN: "text-brain", RULES: "text-route", ROUTE: "text-route", CALL: "text-handoff",
  LAUNCH: "text-route", LIMIT: "text-err", QUOTA: "text-err", FALLBACK: "text-route",
  HANDOFF: "text-handoff", CHECKPOINT: "text-brain", DONE: "text-ok", OK: "text-ok", ERROR: "text-err",
};
type AgentId = string;
type AStatus = "active" | "idle" | "exhausted";
const iconFor = (id: string): LucideIcon => {
  const k = id.toLowerCase();
  if (k.includes("claude")) return Terminal;
  if (k.includes("codex")) return Code2;
  return Bot;
};
const statusStyle: Record<AStatus, { text: string; bg: string }> = {
  active: { text: "text-ok", bg: "bg-ok" },
  idle: { text: "text-muted-foreground", bg: "bg-route" },
  exhausted: { text: "text-err", bg: "bg-err" },
};

const fmt = (s: number) =>
  [Math.floor(s / 3600), Math.floor((s % 3600) / 60), s % 60].map((n) => String(n).padStart(2, "0")).join(":");

function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: ReactNode }) {
  useEffect(() => {
    const k = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", k);
    return () => window.removeEventListener("keydown", k);
  }, [onClose]);
  return (
    <div className="fixed inset-0 z-50 bg-background/80 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-card border rounded-md w-full max-w-lg animate-slide-in" onClick={(e) => e.stopPropagation()}>
        <div className="px-4 py-3 border-b flex items-center justify-between text-xs uppercase tracking-wider text-muted-foreground">
          {title}
          <button onClick={onClose} aria-label="close" className="hover:text-foreground"><X className="size-3.5" /></button>
        </div>
        <div className="p-4">{children}</div>
      </div>
    </div>
  );
}

function Dashboard() {
  const { status, connected, start, next, takeover, setMode: setApiMode } = useAgentRelay(2000);
  const [elapsed, setElapsed] = useState(0);
  const [modal, setModal] = useState<null | "agents" | "new">(null);
  const [draft, setDraft] = useState("");
  const startedAtRef = useRef<number | null>(null);

  // Chrono simple basé sur session.started_at
  useEffect(() => {
    const sa = status?.session?.started_at;
    if (sa) startedAtRef.current = new Date(sa).getTime();
    const t = setInterval(() => {
      if (startedAtRef.current) {
        setElapsed(Math.max(0, Math.floor((Date.now() - startedAtRef.current) / 1000)));
      }
    }, 1000);
    return () => clearInterval(t);
  }, [status?.session?.started_at]);

  const session = status?.session;
  const mode: "manual" | "auto" = (session?.mode as "manual" | "auto") ?? "manual";
  const active = session?.current_agent ?? "—";
  const goal = session?.goal ?? "no session";
  const stepsCount = session?.steps_count ?? 0;
  const agents = (status?.agents ?? []).map((a) => ({
    id: a.name,
    status: (a.status ?? "idle") as AStatus,
    quota: typeof a.quota === "number" ? a.quota : (a.status === "active" ? 100 : a.status === "exhausted" ? 0 : 50),
    description: a.description ?? "",
  }));
  const events = (status?.events ?? []).map((e, i) => ({
    id: i, t: (e.time ?? "").slice(11, 19), k: (e.event as Kind) ?? "OK", m: `${e.agent ? e.agent + " · " : ""}${e.detail ?? ""}`,
  }));
  const dec = status?.last_decision ?? status?.pending_step ?? null;

  const start_ = async () => {
    const g = draft.trim();
    if (!g) return;
    await start(g, mode === "auto");
    setDraft("");
    setModal(null);
    startedAtRef.current = Date.now();
    setElapsed(0);
  };

  const simulateQuota = async (id: string) => {
    const nextCandidate = agents.find((a) => a.id !== id && a.status !== "exhausted");
    if (nextCandidate) await takeover(nextCandidate.id);
  };

  const stats = [
    { icon: Terminal, label: "active agent", value: active, accent: "text-ok" },
    { icon: CheckCircle2, label: "steps completed", value: String(stepsCount), accent: "" },
    { icon: Repeat, label: "handoffs", value: String(events.filter((e) => e.k === "HANDOFF").length), accent: "" },
    { icon: Clock, label: "current session", value: fmt(elapsed), accent: "" },
  ];

  const agentsMd = [
    { h: "Goal", b: goal },
    { h: "This step", b: dec?.task ?? "—" },
    { h: "What's done", b: `${stepsCount} step(s) completed` },
    { h: "Don't", b: "contredire les décisions précédentes · recommencer de zéro" },
  ];

  const taskRows: [string, ReactNode][] = [
    ["goal", goal],
    ["step", `${stepsCount + 1} — ${dec?.task ?? "waiting for decision"}`],
    ["agent", <span className="text-ok">{active}</span>],
    ["context", <button onClick={() => setModal("agents")} className="text-handoff hover:underline">[view AGENTS.md]</button>],
  ];

  return (
    <div className="min-h-screen text-[13px]">
      <header className="h-14 border-b flex items-center justify-between px-6 gap-4">
        <div className="flex items-baseline gap-3 min-w-0">
          <span className="text-ok font-bold">&gt; agentrelay</span>
          <span className="text-muted-foreground text-xs truncate">v0.1.0 · hackathon build</span>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <button onClick={() => setModal("new")} className="flex items-center gap-1.5 border rounded px-2 py-1 hover:border-ok hover:text-ok transition-colors">
            <Plus className="size-3.5" /> new session
          </button>
          <div className="flex border rounded overflow-hidden">
            {(["manual", "auto"] as const).map((m) => (
              <button
                key={m}
                onClick={() => setApiMode(m)}
                className={`px-2 py-1 uppercase transition-colors ${mode === m ? "text-ok bg-ok/10" : "text-muted-foreground hover:text-foreground"}`}
              >
                {m}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <span className={`size-2 rounded-full ${connected ? "bg-ok animate-pulse-dot" : "bg-err"}`} />
            <span>{connected ? "connected" : "offline"}</span>
          </div>
        </div>
      </header>

      <main className="p-6 space-y-6 max-w-7xl mx-auto">
        <section className="grid grid-cols-2 lg:grid-cols-4 gap-px bg-border border rounded-md overflow-hidden">
          {stats.map(({ icon: Icon, label, value, accent }) => (
            <div key={label} className="bg-card p-4">
              <div className="flex items-center gap-2 text-muted-foreground text-xs">
                <Icon className="size-3.5" /> {label}
              </div>
              <div className={`mt-2 text-xl font-medium tabular-nums ${accent}`}>{value}</div>
            </div>
          ))}
        </section>

        <section className="bg-card border border-l-2 border-l-brain rounded-md px-4 py-3 space-y-1">
          <div className="text-xs text-brain uppercase tracking-wider mb-1">last decision</div>
          <div>
            <span className="text-ok">[BRAIN]</span> <span className="text-brain">gemma-3-27b-it</span> chose{" "}
            <span className="text-ok">{dec?.agent ?? "—"}</span>
          </div>
          <div className="text-muted-foreground">task: <span className="text-foreground">{dec?.task ? `"${dec.task}"` : "—"}</span></div>
          <div className="text-muted-foreground">reason: <span className="text-foreground">{dec?.reason ? `"${dec.reason}"` : "—"}</span></div>
        </section>

        <section className="bg-card border rounded-md px-4 py-3">
          <div className="text-xs text-muted-foreground uppercase tracking-wider mb-2">current task</div>
          <dl className="grid grid-cols-[5rem_1fr] gap-y-1">
            {taskRows.map(([k, v]) => (
              <div key={k} className="contents">
                <dt className="text-muted-foreground">{k}:</dt>
                <dd className="truncate">{v}</dd>
              </div>
            ))}
          </dl>
        </section>

        <div className="grid lg:grid-cols-[1fr_1.4fr] gap-6">
          <section className="bg-card border rounded-md">
            <h2 className="px-4 py-3 border-b text-xs text-muted-foreground uppercase tracking-wider">agents</h2>
            <ul>
              {agents.length === 0 && <li className="px-4 py-3 text-muted-foreground">no agents configured</li>}
              {agents.map((a) => {
                const Icon = iconFor(a.id);
                const s = statusStyle[a.status];
                return (
                  <li key={a.id} className="px-4 py-3 border-b last:border-0 transition-colors">
                    <div className="flex items-center justify-between gap-2">
                      <span className="flex items-center gap-2">
                        <Icon className="size-4 text-muted-foreground" /> {a.id}
                      </span>
                      <span className={`${s.text} text-xs`}>● {a.status}</span>
                    </div>
                    <div className="mt-2 h-1 bg-border rounded overflow-hidden">
                      <div className={`h-full ${s.bg} transition-all duration-700`} style={{ width: `${a.quota}%` }} />
                    </div>
                    <div className="mt-2 flex items-center justify-between text-[11px] text-muted-foreground">
                      <span>quota left {a.quota}%</span>
                      <span className="flex items-center gap-1.5">
                        <button
                          onClick={() => simulateQuota(a.id)}
                          aria-label="simulate quota"
                          className="border rounded p-1 text-foreground hover:border-err hover:text-err transition-colors"
                        >
                          <Zap className="size-3" />
                        </button>
                        <button
                          onClick={() => takeover(a.id)}
                          disabled={a.status === "active"}
                          className="border rounded px-2 py-0.5 text-foreground hover:border-handoff hover:text-handoff transition-colors disabled:opacity-30 disabled:pointer-events-none"
                        >
                          take over
                        </button>
                      </span>
                    </div>
                  </li>
                );
              })}
            </ul>
          </section>

          <section className="bg-card border rounded-md flex flex-col h-[420px]">
            <h2 className="px-4 py-3 border-b text-xs text-muted-foreground uppercase tracking-wider flex justify-between">
              event log <span className="text-ok normal-case">● live</span>
            </h2>
            <div className="flex-1 overflow-y-auto p-2 text-xs">
              {events.length === 0 && <div className="p-2 text-muted-foreground">waiting for events_</div>}
              {events.map((e) => (
                <div key={e.id} className="flex gap-3 px-2 py-1 rounded hover:bg-background/50 animate-slide-in">
                  <span className="text-muted-foreground tabular-nums">{e.t}</span>
                  <span className={`${kindColor[e.k] ?? "text-muted-foreground"} w-24 shrink-0`}>[{e.k}]</span>
                  <span className="truncate">{e.m}</span>
                </div>
              ))}
            </div>
          </section>
        </div>

        <section className="flex gap-2 text-xs">
          <button onClick={() => next()} className="border rounded px-3 py-1 hover:border-handoff hover:text-handoff transition-colors">next step</button>
          <button onClick={() => setApiMode(mode === "manual" ? "auto" : "manual")} className="border rounded px-3 py-1 hover:border-ok hover:text-ok transition-colors">toggle mode</button>
        </section>
      </main>

      {modal === "agents" && (
        <Modal title="AGENTS.md" onClose={() => setModal(null)}>
          <div className="space-y-4 text-xs max-h-[60vh] overflow-y-auto">
            {agentsMd.map((s) => (
              <div key={s.h}>
                <div className="text-ok mb-1">## {s.h}</div>
                <pre className="whitespace-pre-wrap font-mono text-foreground/90">{s.b}</pre>
              </div>
            ))}
          </div>
        </Modal>
      )}

      {modal === "new" && (
        <Modal title="new session" onClose={() => setModal(null)}>
          <label className="block text-xs text-muted-foreground mb-2" htmlFor="goal">What do you want to build?</label>
          <textarea
            id="goal"
            autoFocus
            rows={4}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            className="w-full bg-background border rounded p-2 font-mono text-[13px] outline-none focus:border-ok resize-none"
            placeholder="> add JWT authentication to the API_"
          />
          <div className="mt-3 flex justify-end">
            <button
              onClick={start_}
              disabled={!draft.trim()}
              className="border rounded px-3 py-1 text-xs text-ok border-ok/50 hover:bg-ok/10 transition-colors disabled:opacity-30 disabled:pointer-events-none"
            >
              start
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}
