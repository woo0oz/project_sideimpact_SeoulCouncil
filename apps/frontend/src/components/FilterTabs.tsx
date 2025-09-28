import { Tabs, TabsList, TabsTrigger } from './ui/tabs'
import { Badge } from './ui/badge'
import { Filter } from 'lucide-react'
import type { Agenda, UserPreferences } from '../lib/types'

interface FilterTabsProps {
  activeTab: string
  onTabChange: (value: string) => void
  agendas: Agenda[]
  userPreferences: UserPreferences | null
}

export function FilterTabs({ activeTab, onTabChange, agendas, userPreferences }: FilterTabsProps) {
  // 각 탭별 실제 안건 수 계산
  const getTabCounts = () => {
    const all = agendas.length;
    
    // 우리 동네 데이터 중 높은 영향을 가진 데이터
    const highImpact = agendas.filter(agenda => 
      userPreferences 
        ? agenda.district.includes(userPreferences.district) && agenda.impact === "high"
        : agenda.impact === "high"
    ).length;
    
    // 우리 동네 소식 중 한 달 안의 데이터
    const recent = agendas.filter(agenda => {
      const isRecent = new Date(agenda.date.replace(/\./g, "-")) > 
        new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
      return userPreferences 
        ? agenda.district.includes(userPreferences.district) && isRecent
        : isRecent;
    }).length;
    
    // 우리 동네 전체 소식
    const myArea = agendas.filter(agenda => 
      userPreferences ? agenda.district.includes(userPreferences.district) : false
    ).length;

    return { all, highImpact, recent, myArea };
  };

  const counts = getTabCounts();
  
  const tabs = [
    { value: 'all', label: '전체', count: counts.all },
    { value: 'high-impact', label: '높은 영향', count: counts.highImpact },
    { value: 'recent', label: '최근 안건', count: counts.recent },
    { value: 'my-area', label: '우리 동네', count: counts.myArea }
  ]
  
  return (
    <div className="flex items-center space-x-4 mb-6 overflow-x-auto pb-2">
      <div className="flex items-center space-x-2 text-sm text-muted-foreground whitespace-nowrap">
        <Filter className="h-4 w-4" />
        <span>필터</span>
      </div>
      
      <Tabs value={activeTab} onValueChange={onTabChange} className="flex-1">
        <TabsList className="grid w-full grid-cols-4 lg:w-auto lg:grid-cols-none lg:flex">
          {tabs.map((tab) => (
            <TabsTrigger 
              key={tab.value} 
              value={tab.value}
              className="text-xs lg:text-sm whitespace-nowrap border-2 border-transparent data-[state=active]:border-purple-300 data-[state=active]:bg-transparent data-[state=active]:text-purple-600 hover:border-purple-200 transition-all duration-200"
            >
              <span>{tab.label}</span>
              <Badge 
                variant="secondary" 
                className={`ml-2 text-xs px-1.5 py-0 transition-colors ${
                  activeTab === tab.value 
                    ? 'bg-purple-100 text-purple-700 border-purple-300' 
                    : 'bg-gray-100 text-gray-600'
                }`}
              >
                {tab.count}
              </Badge>
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>
    </div>
  )
}