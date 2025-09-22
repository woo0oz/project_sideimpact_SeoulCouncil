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
  const [userPreferences, setUserPreferences] = useState<UserPreferences | null>(null);
  const [agendas, setAgendas] = useState<Agenda[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  // 개인화된 안건 데이터 로드
  const loadPersonalizedAgendas = async (preferences: UserPreferences) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetchPersonalizedAgendas(preferences);
      setAgendas(response.agendas);
    } catch (err) {
      setError('안건 데이터를 불러오는데 실패했습니다. 잠시 후 다시 시도해주세요.');
      console.error('Failed to load personalized agendas:', err);
      
      // 에러 발생시 전체 안건 데이터로 fallback
      try {
        const fallbackResponse = await fetchAllAgendas();
        setAgendas(fallbackResponse.agendas);
        setError('개인화된 데이터 로드에 실패했지만, 전체 안건을 표시합니다.');
      } catch (fallbackErr) {
        console.error('Fallback also failed:', fallbackErr);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // 필터링된 안건 목록
  const filteredAgendas = agendas.filter((agenda) => {
    switch (activeTab) {
      case "high-impact":
        return agenda.impact === "high";
      case "recent":
        return (
          new Date(agenda.date.replace(/\./g, "-")) >
          new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) // 최근 7일
        );
      case "my-area":
        return userPreferences ? agenda.district.includes(userPreferences.district) : true;
      default:
        return true;
    }
  });

  // 온보딩이 완료되지 않았으면 온보딩 페이지 표시
  if (!isOnboardingCompleted) {
    return (
      <OnboardingPage onComplete={handleOnboardingComplete} />
    );
  }

  return (
    <div className="min-h-screen bg-background font-[Pretendard]">
      <Header />

      <main className="container mx-auto px-4 py-6 max-w-4xl">
        {/* 온보딩 카드 */}
        <OnboardingCard
          isCompleted={isOnboardingCompleted}
          district={userPreferences?.district}
          interests={userPreferences?.interests}
        />

        {/* 에러 메시지 */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}

        {/* 필터 탭 */}
        <FilterTabs
          activeTab={activeTab}
          onTabChange={setActiveTab}
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
                  해당 조건의 안건이 없습니다.
                </p>
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