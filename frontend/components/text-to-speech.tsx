"use client"

import { useState } from "react"
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
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null)

  const handleSpeak = async () => {
    if (isPlaying && audio) {
      audio.pause();
      setIsPlaying(false);
      return;
    }

    setIsLoading(true);
    try {
      const endpoint =
        language === "hi"
          ? `${BACKEND_URL}/tts/hindi`
          : `${BACKEND_URL}/tts/english`;
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (!response.ok) throw new Error(t('tts_failed'));
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const audioObj = new Audio(url);
      setAudio(audioObj);
      audioObj.onplay = () => {
        setIsPlaying(true);
        setIsLoading(false);
      };
      audioObj.onended = () => {
        setIsPlaying(false);
        setIsLoading(false);
      };
      audioObj.onerror = () => {
        setIsPlaying(false);
        setIsLoading(false);
        alert(t('tts_playback_error'));
      };
      audioObj.play();
    } catch (error) {
      setIsLoading(false);
      setIsPlaying(false);
      alert(`${t('tts_error')}: ${error}`);
    }
  };

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={handleSpeak}
      className="h-6 w-6 p-0 text-gray-500 hover:text-blue-600 hover:bg-blue-50"
      title={isPlaying ? t('stop_speaking') : t('read_aloud')}
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
