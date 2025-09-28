import { MapPin, Tag, ChevronRight } from 'lucide-react'
import { Card, CardContent } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'

interface OnboardingCardProps {
  isCompleted?: boolean
  district?: string
  interests?: string[]
  onEdit?: () => void
}

const INTEREST_LABELS: Record<string, string> = {
  traffic: '교통',
  environment: '환경',
  welfare: '복지',
  economy: '경제',
  education: '교육',
  safety: '안전',
  culture: '문화',
  health: '보건'
}

export function OnboardingCard({ isCompleted = false, district, interests = [], onEdit }: OnboardingCardProps) {
  if (isCompleted) {
    const displayInterests = interests.map(id => INTEREST_LABELS[id] || id)
    
    return (
      <Card className="mb-6 bg-gradient-to-r from-orange-50 to-red-50 border-orange-200">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2 text-sm">
                <MapPin className="h-4 w-4 text-orange-600" />
                <span className="font-medium">서울 {district}</span>
              </div>
              <div className="flex items-center space-x-2">
                {displayInterests.slice(0, 3).map((interest) => (
                  <Badge key={interest} variant="secondary" className="text-xs">
                    {interest}
                  </Badge>
                ))}
                {displayInterests.length > 3 && (
                  <span className="text-xs text-muted-foreground">+{displayInterests.length - 3}개</span>
                )}
              </div>
            </div>
            <Button variant="ghost" size="sm" onClick={onEdit}>
              변경
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="mb-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
      <CardContent className="p-6">
        <div className="text-center mb-4">
          <h3 className="text-lg font-semibold mb-2">맞춤 정보를 위한 설정</h3>
          <p className="text-sm text-muted-foreground">
            거주지와 관심사를 설정하면 더 정확한 영향도 분석을 받을 수 있어요
          </p>
        </div>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-white rounded-lg border">
            <div className="flex items-center space-x-3">
              <MapPin className="h-5 w-5 text-blue-600" />
              <div>
                <p className="font-medium">거주지 설정</p>
                <p className="text-sm text-muted-foreground">구 · 동 선택</p>
              </div>
            </div>
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          </div>
          
          <div className="flex items-center justify-between p-3 bg-white rounded-lg border">
            <div className="flex items-center space-x-3">
              <Tag className="h-5 w-5 text-blue-600" />
              <div>
                <p className="font-medium">관심 주제 설정</p>
                <p className="text-sm text-muted-foreground">교통, 환경, 복지 등</p>
              </div>
            </div>
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          </div>
        </div>
        
        <Button className="w-full mt-4">
          1분만에 설정 완료하기
        </Button>
      </CardContent>
    </Card>
  )
}