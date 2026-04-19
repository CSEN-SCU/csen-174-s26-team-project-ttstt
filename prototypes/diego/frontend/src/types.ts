export interface Message {
  id: string;
  source: "voice" | "text";
  text: string;
  timestamp: number;
}
