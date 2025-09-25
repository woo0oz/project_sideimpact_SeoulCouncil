import React, { useState } from 'react'
import { MapPin, Tag, ChevronRight, CheckCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Progress } from './ui/progress'

interface OnboardingPageProps {
  onComplete: (data: { district: string; interests: string[] }) => void
  initialDistrict?: string
  initialInterests?: string[]
}

const SEOUL_DISTRICTS = [
  '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
  '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구',
  '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'
]

const INTEREST_CATEGORIES = [
  { id: 'traffic', name: '교통', emoji: '🚗', description: '주차, 도로, 대중교통' },
  { id: 'environment', name: '환경', emoji: '🌱', description: '공원, 쓰레기, 대기질' },
  { id: 'welfare', name: '복지', emoji: '🤝', description: '아동, 노인, 장애인' },
  { id: 'economy', name: '경제', emoji: '💼', description: '상권, 일자리, 예산' },
  { id: 'education', name: '교육', emoji: '📚', description: '학교, 도서관, 평생교육' },
  { id: 'safety', name: '안전', emoji: '🛡️', description: 'CCTV, 방범, 재해대응' },
  { id: 'culture', name: '문화', emoji: '🎭', description: '축제, 문화시설, 예술' },
  { id: 'health', name: '보건', emoji: '🏥', description: '의료, 건강, 위생' }
]

export function OnboardingPage({ onComplete, initialDistrict = '', initialInterests = [] }: OnboardingPageProps) {
  const [step, setStep] = useState(1) // 편집 모드에서도 지역구부터 다시 선택할 수 있도록 1부터 시작
  const [selectedDistrict, setSelectedDistrict] = useState(initialDistrict)
  const [selectedInterests, setSelectedInterests] = useState<string[]>(initialInterests)

  const handleDistrictSelect = (district: string) => {
    setSelectedDistrict(district)
  }

  const handleInterestToggle = (interestId: string) => {
    setSelectedInterests(prev => 
      prev.includes(interestId) 
        ? prev.filter(id => id !== interestId)
        : [...prev, interestId]
    )
  }

  const handleNext = () => {
    if (step === 1 && selectedDistrict) {
      setStep(2)
    } else if (step === 2 && selectedInterests.length > 0) {
      onComplete({
        district: selectedDistrict,
        interests: selectedInterests
      })
    }
  }

  const handleBack = () => {
    if (step === 2) {
      setStep(1)
    }
  }

  const canProceed = step === 1 ? selectedDistrict : selectedInterests.length > 0
  const progress = step === 1 ? 50 : 100

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* 헤더 */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold mb-2">🍆 가지농장</h1>
          <p className="text-muted-foreground">
            {initialDistrict ? '설정을 변경해보세요' : '가까운 지역의 의회 소식을 맞춤형으로 받아보세요'}
          </p>
        </div>

        {/* 진행률 */}
        <div className="mb-6">
          <div className="flex items-center justify-between text-sm text-muted-foreground mb-2">
            <span>설정 진행률</span>
            <span>{step}/2 단계</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              {step === 1 ? (
                <>
                  <MapPin className="h-5 w-5 text-blue-600" />
                  <span>거주지 선택</span>
                </>
              ) : (
                <>
                  <Tag className="h-5 w-5 text-blue-600" />
                  <span>관심 주제 선택</span>
                </>
              )}
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              {step === 1 
                ? '현재 거주하고 계신 서울시 구를 선택해주세요'
                : '관심있는 주제를 선택해주세요 (최소 1개)'
              }
            </p>
          </CardHeader>

          <CardContent className="space-y-4">
            {step === 1 ? (
              // 1단계: 거주지 선택
              <div className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-5 gap-2">
                {SEOUL_DISTRICTS.map((district) => (
                  <button
                    key={district}
                    onClick={() => handleDistrictSelect(district)}
                    className={`p-3 text-sm rounded-lg border transition-all hover:shadow-sm ${
                      selectedDistrict === district
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'bg-white border-gray-200 hover:border-blue-200'
                    }`}
                  >
                    {district}
                  </button>
                ))}
              </div>
            ) : (
              // 2단계: 관심사 선택
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {INTEREST_CATEGORIES.map((category) => (
                  <button
                    key={category.id}
                    onClick={() => handleInterestToggle(category.id)}
                    className={`p-4 text-left rounded-lg border transition-all hover:shadow-sm ${
                      selectedInterests.includes(category.id)
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'bg-white border-gray-200 hover:border-blue-200'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-xl">{category.emoji}</span>
                      <div className="flex-1">
                        <div className="font-medium">{category.name}</div>
                        <div className={`text-xs ${
                          selectedInterests.includes(category.id) 
                            ? 'text-blue-100' 
                            : 'text-muted-foreground'
                        }`}>
                          {category.description}
                        </div>
                      </div>
                      {selectedInterests.includes(category.id) && (
                        <CheckCircle className="h-5 w-5" />
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}

            {/* 선택된 항목 표시 */}
            {step === 1 && selectedDistrict && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <p className="text-sm">
                  <span className="font-medium">선택된 지역:</span> 서울 {selectedDistrict}
                </p>
              </div>
            )}

            {step === 2 && selectedInterests.length > 0 && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <p className="text-sm font-medium mb-2">선택된 관심 주제:</p>
                <div className="flex flex-wrap gap-2">
                  {selectedInterests.map(interestId => {
                    const interest = INTEREST_CATEGORIES.find(cat => cat.id === interestId)
                    return (
                      <Badge key={interestId} variant="secondary">
                        {interest?.emoji} {interest?.name}
                      </Badge>
                    )
                  })}
                </div>
              </div>
            )}

            {/* 버튼 */}
            <div className="flex space-x-3 pt-4">
              {step === 2 && (
                <Button variant="outline" onClick={handleBack} className="flex-1">
                  이전
                </Button>
              )}
              <Button 
                onClick={handleNext}
                disabled={!canProceed}
                className="flex-1"
              >
                {step === 1 ? (
                  <>
                    다음
                    <ChevronRight className="ml-2 h-4 w-4" />
                  </>
                ) : (
                  initialDistrict ? '변경 완료' : '설정 완료'
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* 안내 텍스트 */}
        <p className="text-center text-xs text-muted-foreground mt-4">
          설정은 언제든 변경할 수 있습니다
        </p>
      </div>
    </div>
  )
}