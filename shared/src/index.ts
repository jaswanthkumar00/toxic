export type UserRole = "student" | "instructor";

export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
}

export interface Track {
  id: number;
  slug: string;
  title: string;
  description: string;
  level: string;
  icon: string;
  exercise_count: number;
}

export interface Exercise {
  id: number;
  slug: string;
  track_id: number;
  track_title: string;
  title: string;
  problem_statement: string;
  starter_code: string;
  language: string;
  difficulty: string;
  estimated_minutes: number;
  skill: string;
  tasks: string[];
  test_cases: Array<{ name: string; input: unknown; expected: unknown }>;
}

export interface SubmissionResult {
  submission_id: number;
  status: "passed" | "needs_work";
  score: number;
  evaluation_type: "static_mock";
  execution_time_ms: number;
  output: string;
  test_results: Array<{ name: string; passed: boolean }>;
  passed_count: number;
  total_count: number;
  hint: string | null;
  code_quality: { line_count: number; has_tests: boolean; score: number };
}

export interface Progress {
  completed_count: number;
  completed_exercise_ids: number[];
  total_exercises: number;
  completion_percent: number;
  total_submissions: number;
  skills: Array<{ name: string; score: number }>;
  recommended_exercise_id: number | null;
  recent_submissions: Array<{
    id: number;
    exercise_id: number;
    exercise_title: string;
    status: string;
    score: number;
    created_at: string;
  }>;
}
