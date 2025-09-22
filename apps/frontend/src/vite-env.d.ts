/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_ENVIRONMENT: string
  // 필요에 따라 더 많은 환경 변수를 추가할 수 있습니다
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
