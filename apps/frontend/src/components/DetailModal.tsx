import { Calendar, MapPin, ExternalLink } from 'lucide-react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { ImpactBadge } from './ImpactBadge'

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
    originalUrl?: string
  } | null
}

export function DetailModal({ isOpen, onClose, agenda }: DetailModalProps) {
  if (!agenda) return null

  const handleOriginalUrlClick = () => {
    if (agenda.originalUrl) {
      window.open(agenda.originalUrl, '_blank', 'noopener,noreferrer')
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[92vh] flex flex-col bg-white border-0 shadow-2xl">
        <DialogHeader className="space-y-4 pb-6 flex-shrink-0">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-3">
                <Badge 
                  variant="secondary" 
                  className="px-3 py-1 text-xs font-medium bg-gradient-to-r from-purple-100 to-violet-100 text-purple-700 border-0"
                >
                  {agenda.category}
                </Badge>
                <ImpactBadge level={agenda.impact} />
              </div>
              <DialogTitle className="text-xl font-bold leading-tight text-gray-900">
                {agenda.title}
              </DialogTitle>
            </div>
          </div>
          
          <div className="flex items-center space-x-6 text-sm text-gray-600">
            <div className="flex items-center space-x-2">
              <MapPin className="h-4 w-4 text-gray-400" />
              <span className="font-medium">{agenda.district}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Calendar className="h-4 w-4 text-gray-400" />
              <span>{agenda.date}</span>
            </div>
          </div>
        </DialogHeader>
        
        <div className="overflow-y-auto flex-1 px-1 min-h-0">
          <div className="space-y-6 pb-4">
            {/* 영향도 분석 */}
            <div className="bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 rounded-xl p-6 border border-orange-200/50 shadow-sm">
              <div className="flex items-center mb-3">
                <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center mr-3">
                  <span className="text-orange-600 text-lg">💡</span>
                </div>
                <h4 className="font-semibold text-orange-900 text-base">내 삶에 미치는 영향</h4>
              </div>
              <p className="text-orange-800 leading-relaxed text-sm">
                {agenda.impactDescription}
              </p>
            </div>
            
            {/* 요약 */}
            <div className="bg-gray-50 rounded-xl p-6 border border-gray-200/80">
              <div className="flex items-center mb-3">
                <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center mr-3">
                  <span className="text-gray-600 text-lg">📋</span>
                </div>
                <h4 className="font-semibold text-gray-900 text-base">안건 요약</h4>
              </div>
              <p className="text-gray-700 leading-relaxed text-sm">
                {agenda.summary}
              </p>
            </div>
            
            {/* 전문 보기 */}
            <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
              <div className="flex items-center mb-4">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                  <span className="text-blue-600 text-lg">📄</span>
                </div>
                <h4 className="font-semibold text-gray-900 text-base">회의록 전문</h4>
              </div>
              <div className="bg-slate-50 rounded-lg p-5 text-sm leading-relaxed text-gray-700 border border-slate-200">
                {agenda.fullContent}
              </div>        
            </div>
          </div>
        </div>
          
        {/* 액션 버튼 - Fixed position at bottom */}
        <div className="border-t bg-white p-6 flex-shrink-0">
          {agenda.originalUrl ? (
            <Button 
              className="w-full h-12 bg-gradient-to-r from-purple-400 to-violet-400 hover:from-purple-500 hover:to-violet-500 text-white border-0 shadow-md text-base font-medium" 
              onClick={handleOriginalUrlClick}
            >
              <ExternalLink className="w-5 h-5 mr-2" />
              원문 보기
            </Button>
          ) : (
            <Button 
              className="w-full h-12 text-base font-medium" 
              variant="outline" 
              disabled
            >
              <ExternalLink className="w-5 h-5 mr-2 opacity-50" />
              원문이 제공되지 않는 컨텐츠입니다
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}