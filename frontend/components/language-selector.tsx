"use client"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Languages } from "lucide-react"

const languages = [
  { code: "en", name: "English", nativeName: "English" },
  { code: "hi", name: "Hindi", nativeName: "हिन्दी" },
];

interface LanguageSelectorProps {
  selectedLanguage: string
  onLanguageChange: (language: string) => void
}

export function LanguageSelector({ selectedLanguage, onLanguageChange }: LanguageSelectorProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center text-sm sm:text-base font-medium text-white">
        <Languages className="mr-2 h-4 w-4" />
        Language
      </div>
      <Select value={selectedLanguage} onValueChange={onLanguageChange}>
        <SelectTrigger className="w-full bg-blue-700 border-blue-600 text-white hover:bg-blue-600 text-sm sm:text-base">
          <SelectValue placeholder="Select language" />
        </SelectTrigger>
        <SelectContent className="max-h-[300px] sm:max-h-[400px]">
          {languages.map((lang) => (
            <SelectItem key={lang.code} value={lang.code} className="py-2">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between w-full gap-1 sm:gap-0">
                <span className="text-sm sm:text-base">{lang.name}</span>
                <span className="text-xs sm:text-sm text-gray-500 ml-3 sm:ml-4">{lang.nativeName}</span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}
