# 가지농장 (Gaji Farm)

서울시 구의회 의사결정 요약·개인화 서비스

## 프로젝트 소개

가지농장은 3분 이내에 자신의 삶에 영향있는 지역 의회 안건을 파악할 수 있도록 돕는 반응형 웹 서비스입니다. 사용자는 거주 구와 관심사(교통, 환경, 복지, 경제, 교육 등)를 설정하면 개인화된 의회 안건 요약과 영향도 분석을 받아볼 수 있습니다.

## 프로젝트 구조 (Monorepo)

```
project_sideimpact_SeoulCouncil/
├── apps/
│   ├── frontend/          # React + Vite 프론트엔드
│   └── backend/           # FastAPI 백엔드
├── data/                  # 데이터 파일들
├── packages/              # 공유 패키지들 (필요시)
├── package.json           # 워크스페이스 설정
└── vercel.json           # Vercel 배포 설정
```

## 주요 기능

- 🏛️ **개인화된 의회 안건 추천**: 거주지와 관심사 기반 맞춤형 안건 제공
- 📊 **영향도 분석**: 각 안건이 개인의 삶에 미치는 영향도를 3단계로 표시
- 🔍 **스마트 필터링**: 높은 영향도, 최신 안건, 우리 지역 등 다양한 필터 제공
- 📱 **반응형 디자인**: 모바일과 데스크톱 모두 최적화된 사용 경험
- ⚡ **빠른 정보 습득**: 3분 이내 핵심 정보 파악 가능

## 기술 스택

### Frontend
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **Font**: Pretendard
- **Build Tool**: Vite
- **Icons**: Lucide React
- **Development**: ESLint + TypeScript

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **Migration**: Alembic
- **Validation**: Pydantic
- **Server**: Uvicorn

## 설치 및 실행

### 전체 프로젝트 설정
```bash
# 루트에서 의존성 설치
npm install

# 모든 워크스페이스 설치
npm run install:all
```

### 프론트엔드 개발
```bash
# 프론트엔드 개발 서버 실행
npm run dev

# 또는 직접 실행
cd apps/frontend
npm run dev
```

### 백엔드 개발
```bash
# 백엔드 개발 서버 실행
npm run dev:backend

# 또는 직접 실행
cd apps/backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### 빌드
```bash
# 프론트엔드 빌드
npm run build

# 백엔드 의존성 설치
npm run build:backend
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


### 브라우저 지원
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

