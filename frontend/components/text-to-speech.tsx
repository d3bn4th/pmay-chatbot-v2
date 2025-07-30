"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Volume2, VolumeX, Loader2 } from "lucide-react"
import { TranslationKey } from "@/hooks/use-translation"

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

interface TextToSpeechProps {
  text: string
  language?: string
  t: (key: TranslationKey) => string
}

export function TextToSpeech({ text, language = "en", t }: TextToSpeechProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  // Cleanup function to stop audio and reset state
  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsPlaying(false);
    setIsLoading(false);
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopAudio();
    };
  }, []);

  const handleSpeak = async () => {
    // If currently playing or loading, stop the audio/processing
    if (isPlaying || isLoading) {
      stopAudio();
      return;
    }

    setIsLoading(true);
    try {
      // Create abort controller for the fetch request
      abortControllerRef.current = new AbortController();
      
      const endpoint =
        language === "hi"
          ? `${BACKEND_URL}/tts/hindi`
          : `${BACKEND_URL}/tts/english`;
      
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
        signal: abortControllerRef.current.signal,
      });
      
      if (!response.ok) throw new Error(t('tts_failed'));
      
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const audioObj = new Audio(url);
      audioRef.current = audioObj;
      
      // Set up audio event handlers
      audioObj.onplay = () => {
        setIsPlaying(true);
        setIsLoading(false);
      };
      
      audioObj.onended = () => {
        setIsPlaying(false);
        setIsLoading(false);
        // Clean up the object URL to prevent memory leaks
        URL.revokeObjectURL(url);
        audioRef.current = null;
      };
      
      audioObj.onerror = () => {
        setIsPlaying(false);
        setIsLoading(false);
        URL.revokeObjectURL(url);
        audioRef.current = null;
        alert(t('tts_playback_error'));
      };
      
      audioObj.onpause = () => {
        setIsPlaying(false);
        setIsLoading(false);
        URL.revokeObjectURL(url);
        audioRef.current = null;
      };
      
      await audioObj.play();
    } catch (error) {
      // Don't show error if it was aborted
      if (error instanceof Error && error.name === 'AbortError') {
        return;
      }
      setIsLoading(false);
      setIsPlaying(false);
      console.error('TTS Error:', error);
      alert(`${t('tts_error')}: ${error}`);
    }
  };

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={handleSpeak}
      className={`h-6 w-6 p-0 transition-colors ${
        isPlaying 
          ? "text-red-500 hover:text-red-600 hover:bg-red-50" 
          : isLoading
          ? "text-orange-500 hover:text-orange-600 hover:bg-orange-50"
          : "text-gray-500 hover:text-blue-600 hover:bg-blue-50"
      }`}
      title={
        isPlaying 
          ? t('stop_speaking') 
          : isLoading 
          ? t('stop_processing') 
          : t('read_aloud')
      }
    >
      {isLoading ? (
        <Loader2 className="h-3 w-3 animate-spin" />
      ) : isPlaying ? (
        <VolumeX className="h-3 w-3" />
      ) : (
        <Volume2 className="h-3 w-3" />
      )}
    </Button>
  );
}
