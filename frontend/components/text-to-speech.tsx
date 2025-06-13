"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Volume2, VolumeX, Loader2 } from "lucide-react"

interface TextToSpeechProps {
  text: string
  language?: string
}

export function TextToSpeech({ text, language = "en" }: TextToSpeechProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleSpeak = async () => {
    if (isPlaying) {
      // Stop current speech
      window.speechSynthesis.cancel()
      setIsPlaying(false)
      return
    }

    if (!window.speechSynthesis) {
      alert("Text-to-speech is not supported in your browser")
      return
    }

    setIsLoading(true)

    try {
      // Clean the text by removing markdown and HTML
      const cleanText = text
        .replace(/[#*`]/g, "") // Remove markdown symbols
        .replace(/<[^>]*>/g, "") // Remove HTML tags
        .replace(/\n+/g, " ") // Replace newlines with spaces
        .trim()

      const utterance = new SpeechSynthesisUtterance(cleanText)

      // Set language based on selection
      const langMap: { [key: string]: string } = {
        en: "en-US",
        hi: "hi-IN",
        bn: "bn-IN",
        te: "te-IN",
        mr: "mr-IN",
        ta: "ta-IN",
        gu: "gu-IN",
        kn: "kn-IN",
        ml: "ml-IN",
        pa: "pa-IN",
      }

      utterance.lang = langMap[language] || "en-US"
      utterance.rate = 0.9
      utterance.pitch = 1
      utterance.volume = 0.8

      utterance.onstart = () => {
        setIsPlaying(true)
        setIsLoading(false)
      }

      utterance.onend = () => {
        setIsPlaying(false)
        setIsLoading(false)
      }

      utterance.onerror = () => {
        setIsPlaying(false)
        setIsLoading(false)
        alert("Error occurred during text-to-speech")
      }

      window.speechSynthesis.speak(utterance)
    } catch (error) {
      setIsLoading(false)
      setIsPlaying(false)
      console.error("Text-to-speech error:", error)
    }
  }

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={handleSpeak}
      className="h-6 w-6 p-0 text-gray-500 hover:text-blue-600 hover:bg-blue-50"
      title={isPlaying ? "Stop speaking" : "Read aloud"}
    >
      {isLoading ? (
        <Loader2 className="h-3 w-3 animate-spin" />
      ) : isPlaying ? (
        <VolumeX className="h-3 w-3" />
      ) : (
        <Volume2 className="h-3 w-3" />
      )}
    </Button>
  )
}
