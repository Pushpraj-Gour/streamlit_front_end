export interface Profile {
  name: string;
  email: string;
  role: string;
  skills: string;
  education: string;
  projects: string;
  achievements: string;
  experience: string;
}

export interface RegisterInput {
  name: string;
  email: string;
  role: string;
  education: string;
  skills: string;
  projects?: string;
  achievements?: string;
  experience?: string;
}

export interface InterviewSummary {
  id: number;
  score: number | null;
  summary: string;
  created_at: string;
}

export interface QuestionDetail {
  communication_score?: number;
  communication_reasoning?: string;
  content_quality_score?: number;
  content_quality_reasoning?: string;
  domain_insight_score?: number;
  domain_insight_reasoning?: string;
  strategic_depth_score?: number;
  strategic_depth_reasoning?: string;
  professional_tone_score?: number;
  professional_tone_reasoning?: string;
  ideal_answer?: string;
}

export interface QuestionAnalysis {
  question: string;
  response?: string;
  overall_score?: number;
  overall_reasoning?: string;
  question_and_response_detailed_analysis?: QuestionDetail[];
}

export interface OverallFeedback {
  overall_score?: number;
  overall_reasoning?: string;
  overall_communication_score?: number;
  overall_communication_reasoning?: string;
  overall_content_quality_score?: number;
  overall_content_quality_reasoning?: string;
  overall_domain_insight_score?: number;
  overall_domain_insight_reasoning?: string;
  technical_skills_with_score?: string[];
  soft_skills_with_score?: string[];
}

export interface Feedback {
  overall: OverallFeedback;
  observations?: string;
  questions: QuestionAnalysis[];
}
