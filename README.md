````markdown
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
- **Styling**: Tailwind CSS + shadcn/ui
- **Font**: Pretendard
- **Build Tool**: Vite
- **Icons**: Lucide React
- **Development**: ESLint + TypeScript

## 설치 및 실행

### 1. 의존성 설치
```bash
npm install
# 또는
yarn install
# 또는
pnpm install
```

### 2. 환경변수 설정
```bash
# .env.local 파일 생성
cp .env.example .env.local

# 환경변수 설정
REACT_APP_API_URL=http://localhost:3001/api  # 백엔드 API URL
REACT_APP_ENVIRONMENT=development           # 환경 구분
```

### 3. 개발 서버 실행
```bash
npm run dev
# 또는
yarn dev
# 또는
pnpm dev
```

브라우저에서 `http://localhost:5173`으로 접속하여 애플리케이션을 확인할 수 있습니다.

### 4. 빌드
```bash
npm run build
# 또는
yarn build
# 또는
pnpm build
```

### 5. 린팅
```bash
npm run lint
# 또는
yarn lint
# 또는
pnpm lint
```

### 6. 미리보기
```bash
npm run preview
# 또는
yarn preview
# 또는
pnpm preview
```

## 프로젝트 구조

```
├── components/              # React 컴포넌트
│   ├── ui/                 # shadcn/ui 기본 컴포넌트
│   │   ├── button.tsx      # 버튼 컴포넌트
│   │   ├── card.tsx        # 카드 컴포넌트
│   │   ├── dialog.tsx      # 모달/다이얼로그
│   │   ├── progress.tsx    # 프로그레스 바
│   │   ├── tabs.tsx        # 탭 컴포넌트
│   │   └── ...             # 기타 UI 컴포넌트들
│   ├── figma/              # Figma 관련 컴포넌트
│   │   └── ImageWithFallback.tsx  # 이미지 폴백 컴포넌트
│   ├── AgendaCard.tsx      # 안건 카드 컴포넌트
│   ├── DetailModal.tsx     # 상세보기 모달
│   ├── FilterTabs.tsx      # 필터 탭
│   ├── Header.tsx          # 헤더
│   ├── ImpactBadge.tsx     # 영향도 배지
│   ├── OnboardingCard.tsx  # 온보딩 완료 카드
│   └── OnboardingPage.tsx  # 온보딩 페이지
├── lib/                    # 유틸리티 및 API
│   ├── api.ts             # API 호출 함수들
│   └── types.ts           # TypeScript 타입 정의
├── styles/
│   └── globals.css         # 전역 스타일 (Tailwind CSS)
├── guidelines/
│   └── Guidelines.md       # 개발 가이드라인
├── App.tsx                 # 메인 애플리케이션
├── main.tsx               # 엔트리 포인트
├── index.html             # HTML 템플릿
├── vite.config.ts         # Vite 설정
├── tailwind.config.js     # Tailwind CSS 설정
├── postcss.config.js      # PostCSS 설정
├── tsconfig.json          # TypeScript 설정
├── tsconfig.node.json     # Node.js TypeScript 설정
└── eslint.config.js       # ESLint 설정
```

## 주요 컴포넌트

### 페이지 컴포넌트
- **OnboardingPage**: 거주지와 관심사 설정을 위한 온보딩 페이지
- **App**: 메인 애플리케이션 컴포넌트

### UI 컴포넌트
- **Header**: 상단 헤더 (로고, 네비게이션)
- **FilterTabs**: 전체, 높은 영향도, 최신, 우리 지역 필터 탭
- **AgendaCard**: 의회 안건 요약 카드 (제목, 요약, 영향도, 카테고리 표시)
- **DetailModal**: 안건 상세 정보 모달 (전문, 예산, 시행일 등)
- **OnboardingCard**: 온보딩 완료 후 표시되는 요약 카드
- **ImpactBadge**: 안건 영향도 표시 배지 (높음/보통/낮음)

### shadcn/ui 컴포넌트
프로젝트에서 사용하는 주요 shadcn/ui 컴포넌트들:
- **Button, Card, Dialog**: 기본 UI 요소
- **Progress, Tabs**: 인터랙션 컴포넌트
- **Badge, Avatar**: 표시 컴포넌트
- **Form, Input, Select**: 폼 관련 컴포넌트

## API 연동

현재는 목업 데이터를 사용하며, 향후 백엔드 API와 연동될 예정입니다.

### 백엔드 연결 준비사항

프로젝트는 백엔드 연결을 위해 다음과 같이 준비되어 있습니다:

- **API 레이어 분리**: `lib/api.ts`에서 모든 API 호출 관리
- **타입 정의**: `lib/types.ts`에서 데이터 타입 정의
- **환경변수 설정**: API URL 등 설정 가능
- **에러 처리**: API 실패시 fallback 로직 포함
- **로딩 상태**: 사용자 경험을 위한 로딩 표시

### 예정된 API 엔드포인트

```typescript
// 개인화된 안건 조회
POST /api/agendas/personalized
Body: { district: string, interests: string[] }

// 전체 안건 목록
GET /api/agendas?district=&category=&impact=

// 특정 안건 상세
GET /api/agendas/:id

// 사용자 선호도 저장
POST /api/user/preferences
Body: { district: string, interests: string[] }

// 지역구 목록
GET /api/districts

// 관심사 카테고리
GET /api/categories
```

### 백엔드 연결시 수정 사항

백엔드가 준비되면 `lib/api.ts`에서 다음 부분만 수정하면 됩니다:

1. `IS_DEVELOPMENT` 조건 제거
2. 목업 데이터 대신 실제 API 호출 사용
3. 에러 처리 및 응답 형식 조정

## 환경 설정

### 환경 변수
```env
REACT_APP_API_URL=http://localhost:3001/api  # 백엔드 API URL
REACT_APP_ENVIRONMENT=development           # 환경 구분 (development/production)
```

### 브라우저 지원
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 개발 가이드라인

자세한 개발 가이드라인은 [Guidelines.md](guidelines/Guidelines.md)를 참조하세요.

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
````