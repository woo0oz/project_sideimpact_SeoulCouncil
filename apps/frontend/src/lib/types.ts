// 사용자 선호도 타입
export interface UserPreferences {
  district: string;
  interests: string[];
}

// 안건 타입
export interface Agenda {
  id: string;
  title: string;
  summary: string;
  impact: "high" | "medium" | "low";
  impactDescription: string;
  district: string;
  date: string;
  category: string;
  fullContent: string;
  budget: string;
  implementationDate: string;
  relatedDepartment: string;
}

// API 응답 타입
export interface AgendasResponse {
  agendas: Agenda[];
  message?: string;
  total?: number;
  page?: number;
  hasMore?: boolean;
}

// API 에러 타입
export interface ApiError {
  message: string;
  code?: string;
  status?: number;
}

// 필터 옵션 타입
export interface FilterOptions {
  district?: string;
  category?: string;
  impact?: string;
  dateFrom?: string;
  dateTo?: string;
  limit?: number;
  offset?: number;
}
