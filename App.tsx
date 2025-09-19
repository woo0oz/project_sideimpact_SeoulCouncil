import React, { useState } from "react";
import { Header } from "./components/Header";
import { OnboardingCard } from "./components/OnboardingCard";
import { OnboardingPage } from "./components/OnboardingPage";
import { FilterTabs } from "./components/FilterTabs";
import { AgendaCard } from "./components/AgendaCard";
import { DetailModal } from "./components/DetailModal";

// 목업 데이터
const mockAgendas = [
  {
    id: "1",
    title: "동작구 주택가 주차장 확충 예산 승인",
    summary:
      "상도동, 노량진동 일대 공영주차장 3개소 신설 예산 12억원 승인. 기존 주차난 해소를 위해 2024년 상반기 착공 예정.",
    impact: "high" as const,
    impactDescription:
      "우리 동네 주차난이 크게 개선될 예정입니다. 상도동 거주자는 집 근처 주차공간이 약 150대 늘어납니다.",
    district: "서울 동작구",
    date: "2024.01.15",
    category: "교통",
    fullContent:
      '동작구의회는 제1차 정례회에서 주택가 주차장 확충 사업에 대한 예산안을 만장일치로 가결했다. 이번 사업은 상도동 3개소, 노량진동 2개소에 총 150대 규모의 공영주차장을 신설하는 내용이다. 총 사업비는 12억원으로, 토지매입비 8억원, 시설비 4억원으로 구성된다. 구의회 교통위원회는 "지역 주민들의 오랜 숙원사업이었던 주차난 해소에 큰 도움이 될 것"이라고 밝혔다.',
    budget: "12억원 (토지매입비 8억원, 시설비 4억원)",
    implementationDate: "2024년 6월 착공 예정",
    relatedDepartment: "동작구 교통행정과",
  },
  {
    id: "2",
    title: "흑석동 어린이 놀이터 안전시설 개선",
    summary:
      "노후된 놀이기구 교체 및 안전펜스 설치로 어린이 안전 강화. 총 사업비 3억원으로 5개 놀이터 개선.",
    impact: "medium" as const,
    impactDescription:
      "자녀가 있는 가정에서는 더 안전한 놀이환경을 이용할 수 있게 됩니다. 특히 흑석동 거주 가정에 직접적 혜택이 있습니다.",
    district: "서울 동작구",
    date: "2024.01.12",
    category: "복지",
    fullContent:
      "동작구의회는 흑석동 일대 5개 어린이 놀이터의 안전시설 개선사업을 승인했다. 10년 이상 된 노후 놀이기구를 최신 안전기준에 맞춰 교체하고, 놀이구역 주변에 안전펜스를 추가로 설치한다. 또한 놀이터 바닥재를 충격흡수 소재로 교체하여 어린이들의 안전을 강화한다.",
    budget: "3억원",
    implementationDate: "2024년 3월 시작",
    relatedDepartment: "동작구 여성가족과",
  },
  {
    id: "3",
    title: "상도동 가로수 정비 및 보도 확장",
    summary:
      "보행자 안전을 위한 보도 확장과 가로수 정비 사업. 상도로 일대 1.2km 구간 대상.",
    impact: "medium" as const,
    impactDescription:
      "상도동 거주자의 보행 편의성이 개선되고, 더 쾌적한 가로환경을 경험할 수 있습니다.",
    district: "서울 동작구",
    date: "2024.01.10",
    category: "환경",
    fullContent:
      "상도로 일대 1.2km 구간의 보도를 기존 1.5m에서 2.0m로 확장하고, 노후된 가로수 80그루를 새로 식재한다. 보행자와 자전거 이용자의 안전을 위해 별도의 자전거 도로도 신설할 예정이다.",
    budget: "8억원",
    implementationDate: "2024년 4월 착공",
    relatedDepartment: "동작구 도시계획과",
  },
  {
    id: "4",
    title: "사당동 공공 도서관 운영시간 연장",
    summary:
      "직장인과 학생들의 편의를 위해 평일 운영시간을 오후 10시까지 연장. 주말도 오후 8시까지 운영.",
    impact: "low" as const,
    impactDescription:
      "도서관을 자주 이용하는 직장인과 학생들에게 더 많은 이용 시간이 제공됩니다.",
    district: "서울 동작구",
    date: "2024.01.08",
    category: "교육",
    fullContent:
      "사당동 공공도서관의 운영시간을 기존 평일 오후 6시에서 오후 10시까지, 주말은 오후 5시에서 오후 8시까지 연장하기로 결정했다. 이에 따른 추가 인건비와 관리비용으로 연간 2억원의 예산이 투입된다.",
    budget: "연간 2억원 (인건비, 관리비)",
    implementationDate: "2024년 2월 1일부터",
    relatedDepartment: "동작구 교육지원과",
  },
];

export default function App() {
  const [activeTab, setActiveTab] = useState("all");
  const [selectedAgenda, setSelectedAgenda] = useState<
    (typeof mockAgendas)[0] | null
  >(null);
  const [isOnboardingCompleted, setIsOnboardingCompleted] =
    useState(false);
  const [userPreferences, setUserPreferences] = useState<{
    district: string;
    interests: string[];
  } | null>(null);

  const handleOnboardingComplete = (data: {
    district: string;
    interests: string[];
  }) => {
    setUserPreferences(data);
    setIsOnboardingCompleted(true);
  };

  const filteredAgendas = mockAgendas.filter((agenda) => {
    switch (activeTab) {
      case "high-impact":
        return agenda.impact === "high";
      case "recent":
        return (
          new Date(agenda.date.replace(/\./g, "-")) >
          new Date("2024-01-10")
        );
      case "my-area":
        return agenda.district.includes("동작구");
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

        {/* 필터 탭 */}
        <FilterTabs
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />

        {/* 안건 목록 */}
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