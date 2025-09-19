import { UserPreferences, Agenda, AgendasResponse, FilterOptions, ApiError } from './types';

// 환경 설정
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://gaji.ai.kr/api';
const IS_DEVELOPMENT = process.env.REACT_APP_ENVIRONMENT !== 'production';

// 임시 목업 데이터
const mockAgendas: Agenda[] = [
  {
    id: "1",
    title: "동작구 주택가 주차장 확충 예산 승인",
    summary: "상도동, 노량진동 일대 공영주차장 3개소 신설 예산 12억원 승인. 기존 주차난 해소를 위해 2024년 상반기 착공 예정.",
    impact: "high" as const,
    impactDescription: "우리 동네 주차난이 크게 개선될 예정입니다. 상도동 거주자는 집 근처 주차공간이 약 150대 늘어납니다.",
    district: "서울 동작구",
    date: "2024.01.15",
    category: "교통",
    fullContent: '동작구의회는 제1차 정례회에서 주택가 주차장 확충 사업에 대한 예산안을 만장일치로 가결했다. 이번 사업은 상도동 3개소, 노량진동 2개소에 총 150대 규모의 공영주차장을 신설하는 내용이다. 총 사업비는 12억원으로, 토지매입비 8억원, 시설비 4억원으로 구성된다. 구의회 교통위원회는 "지역 주민들의 오랜 숙원사업이었던 주차난 해소에 큰 도움이 될 것"이라고 밝혔다.',
    budget: "12억원 (토지매입비 8억원, 시설비 4억원)",
    implementationDate: "2024년 6월 착공 예정",
    relatedDepartment: "동작구 교통행정과",
  },
  {
    id: "2",
    title: "흑석동 어린이 놀이터 안전시설 개선",
    summary: "노후된 놀이기구 교체 및 안전펜스 설치로 어린이 안전 강화. 총 사업비 3억원으로 5개 놀이터 개선.",
    impact: "medium" as const,
    impactDescription: "자녀가 있는 가정에서는 더 안전한 놀이환경을 이용할 수 있게 됩니다. 특히 흑석동 거주 가정에 직접적 혜택이 있습니다.",
    district: "서울 동작구",
    date: "2024.01.12",
    category: "복지",
    fullContent: "동작구의회는 흑석동 일대 5개 어린이 놀이터의 안전시설 개선사업을 승인했다. 10년 이상 된 노후 놀이기구를 최신 안전기준에 맞춰 교체하고, 놀이구역 주변에 안전펜스를 추가로 설치한다. 또한 놀이터 바닥재를 충격흡수 소재로 교체하여 어린이들의 안전을 강화한다.",
    budget: "3억원",
    implementationDate: "2024년 3월 시작",
    relatedDepartment: "동작구 여성가족과",
  },
  {
    id: "3",
    title: "상도동 가로수 정비 및 보도 확장",
    summary: "보행자 안전을 위한 보도 확장과 가로수 정비 사업. 상도로 일대 1.2km 구간 대상.",
    impact: "medium" as const,
    impactDescription: "상도동 거주자의 보행 편의성이 개선되고, 더 쾌적한 가로환경을 경험할 수 있습니다.",
    district: "서울 동작구",
    date: "2024.01.10",
    category: "환경",
    fullContent: "상도로 일대 1.2km 구간의 보도를 기존 1.5m에서 2.0m로 확장하고, 노후된 가로수 80그루를 새로 식재한다. 보행자와 자전거 이용자의 안전을 위해 별도의 자전거 도로도 신설할 예정이다.",
    budget: "8억원",
    implementationDate: "2024년 4월 착공",
    relatedDepartment: "동작구 도시계획과",
  },
  {
    id: "4",
    title: "사당동 공공 도서관 운영시간 연장",
    summary: "직장인과 학생들의 편의를 위해 평일 운영시간을 오후 10시까지 연장. 주말도 오후 8시까지 운영.",
    impact: "low" as const,
    impactDescription: "도서관을 자주 이용하는 직장인과 학생들에게 더 많은 이용 시간이 제공됩니다.",
    district: "서울 동작구",
    date: "2024.01.08",
    category: "교육",
    fullContent: "사당동 공공도서관의 운영시간을 기존 평일 오후 6시에서 오후 10시까지, 주말은 오후 5시에서 오후 8시까지 연장하기로 결정했다. 이에 따른 추가 인건비와 관리비용으로 연간 2억원의 예산이 투입된다.",
    budget: "연간 2억원 (인건비, 관리비)",
    implementationDate: "2024년 2월 1일부터",
    relatedDepartment: "동작구 교육지원과",
  },
];

// API 헬퍼 함수
async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const error: ApiError = {
        message: errorData.message || `HTTP error! status: ${response.status}`,
        code: errorData.code,
        status: response.status,
      };
      throw error;
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      console.error(`API request failed: ${error.message}`);
    }
    throw error;
  }
}

// 개인화된 안건 조회
export async function fetchPersonalizedAgendas(preferences: UserPreferences): Promise<AgendasResponse> {
  // TODO: 백엔드 연결시 실제 API 호출로 변경
  if (!IS_DEVELOPMENT) {
    try {
      return await apiRequest<AgendasResponse>('/agendas/personalized', {
        method: 'POST',
        body: JSON.stringify(preferences),
      });
    } catch (error) {
      console.warn('API call failed, falling back to mock data:', error);
    }
  }

  // 임시 목업 데이터 (선호도 기반 필터링)
  console.log('Using mock data - Backend will be connected later');
  console.log('User preferences:', preferences);
  
  // 사용자 선호도에 따른 간단한 필터링
  const filteredAgendas = mockAgendas.filter(agenda => {
    // 지역 필터링
    if (preferences.district && !agenda.district.includes(preferences.district)) {
      return false;
    }
    
    // 관심사 필터링
    if (preferences.interests.length > 0 && !preferences.interests.includes(agenda.category)) {
      return false;
    }
    
    return true;
  });

  return {
    agendas: filteredAgendas.length > 0 ? filteredAgendas : mockAgendas,
    message: 'Mock data loaded successfully',
    total: filteredAgendas.length,
  };
}

// 전체 안건 조회
export async function fetchAllAgendas(filters?: FilterOptions): Promise<AgendasResponse> {
  // TODO: 백엔드 연결시 실제 API 호출로 변경
  if (!IS_DEVELOPMENT) {
    try {
      const queryParams = filters ? `?${new URLSearchParams(filters as Record<string, string>)}` : '';
      return await apiRequest<AgendasResponse>(`/agendas${queryParams}`);
    } catch (error) {
      console.warn('API call failed, falling back to mock data:', error);
    }
  }

  console.log('Using mock data - Backend will be connected later');
  
  let filteredAgendas = [...mockAgendas];
  
  // 필터 적용
  if (filters) {
    if (filters.district) {
      filteredAgendas = filteredAgendas.filter(agenda => 
        agenda.district.includes(filters.district!)
      );
    }
    
    if (filters.category) {
      filteredAgendas = filteredAgendas.filter(agenda => 
        agenda.category === filters.category
      );
    }
    
    if (filters.impact) {
      filteredAgendas = filteredAgendas.filter(agenda => 
        agenda.impact === filters.impact
      );
    }
  }

  return {
    agendas: filteredAgendas,
    message: 'All mock data loaded successfully',
    total: filteredAgendas.length,
  };
}

// 특정 안건 상세 조회
export async function fetchAgendaById(id: string): Promise<Agenda> {
  // TODO: 백엔드 연결시 실제 API 호출로 변경
  if (!IS_DEVELOPMENT) {
    try {
      return await apiRequest<Agenda>(`/agendas/${id}`);
    } catch (error) {
      console.warn('API call failed, falling back to mock data:', error);
    }
  }

  const agenda = mockAgendas.find(a => a.id === id);
  if (!agenda) {
    throw new Error(`Agenda with id ${id} not found`);
  }
  
  return agenda;
}

// 사용자 선호도 저장
export async function saveUserPreferences(preferences: UserPreferences): Promise<{ success: boolean }> {
  // TODO: 백엔드 연결시 실제 API 호출로 변경
  if (!IS_DEVELOPMENT) {
    try {
      return await apiRequest<{ success: boolean }>('/user/preferences', {
        method: 'POST',
        body: JSON.stringify(preferences),
      });
    } catch (error) {
      console.warn('API call failed:', error);
    }
  }

  console.log('Mock: Saving user preferences:', preferences);
  return { success: true };
}

// 지역구 목록 조회
export async function fetchDistricts(): Promise<string[]> {
  // TODO: 백엔드 연결시 실제 API 호출로 변경
  if (!IS_DEVELOPMENT) {
    try {
      return await apiRequest<string[]>('/districts');
    } catch (error) {
      console.warn('API call failed, using hardcoded data:', error);
    }
  }

  return [
    '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
    '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구',
    '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'
  ];
}

// 관심사 카테고리 조회
export async function fetchCategories(): Promise<Array<{id: string, name: string, emoji: string, description: string}>> {
  // TODO: 백엔드 연결시 실제 API 호출로 변경
  if (!IS_DEVELOPMENT) {
    try {
      return await apiRequest<Array<{id: string, name: string, emoji: string, description: string}>>('/categories');
    } catch (error) {
      console.warn('API call failed, using hardcoded data:', error);
    }
  }

  return [
    { id: 'traffic', name: '교통', emoji: '🚗', description: '주차, 도로, 대중교통' },
    { id: 'environment', name: '환경', emoji: '🌱', description: '공원, 쓰레기, 대기질' },
    { id: 'welfare', name: '복지', emoji: '🤝', description: '아동, 노인, 장애인' },
    { id: 'economy', name: '경제', emoji: '💼', description: '상권, 일자리, 예산' },
    { id: 'education', name: '교육', emoji: '📚', description: '학교, 도서관, 평생교육' },
    { id: 'safety', name: '안전', emoji: '🛡️', description: 'CCTV, 방범, 재해대응' },
    { id: 'culture', name: '문화', emoji: '🎭', description: '축제, 문화시설, 예술' },
    { id: 'health', name: '보건', emoji: '🏥', description: '의료, 건강, 위생' }
  ];
}
