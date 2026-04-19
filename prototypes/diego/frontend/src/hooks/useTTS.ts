import { useCallback, useRef, useState } from "react";

export function useTTS() {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const play = useCallback(
    async (text: string, voice?: string, rate?: string, pitch?: string) => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }

      const formData = new FormData();
      formData.append("text", text);
      if (voice) formData.append("voice", voice);
      if (rate) formData.append("rate", rate);
      if (pitch) formData.append("pitch", pitch);

      const res = await fetch("/api/tts", {
        method: "POST",
        body: formData,
      });
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);

      const audio = new Audio(url);
      audioRef.current = audio;
      setIsPlaying(true);

      audio.onended = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(url);
        audioRef.current = null;
      };

      await audio.play();
    },
    [],
  );

  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setIsPlaying(false);
    }
  }, []);

  return { isPlaying, play, stop };
}
