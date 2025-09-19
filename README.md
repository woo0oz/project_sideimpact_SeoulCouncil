# 가지농장 (Gaji Farm)

서울시 구의회 의사결정 요약·개인화 서비스

## 프로젝트 소개

가지농장은 3분 이내에 자신의 삶에 영향있는 지역 의회 안건을 파악할 수 있도록 돕는 반응형 웹 서비스입니다. 사용자는 거주 구와 관심사(교통, 환경, 복지, 경제, 교육 등)를 설정하면 개인화된 의회 안건 요약과 영향도 분석을 받아볼 수 있습니다.

## 주요 기능

- 🏛️ **개인화된 의회 안건 추천**: 거주지와 관심사 기반 맞춤형 안건 제공
- 📊 **영향도 분석**: 각 안건이 개인의 삶에 미치는 영향도를 3단계로 표시
- 🔍 **스마트 필터링**: 높은 영향도, 최신 안건, 우리 지역 등 다양한 필터 제공
- 📱 **반응형 디자인**: 모바일과 데스크톱 모두 최적화된 사용 경험
- ⚡ **빠른 정보 습득**: 3분 이내 핵심 정보 파악 가능

## 기술 스택

- **Frontend**: React 18 + TypeScript
- **Styling**: Tailwind CSS v4 + shadcn/ui
- **Font**: Pretendard
- **Build Tool**: Vite
- **Icons**: Lucide React

## 설치 및 실행

### 1. 의존성 설치
```bash
npm install
# 또는
yarn install
# 또는
pnpm install
```

### 2. 개발 서버 실행
```bash
npm run dev
# 또는
yarn dev
# 또는
pnpm dev
```

브라우저에서 `http://localhost:5173`으로 접속하여 애플리케이션을 확인할 수 있습니다.

### 3. 빌드
```bash
npm run build
# 또는
yarn build
# 또는
pnpm build
```

## 프로젝트 구조

```
├── components/          # React 컴포넌트
│   ├── ui/             # shadcn/ui 컴포넌트
│   ├── AgendaCard.tsx  # 안건 카드 컴포넌트
│   ├── DetailModal.tsx # 상세보기 모달
│   ├── FilterTabs.tsx  # 필터 탭
│   ├── Header.tsx      # 헤더
│   ├── OnboardingCard.tsx  # 온보딩 완료 카드
│   └── OnboardingPage.tsx  # 온보딩 페이지
├── styles/
│   └── globals.css     # 전역 스타일 (Tailwind CSS v4)
├── App.tsx             # 메인 애플리케이션
└── main.tsx           # 엔트리 포인트
```

## 주요 컴포넌트

- **OnboardingPage**: 거주지와 관심사 설정을 위한 온보딩 페이지
- **FilterTabs**: 전체, 높은 영향도, 최신, 우리 지역 필터 탭
- **AgendaCard**: 의회 안건 요약 카드 (제목, 요약, 영향도, 카테고리 표시)
- **DetailModal**: 안건 상세 정보 모달 (전문, 예산, 시행일 등)
- **ImpactBadge**: 안건 영향도 표시 배지 (높음/보통/낮음)

## 데이터 구조

현재는 목업 데이터를 사용하며, 실제 서비스에서는 API와 연동될 예정입니다.

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.