import { useCallback, useRef, useState } from "react";

export function useAudioRecorder() {
  const [isRecording, setIsRecording] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const startRecording = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    streamRef.current = stream;

    const mediaRecorder = new MediaRecorder(stream, {
      mimeType: MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : "audio/webm",
    });

    chunksRef.current = [];
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };

    mediaRecorderRef.current = mediaRecorder;

    return new Promise<void>((resolve) => {
      mediaRecorder.onstart = () => {
        setIsRecording(true);
        setElapsed(0);

        const start = Date.now();
        timerRef.current = setInterval(() => {
          setElapsed(Math.floor((Date.now() - start) / 1000));
        }, 1000);

        resolve();
      };

      mediaRecorder.start(250);
    });
  }, []);

  const stopRecording = useCallback(async (): Promise<string> => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    return new Promise((resolve, reject) => {
      const mediaRecorder = mediaRecorderRef.current;
      if (!mediaRecorder || mediaRecorder.state === "inactive") {
        setIsRecording(false);
        reject(new Error("No active recorder"));
        return;
      }

      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        const formData = new FormData();
        formData.append("audio", blob, "recording.webm");

        try {
          const res = await fetch("/api/stt", {
            method: "POST",
            body: formData,
          });
          const data = await res.json();
          resolve(data.text || "");
        } catch (err) {
          reject(err);
        }

        if (streamRef.current) {
          streamRef.current.getTracks().forEach((t) => t.stop());
          streamRef.current = null;
        }
        setIsRecording(false);
        setElapsed(0);
      };

      mediaRecorder.stop();
    });
  }, []);

  return { isRecording, elapsed, startRecording, stopRecording };
}
