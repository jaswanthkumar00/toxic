import type { Exercise, Progress, SubmissionResult, Track, User } from "../../shared/src";

const API_URL = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    credentials: "include",
    headers,
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(payload?.detail || `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  me: () => request<User>("/api/auth/me"),
  login: (email: string, password: string) =>
    request<User>("/api/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  register: (name: string, email: string, password: string) =>
    request<User>("/api/auth/register", { method: "POST", body: JSON.stringify({ name, email, password }) }),
  logout: () => request<{ status: string }>("/api/auth/logout", { method: "POST" }),
  tracks: () => request<Track[]>("/api/tracks"),
  exercises: () => request<Exercise[]>("/api/exercises"),
  progress: () => request<Progress>("/api/progress/me"),
  submissions: () => request<Progress["recent_submissions"]>("/api/submissions/mine"),
  submit: (exercise_id: number, code: string, action: "run" | "submit") =>
    request<SubmissionResult>("/api/submissions", {
      method: "POST",
      body: JSON.stringify({ exercise_id, code, action }),
    }),
  hint: (exercise_id: number, code: string) =>
    request<{ source: string; hint: string }>("/api/assistant/hint", {
      method: "POST",
      body: JSON.stringify({ exercise_id, code }),
    }),
};
