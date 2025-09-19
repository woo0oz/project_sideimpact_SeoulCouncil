import { Calendar, MapPin, Users, Clock, ExternalLink } from 'lucide-react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { ImpactBadge } from './ImpactBadge'
import { Separator } from './ui/separator'

interface DetailModalProps {
  isOpen: boolean
  onClose: () => void
  agenda: {
    title: string
    summary: string
    impact: 'high' | 'medium' | 'low'
    impactDescription: string
    district: string
    date: string
    category: string
    fullContent: string
    budget?: string
    implementationDate?: string
    relatedDepartment?: string
  } | null
}

export function DetailModal({ isOpen, onClose, agenda }: DetailModalProps) {
  if (!agenda) return null
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader className="space-y-3">
          <div className="flex items-start justify-between">
            <div className="flex-1 pr-4">
              <div className="flex items-center space-x-2 mb-2">
                <Badge variant="outline" className="text-xs">
                  {agenda.category}
                </Badge>
                <ImpactBadge level={agenda.impact} />
              </div>
              <DialogTitle className="text-lg leading-tight">
                {agenda.title}
              </DialogTitle>
            </div>
          </div>
          
          <div className="flex items-center space-x-4 text-sm text-muted-foreground">
            <div className="flex items-center space-x-1">
              <MapPin className="h-3 w-3" />
              <span>{agenda.district}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Calendar className="h-3 w-3" />
              <span>{agenda.date}</span>
            </div>
          </div>
        </DialogHeader>
        
        <div className="space-y-6 mt-6">
          {/* 영향도 분석 */}
          <div className="bg-gradient-to-r from-orange-50 to-red-50 rounded-lg p-4 border border-orange-100">
            <h4 className="font-semibold text-orange-900 mb-2 flex items-center">
              <span className="mr-2">💡</span>
              내 삶에 미치는 영향
            </h4>
            <p className="text-sm text-orange-800 leading-relaxed">
              {agenda.impactDescription}
            </p>
          </div>
          
          {/* 요약 */}
          <div>
            <h4 className="font-semibold mb-2">📋 안건 요약</h4>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {agenda.summary}
            </p>
          </div>
          
          <Separator />
          
          {/* 상세 정보 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {agenda.budget && (
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="font-medium text-sm">예산 규모</span>
                </div>
                <p className="text-sm text-muted-foreground pl-4">{agenda.budget}</p>
              </div>
            )}
            
            {agenda.implementationDate && (
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4 text-green-600" />
                  <span className="font-medium text-sm">시행 예정일</span>
                </div>
                <p className="text-sm text-muted-foreground pl-6">{agenda.implementationDate}</p>
              </div>
            )}
            
            {agenda.relatedDepartment && (
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Users className="w-4 h-4 text-purple-600" />
                  <span className="font-medium text-sm">담당 부서</span>
                </div>
                <p className="text-sm text-muted-foreground pl-6">{agenda.relatedDepartment}</p>
              </div>
            )}
          </div>
          
          <Separator />
          
          {/* 전문 보기 */}
          <div>
            <h4 className="font-semibold mb-3">📄 회의록 전문</h4>
            <div className="bg-muted/50 rounded-lg p-4 text-sm leading-relaxed">
              {agenda.fullContent}
            </div>
          </div>
          
          {/* 액션 버튼 */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4">
            <Button className="flex-1" variant="outline">
              <ExternalLink className="w-4 h-4 mr-2" />
              원문 보기
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}