import { Calendar, MapPin, ChevronRight } from 'lucide-react'
import { Card, CardContent, CardHeader } from './ui/card'
import { Badge } from './ui/badge'
import { ImpactBadge } from './ImpactBadge'

interface AgendaCardProps {
  title: string
  summary: string
  impact: 'high' | 'medium' | 'low'
  impactDescription: string
  district: string
  date: string
  category: string
  onClick?: () => void
}

export function AgendaCard({
  title,
  summary,
  impact,
  impactDescription,
  district,
  date,
  category,
  onClick
}: AgendaCardProps) {
  // category가 배열이면 여러 Badge로, 아니면 기존대로
  const categories = Array.isArray(category) ? category : [category];
  return (
    <Card className="mb-4 hover:shadow-md transition-shadow cursor-pointer" onClick={onClick}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              {categories.map((cat, idx) => (
                <Badge key={cat + idx} variant="outline" className="text-xs bg-gradient-to-r from-purple-50 to-violet-50 text-purple-700 border-purple-200">
                  {cat}
                </Badge>
              ))}
              <ImpactBadge level={impact} />
            </div>
            <h3 className="font-semibold leading-tight mb-2">{title}</h3>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <p className="text-sm text-muted-foreground mb-3 leading-relaxed">
          {summary}
        </p>
        
        <div className="bg-gradient-to-r from-orange-50 to-red-50 rounded-lg p-3 mb-3 border border-orange-100">
          <p className="text-sm font-medium text-orange-900 mb-1">💡 내 삶에 미치는 영향</p>
          <p className="text-sm text-orange-800">{impactDescription}</p>
        </div>
        
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <MapPin className="h-3 w-3" />
              <span>{district}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Calendar className="h-3 w-3" />
              <span>{date}</span>
            </div>
          </div>
          <div className="flex items-center space-x-1 text-primary">
            <span className="text-sm font-medium">상세보기</span>
            <ChevronRight className="h-3 w-3" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}