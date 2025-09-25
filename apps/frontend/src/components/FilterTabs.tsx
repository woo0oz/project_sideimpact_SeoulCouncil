import { Tabs, TabsList, TabsTrigger } from './ui/tabs'
import { Badge } from './ui/badge'
import { Filter } from 'lucide-react'

interface FilterTabsProps {
  activeTab: string
  onTabChange: (value: string) => void
}

export function FilterTabs({ activeTab, onTabChange }: FilterTabsProps) {
  const tabs = [
    { value: 'all', label: '전체', count: 12 },
    { value: 'high-impact', label: '높은 영향', count: 3 },
    { value: 'recent', label: '최근 안건', count: 8 },
    { value: 'my-area', label: '우리 동네', count: 5 }
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