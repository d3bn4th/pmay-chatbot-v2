"use client"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Cpu } from "lucide-react"

const models = [
  { id: "us.amazon.nova-pro-v1:0", name: "Nova Pro", description: "High-quality responses" },
  { id: "us.amazon.nova-lite-v1:0", name: "Nova Lite", description: "Fast responses" },
  { id: "us.amazon.nova-micro-v1:0", name: "Nova Micro", description: "Lightweight model" },
  { id: "anthropic.claude-3-sonnet-20240229-v1:0", name: "Claude 3 Sonnet", description: "Balanced performance" },
  { id: "anthropic.claude-3-haiku-20240307-v1:0", name: "Claude 3 Haiku", description: "Fast and efficient" },
]

interface ModelSelectorProps {
  selectedModel: string
  onModelChange: (model: string) => void
}

export function ModelSelector({ selectedModel, onModelChange }: ModelSelectorProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center text-sm font-medium text-white">
        <Cpu className="mr-2 h-4 w-4" />
        AI Model
      </div>
      <Select value={selectedModel} onValueChange={onModelChange}>
        <SelectTrigger className="w-full bg-blue-700 border-blue-600 text-white hover:bg-blue-600">
          <SelectValue placeholder="Select model" />
        </SelectTrigger>
        <SelectContent>
          {models.map((model) => (
            <SelectItem key={model.id} value={model.id}>
              <div className="flex flex-col items-start">
                <span className="font-medium">{model.name}</span>
                <span className="text-xs text-gray-500">{model.description}</span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}
