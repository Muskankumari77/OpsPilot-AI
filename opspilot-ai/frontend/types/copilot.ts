export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatResponse {
  response: string;
  tools_used: string[];
  domains_involved: string[];
}
