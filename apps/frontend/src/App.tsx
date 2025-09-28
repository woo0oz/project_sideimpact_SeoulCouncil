import { useState } from "react";
import { Header } from "./components/Header";
import { OnboardingCard } from "./components/OnboardingCard";
import { OnboardingPage } from "./components/OnboardingPage";
import { FilterTabs } from "./components/FilterTabs";
import { AgendaCard } from "./components/AgendaCard";
import { DetailModal } from "./components/DetailModal";
import { 
  fetchPersonalizedAgendas, 
  fetchAllAgendas, 
  saveUserPreferences
} from "./lib/api";
import type { Agenda, UserPreferences } from "./lib/types";

export default function App() {
  const [activeTab, setActiveTab] = useState("all");
  const [selectedAgenda, setSelectedAgenda] = useState<Agenda | null>(null);
  const [isOnboardingCompleted, setIsOnboardingCompleted] = useState(false);
  const [isEditingPreferences, setIsEditingPreferences] = useState(false);
  const [userPreferences, setUserPreferences] = useState<UserPreferences | null>(null);
  const [agendas, setAgendas] = useState<Agenda[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  // 온보딩 완료 핸들러
  const handleOnboardingComplete = async (data: UserPreferences) => {
    setUserPreferences(data);
    setIsOnboardingCompleted(true);
    
    // 사용자 선호도 저장
    try {
      await saveUserPreferences(data);
    } catch (error) {
      console.error('Failed to save preferences:', error);
    }
    
    // 개인화된 안건 데이터 로드
    await loadPersonalizedAgendas(data);
  };

  // 사용자 설정 편집 핸들러
  const handleEditPreferences = () => {
    setIsEditingPreferences(true);
  };

  // 설정 편집 완료 핸들러
  const handleEditComplete = async (data: UserPreferences) => {
    setUserPreferences(data);
    setIsEditingPreferences(false);
    
    // 사용자 선호도 저장 및 안건 다시 로드
    try {
      await saveUserPreferences(data);
      await loadPersonalizedAgendas(data);
    } catch (err) {
      console.error('Failed to save updated preferences:', err);
      setError('설정 저장에 실패했습니다. 다시 시도해주세요.');
    }
  };

  // 개인화된 안건 데이터 로드
  const loadPersonalizedAgendas = async (preferences: UserPreferences) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetchPersonalizedAgendas(preferences);
      const convertAgenda = (row: any): Agenda => ({
  id: row.agenda_id ?? row.id,
  title: row.agenda_title ?? row.title,
  summary: row.agenda_summary ?? row.summary,
  impact: row.agenda_impact ?? row.impact ?? 'high',
  category: row.agenda_interests ?? row.category,
  fullContent: row.agenda_full_text ?? row.fullContent,
  district: row.district ?? '',
  date: row.date ?? '',
  impactDescription: row.agenda_impact ?? row.impactDescription ?? '',
  originalUrl: row.originalUrl ?? undefined
      });
      setAgendas((response.agendas ?? []).map(convertAgenda));
    } catch (err) {
      setError('안건 데이터를 불러오는데 실패했습니다. 잠시 후 다시 시도해주세요.');
      console.error('Failed to load personalized agendas:', err);
      
      // 에러 발생시 전체 안건 데이터로 fallback
      try {
  const fallbackResponse = await fetchAllAgendas();
  setAgendas((fallbackResponse.agendas ?? []).map(convertAgenda));
        setError('개인화된 데이터 로드에 실패했지만, 전체 안건을 표시합니다.');
      } catch (fallbackErr) {
        console.error('Fallback also failed:', fallbackErr);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // 필터링된 안건 목록
  const filteredAgendas = (() => {
    let filtered = agendas.filter((agenda) => {
      // 먼저 탭별 필터링 적용
      let tabFiltered = false;
      switch (activeTab) {
        case "high-impact":
          // 우리 동네 데이터 중 높은 영향을 가진 데이터
          tabFiltered = userPreferences 
            ? agenda.district.includes(userPreferences.district) && agenda.impact === "high"
            : agenda.impact === "high";
          break;
        case "recent":
          // 우리 동네 소식 중 한 달 안의 데이터
          const isRecent = new Date(agenda.date.replace(/\./g, "-")) > 
            new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
          tabFiltered = userPreferences 
            ? agenda.district.includes(userPreferences.district) && isRecent
            : isRecent;
          break;
        case "my-area":
          // 우리 동네 전체 소식
          tabFiltered = userPreferences ? agenda.district.includes(userPreferences.district) : true;
          break;
        default:
          tabFiltered = true;
      }

      // 검색어 필터링 적용
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase().trim();
        const matchesSearch = 
          agenda.title.toLowerCase().includes(query) ||
          agenda.summary.toLowerCase().includes(query) ||
          agenda.category.toLowerCase().includes(query) ||
          agenda.district.toLowerCase().includes(query);
        
        return tabFiltered && matchesSearch;
      }

      return tabFiltered;
    });

    // 최근 안건 탭인 경우 최신순으로 정렬
    if (activeTab === "recent") {
      filtered = filtered.sort((a, b) => {
        const dateA = new Date(a.date.replace(/\./g, "-"));
        const dateB = new Date(b.date.replace(/\./g, "-"));
        return dateB.getTime() - dateA.getTime(); // 최신순 정렬
      });
    }

    return filtered;
  })();

  // 온보딩이 완료되지 않았거나 편집 모드면 온보딩 페이지 표시
  if (!isOnboardingCompleted) {
    return (
      <OnboardingPage onComplete={handleOnboardingComplete} />
    );
  }

  if (isEditingPreferences) {
    return (
      <OnboardingPage 
        onComplete={handleEditComplete}
        initialDistrict={userPreferences?.district}
        initialInterests={userPreferences?.interests}
      />
    );
  }

  return (
    <div className="min-h-screen bg-background font-[Pretendard]">
      <Header 
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />

      <main className="container mx-auto px-4 py-6 max-w-4xl">
        {/* 온보딩 카드 */}
        <OnboardingCard
          isCompleted={isOnboardingCompleted}
          district={userPreferences?.district}
          interests={userPreferences?.interests}
          onEdit={handleEditPreferences}
        />

        {/* 에러 메시지 */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}

        {/* 검색 결과 정보 */}
        {searchQuery.trim() && (
          <div className="mb-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
            <p className="text-sm text-purple-700">
              <span className="font-medium">"{searchQuery}"</span> 검색결과 
              <span className="font-medium ml-1">{filteredAgendas.length}건</span>
            </p>
          </div>
        )}

        {/* 필터 탭 */}
        <FilterTabs
          activeTab={activeTab}
          onTabChange={setActiveTab}
          agendas={agendas}
          userPreferences={userPreferences}
        />

        {/* 로딩 상태 */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <p className="mt-2 text-muted-foreground">안건을 불러오는 중...</p>
          </div>
        )}

        {/* 안건 목록 */}
        {!isLoading && (
          <div className="space-y-4">
            {filteredAgendas.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-muted-foreground">
                  {searchQuery.trim() 
                    ? `"${searchQuery}" 검색 결과가 없습니다.`
                    : '해당 조건의 안건이 없습니다.'
                  }
                </p>
                {searchQuery.trim() && (
                  <p className="text-sm text-muted-foreground mt-2">
                    다른 키워드로 검색해보세요.
                  </p>
                )}
              </div>
            ) : (
              filteredAgendas.map((agenda) => (
                <AgendaCard
                  key={agenda.id}
                  title={agenda.title}
                  summary={agenda.summary}
                  impact={agenda.impact}
                  impactDescription={agenda.impactDescription}
                  district={agenda.district}
                  date={agenda.date}
                  category={agenda.category}
                  onClick={() => setSelectedAgenda(agenda)}
                />
              ))
            )}
          </div>
        )}

        {/* 상세 모달 */}
        <DetailModal
          isOpen={selectedAgenda !== null}
          onClose={() => setSelectedAgenda(null)}
          agenda={selectedAgenda}
        />
      </main>
    </div>
  );
}

function convertAgenda(value: Agenda, index: number, array: Agenda[]): Agenda {
  throw new Error("Function not implemented.");
}
