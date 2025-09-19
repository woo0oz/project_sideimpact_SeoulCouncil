import { Badge } from './ui/badge'

interface ImpactBadgeProps {
  level: 'high' | 'medium' | 'low'
  text?: string
}

export function ImpactBadge({ level, text }: ImpactBadgeProps) {
  const configs = {
    high: {
      color: 'bg-red-100 text-red-800 border-red-200',
      emoji: '🔥',
      defaultText: '높은 영향'
    },
    medium: {
      color: 'bg-orange-100 text-orange-800 border-orange-200',
      emoji: '⚡',
      defaultText: '보통 영향'
    },
    low: {
      color: 'bg-blue-100 text-blue-800 border-blue-200',
      emoji: '💡',
      defaultText: '낮은 영향'
    }
  }
  
  const config = configs[level]
  
  return (
    <Badge className={`${config.color} font-medium px-2 py-1`}>
      <span className="mr-1">{config.emoji}</span>
      {text || config.defaultText}
    </Badge>
  )
}