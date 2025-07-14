"use client"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Cpu } from "lucide-react"

const models = [
  { id: "llama3.2:1b", name: "Llama 3 1B", description: "Llama 3, 1.2B parameters" },
  { id: "llama3.2:3b", name: "Llama 3 3B", description: "Llama 3, 3.2B parameters" },
  { id: "llama3.2:1b-instruct-fp16", name: "Llama 3 1B Instruct FP16", description: "Llama 3, 1.2B, Instruct, FP16" },
  { id: "gemma3:1b-it-qat", name: "Gemma 3 1B IT QAT", description: "Gemma 3, 1B, IT QAT" },
  { id: "gemma3:1b", name: "Gemma 3 1B", description: "Gemma 3, 1B parameters" },
  { id: "gaganyatri/sarvam-2b-v0.5:latest", name: "Sarvam 2B v0.5", description: "Sarvam, 2B parameters, v0.5" }
];

interface ModelSelectorProps {
  selectedModel: string
  onModelChange: (model: string) => void
}

export function ModelSelector({ selectedModel, onModelChange }: ModelSelectorProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center text-sm sm:text-base font-medium text-white">
        <Cpu className="mr-2 h-4 w-4" />
        AI Model
      </div>
      <Select value={selectedModel} onValueChange={onModelChange}>
        <SelectTrigger className="w-full h-24 py-6 bg-blue-700 border-blue-600 text-white hover:bg-blue-600 text-sm sm:text-base">
          <SelectValue placeholder="Select model">
            {selectedModel && (() => {
              const model = models.find(m => m.id === selectedModel);
              if (!model) return null;
              return (
                <div className="flex flex-col items-start leading-tight">
                  <span className="font-medium text-sm">{model.name}</span>
                  <span className="text-xs text-gray-400">{model.description}</span>
                </div>
              );
            })()}
          </SelectValue>
        </SelectTrigger>
        <SelectContent className="max-h-[300px] sm:max-h-[400px]">
          {models.map((model) => (
            <SelectItem key={model.id} value={model.id} className="py-2">
              <div className="flex flex-col items-start">
                <span className="font-medium text-base">{model.name}</span>
                <span className="text-xs text-gray-500">{model.description}</span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}
