import { useState } from 'react'
import { Search, Settings, X } from 'lucide-react'
import { Button } from './ui/button'
import { Input } from './ui/input'

interface HeaderProps {
  searchQuery?: string
  onSearchChange?: (query: string) => void
}

export function Header({ searchQuery = '', onSearchChange }: HeaderProps) {
  const [isMobileSearchOpen, setIsMobileSearchOpen] = useState(false)
  return (
    <header className="sticky top-0 z-50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        {!isMobileSearchOpen ? (
          <>
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-bold text-primary">🍆 가지농장</h1>
              <p className="hidden sm:block text-sm text-muted-foreground">가까운 지역의 의회 소식</p>
            </div>
            
            <div className="flex-1 max-w-sm mx-4 hidden md:block">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input 
                  placeholder="키워드, 주제로 검색하세요"
                  className="pl-10"
                  value={searchQuery}
                  onChange={(e) => onSearchChange?.(e.target.value)}
                />
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button 
                variant="ghost" 
                size="icon" 
                className="md:hidden"
                onClick={() => setIsMobileSearchOpen(true)}
              >
                <Search className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon">
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </>
        ) : (
          <div className="flex items-center space-x-2 w-full">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input 
                  placeholder="키워드, 주제로 검색하세요"
                  className="pl-10"
                  value={searchQuery}
                  onChange={(e) => onSearchChange?.(e.target.value)}
                  autoFocus
                />
              </div>
            </div>
            <Button 
              variant="ghost" 
              size="icon"
              onClick={() => setIsMobileSearchOpen(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>
    </header>
  )
}