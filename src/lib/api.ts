import type {
  Feedback,
  InterviewSummary,
  Profile,
  QuestionAnalysis,
  RegisterInput,
} from "@/types";

/** next.config.ts rewrites /backend/* to the interview API. */
const BASE = "/backend/interview";

export class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
  }
}

async function request<T = any>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE}${path}`, { cache: "no-store", ...init });
  } catch {
    throw new ApiError("Can't reach the server. Check your connection and try again.");
  }
  let body: any = null;
  try {
    body = await res.json();
  } catch {
    /* non-JSON body */
  }
  if (!res.ok) {
    throw new ApiError(body?.message ?? body?.detail ?? `Request failed (${res.status})`, res.status);
  }
  return body as T;
}

const enc = encodeURIComponent;

export async function login(email: string): Promise<Profile | null> {
  try {
    const body = await request(`/candidate/${enc(email)}`);
    if (body?.status !== "success" || !body.data?.name) return null;
    const d = body.data;
    return {
      name: d.name,
      email: d.email ?? email,
      role: d.role ?? "",
      skills: d.skills ?? "",
      education: d.education ?? "",
      projects: d.projects ?? "",
      achievements: d.achievements ?? "",
      experience: d.experience ?? "",
    };
  } catch (e) {
    if (e instanceof ApiError && e.status && e.status < 500) return null; // unknown user
    throw e;
  }
}

export async function register(input: RegisterInput): Promise<Profile> {
  await request(`/candidates/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      candidate_name: input.name,
      candidate_email: input.email,
      role: input.role,
      skills: input.skills,
      education: input.education,
      projects: input.projects || null,
      achievements: input.achievements || null,
      experience: input.experience || null,
    }),
  });
  return {
    name: input.name,
    email: input.email,
    role: input.role,
    skills: input.skills,
    education: input.education,
    projects: input.projects ?? "",
    achievements: input.achievements ?? "",
    experience: input.experience ?? "",
  };
}

export async function getInterviews(email: string): Promise<InterviewSummary[]> {
  const body = await request(`/candidate/${enc(email)}/interviews`);
  const list: InterviewSummary[] = body?.interviews ?? [];
  return [...list].sort((a, b) => (b.created_at ?? "").localeCompare(a.created_at ?? ""));
}

async function questionFrom(path: string): Promise<string> {
  const body = await request(path);
  const q = body?.data?.question;
  if (body?.status !== "success" || typeof q !== "string" || !q.trim()) {
    throw new ApiError(body?.message ?? "No question received from the server.");
  }
  return q;
}

export const getFirstQuestion = (email: string) =>
  questionFrom(`/candidates/${enc(email)}/interview-questions`);

export const getNextQuestion = () => questionFrom(`/next-question`);

export async function uploadAnswer(question: string, audio: Blob): Promise<void> {
  const form = new FormData();
  form.append("question", question);
  form.append("audio_file", audio, "response.wav");
  await request(`/responses/upload`, { method: "POST", body: form });
}

function normalize(data: any): Feedback {
  // The two feedback endpoints name the per-question block differently.
  const block = data?.question_feedback ?? data?.feedback_by_question ?? {};
  const questions: QuestionAnalysis[] = Array.isArray(block) ? block : (block.question_analysis ?? []);
  return {
    overall: data?.overall_feedback ?? {},
    observations: Array.isArray(block) ? undefined : block.overall_analysis,
    questions,
  };
}

async function feedbackFrom(path: string): Promise<Feedback> {
  const body = await request(path);
  if (body?.status !== "success" || !body.data) {
    throw new ApiError(body?.message ?? "No feedback available yet.");
  }
  return normalize(body.data);
}

export const getLatestFeedback = (email: string) => feedbackFrom(`/candidate/${enc(email)}/overall/feedback`);
export const getInterviewFeedback = (id: string | number) => feedbackFrom(`/${id}/feedback`);
