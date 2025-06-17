"use client"

import { useState } from "react"
import { ChevronDown, ChevronUp, FileText } from "lucide-react"
import { Button } from "@/components/ui/button"

export interface SourceDocument {
  text: string
  score: number
  metadata: {
    source?: string
    title?: string
    author?: string
    date?: string
    page?: number
  }
}

interface SourceDocumentsProps {
  documents: SourceDocument[]
}

export function SourceDocuments({ documents }: SourceDocumentsProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  if (!documents || documents.length === 0) {
    return null
  }

  return (
    <div className="mt-2 text-xs sm:text-sm">
      <Button
        variant="ghost"
        size="sm"
        className="flex items-center text-blue-600 hover:text-blue-800 p-0 h-auto w-full sm:w-auto justify-start sm:justify-center"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {isExpanded ? <ChevronUp className="h-3 w-3 mr-1" /> : <ChevronDown className="h-3 w-3 mr-1" />}
        <span>
          {isExpanded ? "Hide" : "Show"} {documents.length} source{documents.length > 1 ? "s" : ""}
        </span>
      </Button>

      {isExpanded && (
        <div className="mt-2 space-y-2 border-t border-gray-100 pt-2">
          {documents.map((doc, index) => (
            <div key={index} className="bg-gray-50 p-2 sm:p-3 rounded border border-gray-200">
              <div className="flex flex-col sm:flex-row sm:items-center text-gray-600 mb-1 gap-1 sm:gap-0">
                <div className="flex items-center">
                  <FileText className="h-3 w-3 mr-1" />
                  <span className="font-medium">{doc.metadata?.source || "Document"}</span>
                </div>
                <span className="text-gray-400 sm:ml-auto">Relevance: {(doc.score * 100).toFixed(0)}%</span>
              </div>
              <p className="text-gray-700 text-xs sm:text-sm break-words">{doc.text}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
