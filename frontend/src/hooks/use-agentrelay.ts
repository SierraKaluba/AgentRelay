// Hook de polling + mutations pour le dashboard AgentRelay.
// Interroge /api/status toutes les 2 secondes et expose les actions.

import { useCallback, useEffect, useRef, useState } from "react";
import { api, type Status } from "@/lib/api";

interface UseAgentRelayResult {
  status: Status | null;
  connected: boolean;
  loading: boolean;
  error: string | null;
  start: (goal: string, auto?: boolean) => Promise<void>;
  next: (output?: string) => Promise<void>;
  takeover: (agent: string, task?: string) => Promise<void>;
  setMode: (mode: "manual" | "auto") => Promise<void>;
  stop: () => Promise<void>;
  refresh: () => Promise<void>;
}

export function useAgentRelay(pollMs = 2000): UseAgentRelayResult {
  const [status, setStatus] = useState<Status | null>(null);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

  const refresh = useCallback(async () => {
    try {
      const s = await api.getStatus();
      setStatus(s);
      setConnected(true);
      setError(null);
    } catch (e) {
      setConnected(false);
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    timerRef.current = window.setInterval(refresh, pollMs);
    return () => {
      if (timerRef.current !== null) window.clearInterval(timerRef.current);
    };
  }, [pollMs, refresh]);

  const start = useCallback(async (goal: string, auto = false) => {
    await api.start(goal, auto);
    await refresh();
  }, [refresh]);

  const next = useCallback(async (output?: string) => {
    await api.next(output);
    await refresh();
  }, [refresh]);

  const takeover = useCallback(async (agent: string, task?: string) => {
    await api.takeover(agent, task);
    await refresh();
  }, [refresh]);

  const setMode = useCallback(async (mode: "manual" | "auto") => {
    await api.setMode(mode);
    await refresh();
  }, [refresh]);

  const stop = useCallback(async () => {
    await api.stop();
    await refresh();
  }, [refresh]);

  return { status, connected, loading, error, start, next, takeover, setMode, stop, refresh };
}
