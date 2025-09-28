import { UserPreferences, Agenda, AgendasResponse, FilterOptions, ApiError } from './types';

// 환경 설정 (Vite 방식)
const API_BASE_URL = import.meta.env.VITE_API_URL || '';
const IS_DEVELOPMENT = import.meta.env.VITE_ENVIRONMENT !== 'production';

console.log('API_BASE_URL:', API_BASE_URL);
console.log('IS_DEVELOPMENT:', IS_DEVELOPMENT);

// 임시 목업 데이터
const mockAgendas: Agenda[] = [
  {
    id: "1",
    title: "동작구 상도동 주차장 확충 사업",
    summary: "주택가 주차난 해소를 위한 공영주차장 건설. 상도동 3개소, 노량진동 2개소에 총 150대 규모.",
    impact: "high" as const,
    impactDescription: "우리 동네 주차난이 크게 개선될 예정입니다. 상도동 거주자는 집 근처 주차공간이 약 150대 늘어납니다.",
    district: "서울 동작구",
    date: "2025.09.15", // 최근 날짜로 업데이트
    category: "교통",
    fullContent: '동작구의회는 제1차 정례회에서 주택가 주차장 확충 사업에 대한 예산안을 만장일치로 가결했다. 이번 사업은 상도동 3개소, 노량진동 2개소에 총 150대 규모의 공영주차장을 신설하는 내용이다. 총 사업비는 12억원으로, 토지매입비 8억원, 시설비 4억원으로 구성된다. 구의회 교통위원회는 "지역 주민들의 오랜 숙원사업이었던 주차난 해소에 큰 도움이 될 것"이라고 밝혔다.',
    originalUrl: "https://dongjak.go.kr/council/agenda/2024/001",
  },
  {
    id: "2",
    title: "흑석동 어린이 놀이터 안전시설 개선",
    summary: "노후된 놀이기구 교체 및 안전펜스 설치로 어린이 안전 강화. 총 사업비 3억원으로 5개 놀이터 개선.",
    impact: "medium" as const,
    impactDescription: "자녀가 있는 가정에서는 더 안전한 놀이환경을 이용할 수 있게 됩니다. 특히 흑석동 거주 가정에 직접적 혜택이 있습니다.",
    district: "서울 동작구",
    date: "2025.09.10", // 최근 날짜로 업데이트
    category: "복지",
    fullContent: "동작구의회는 흑석동 일대 5개 어린이 놀이터의 안전시설 개선사업을 승인했다. 10년 이상 된 노후 놀이기구를 최신 안전기준에 맞춰 교체하고, 놀이구역 주변에 안전펜스를 추가로 설치한다. 또한 놀이터 바닥재를 충격흡수 소재로 교체하여 어린이들의 안전을 강화한다.",
  },
  {
    id: "3",
    title: "관악구 신림동 지하철 2호선 연장 검토 요구",
    summary: "2호선 신림역까지 연장하여 교통편의 개선 추진. 서울시에 정식 건의안 제출 예정.",
    impact: "high" as const,
    impactDescription: "신림동, 봉천동 거주자들의 교통편의가 크게 개선됩니다. 출퇴근 시간이 30분 이상 단축될 것으로 예상됩니다.",
    district: "서울 관악구",
    date: "2025.09.05", // 최근 날짜로 업데이트
    category: "교통",
    fullContent: "관악구의회는 지하철 2호선 신림역 연장에 대한 서울시 건의안을 채택했다. 현재 신대방역까지인 2호선을 신림역까지 연장하여 관악구 교통불편을 해소하겠다는 내용이다. 총 연장거리 2.5km, 예상 건설비 8,000억원 규모의 대형 프로젝트다.",
  },
  {
    id: "4",
    title: "사당동 공공 도서관 운영시간 연장",
    summary: "직장인과 학생들의 편의를 위해 평일 운영시간을 오후 10시까지 연장. 주말도 오후 8시까지 운영.",
    impact: "low" as const,
    impactDescription: "도서관을 자주 이용하는 직장인과 학생들에게 더 많은 이용 시간이 제공됩니다.",
    district: "서울 동작구",
    date: "2025.09.01",
    category: "교육",
    fullContent: "사당동 공공도서관의 운영시간을 기존 평일 오후 6시에서 오후 10시까지, 주말은 오후 5시에서 오후 8시까지 연장하기로 결정했다. 이에 따른 추가 인건비와 관리비용으로 연간 2억원의 예산이 투입된다.",
  },
  {
    id: "5",
    title: "동작구 노량진동 고시원 화재안전 강화",
    summary: "노량진 고시원 밀집지역 화재안전 점검 및 스프링클러 설치 의무화. 총 50개소 대상.",
    impact: "high" as const,
    impactDescription: "고시원 거주자들의 생명 안전이 크게 향상됩니다. 화재 발생 시 신속한 대응이 가능해집니다.",
    district: "서울 동작구",
    date: "2025.09.20",
    category: "안전",
    fullContent: "동작구의회는 노량진동 고시원 밀집지역의 화재안전 강화를 위한 조례 개정안을 통과시켰다. 모든 고시원에 스프링클러 설치를 의무화하고, 정기적인 안전점검을 실시하기로 했다. 총 사업비 15억원이 투입되며, 2026년까지 완료 예정이다.",
  },
  {
    id: "6",
    title: "관악구 봉천동 청년 임대주택 공급",
    summary: "청년층을 위한 임대주택 200세대 공급. 시세의 80% 수준으로 임대료 책정.",
    impact: "high" as const,
    impactDescription: "관악구 거주 청년들의 주거비 부담이 크게 줄어들 것으로 예상됩니다. 안정적인 주거 환경을 제공받을 수 있습니다.",
    district: "서울 관악구",
    date: "2025.09.22",
    category: "주거",
    fullContent: "관악구의회는 봉천동 일대에 청년 임대주택 200세대를 공급하는 사업을 승인했다. 만 19-39세 청년을 대상으로 하며, 임대료는 시세의 80% 수준으로 책정된다. 총 사업비 500억원으로 2027년 입주 예정이다.",
  },
];

// API 헬퍼 함수
// 안전한 날짜 파싱 함수
function parseDate(dateStr: string): Date {
  // "2025.09.22" → "2025-09-22"
  return new Date(dateStr.replace(/\./g, '-').trim());
}
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

  // 개발 환경에서는 빈 배열 반환 (실제 데이터만 사용)
  console.log('Using development mode: no mock data');
  return {
    agendas: [],
    message: '개발 환경에서는 mock 데이터 미사용',
    total: 0,
  };
}

// 전체 안건 조회
export async function fetchAllAgendas(filters?: FilterOptions): Promise<AgendasResponse> {
  // TODO: 백엔드 연결시 실제 API 호출로 변경
  if (!IS_DEVELOPMENT) {
    try {
      // Cloud Run API를 환경 변수(API_BASE_URL)로 통일
      const response = await fetch(`${API_BASE_URL}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          district: filters?.district || "",
          category: filters?.category || "",
          impact: filters?.impact || "",
          dateFrom: filters?.dateFrom || "",
          dateTo: filters?.dateTo || "",
          limit: filters?.limit || 20,
          offset: filters?.offset || 0,
        })
      });
      if (!response.ok) throw new Error("서버 오류 발생");
      const data = await response.json();
      // data가 Agenda[] 형태라고 가정
      // 최신 날짜(내림차순)로 정렬 (parseDate 사용)
      const sortedAgendas = Array.isArray(data) ? data.slice().sort((a, b) => {
        return parseDate(b.date).getTime() - parseDate(a.date).getTime();
      }) : [];
      return {
        agendas: sortedAgendas,
        message: 'AlloyDB에서 데이터를 성공적으로 불러옴',
        total: sortedAgendas.length,
      };
    } catch (error) {
      console.error('Cloud Run API 호출 실패:', error);
      return {
        agendas: [],
        message: '데이터를 불러오지 못했습니다',
        total: 0,
      };
    }
  }

  // 개발 환경에서는 빈 배열 반환 (실제 데이터만 사용)
  console.log('Using development mode: no mock data');
  return {
    agendas: [],
    message: '개발 환경에서는 mock 데이터 미사용',
    total: 0,
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
