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
    <div className="mt-2 text-xs">
      <Button
        variant="ghost"
        size="sm"
        className="flex items-center text-blue-600 hover:text-blue-800 p-0 h-auto"
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
            <div key={index} className="bg-gray-50 p-2 rounded border border-gray-200">
              <div className="flex items-center text-gray-600 mb-1">
                <FileText className="h-3 w-3 mr-1" />
                <span className="font-medium">{doc.metadata?.source || "Document"}</span>
                <span className="ml-auto text-gray-400">Relevance: {(doc.score * 100).toFixed(0)}%</span>
              </div>
              <p className="text-gray-700 text-xs">{doc.text}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
