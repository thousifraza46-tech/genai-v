import { useState, useEffect, useRef } from "react";
import { Send, Loader2, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { API_CONFIG, getApiUrl } from "@/config/api";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
};

// API Configuration
const API_BASE_URL = API_CONFIG.baseURL;

const AIAssistance = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Welcome! I'm here to help you create stunning videos. Ask me anything about video generation, editing tips, or creative ideas!",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session-${Date.now()}`);
  const [apiStatus, setApiStatus] = useState<"checking" | "online" | "offline">("checking");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: input,
          session_id: sessionId,
          mode: "smart",
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);
      setApiStatus("online");
    } catch (error) {
      console.error("Failed to get AI response:", error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "I'm having trouble connecting to the AI service. Please make sure the backend is running.",
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, errorMessage]);
      setApiStatus("offline");
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: "1",
        role: "assistant",
        content: "Welcome! I'm here to help you create stunning videos. Ask me anything about video generation, editing tips, or creative ideas!",
        timestamp: new Date(),
      },
    ]);
  };
  
  return (
    <div className="h-full flex flex-col items-center justify-center p-8">
      <div className="w-full max-w-4xl h-[calc(100vh-12rem)] flex flex-col relative">
        {/* Clear Chat Button - Top Right */}
        <Button
          onClick={handleClearChat}
          variant="ghost"
          size="sm"
          className="absolute top-0 right-0 text-muted-foreground hover:text-foreground z-10"
        >
          <Trash2 className="w-4 h-4 mr-2" />
          Clear Chat
        </Button>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-6 pr-2 scrollbar-hide">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"} animate-fade-in`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-5 py-3 ${
                  message.role === "user"
                    ? "bg-muted text-foreground"
                    : "bg-primary/10 text-foreground border border-primary/20"
                }`}
              >
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                <span className="text-xs text-muted-foreground mt-1 block">
                  {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </span>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start animate-fade-in">
              <div className="bg-primary/10 text-foreground border border-primary/20 rounded-2xl px-5 py-3">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm">Generating response...</span>
                </div>
              </div>  
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="bg-card/80 backdrop-blur-sm rounded-2xl shadow-medium border border-border p-3">
          <div className="flex items-center gap-3">
            <div className="flex-1 min-h-[56px] max-h-[140px] flex items-center">
              <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="Type your message here..."
                className="min-h-[56px] max-h-[140px] resize-none border-0 focus-visible:ring-0 bg-transparent text-base px-2 py-2"
                disabled={isLoading}
              />
            </div>
            
            <Button
              onClick={handleSend}
              size="icon"
              disabled={isLoading || !input.trim()}
              className="rounded-full bg-primary hover:bg-primary/90 text-primary-foreground shadow-soft hover:glow-primary transition-smooth flex-shrink-0 disabled:opacity-50 disabled:cursor-not-allowed h-11 w-11"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIAssistance;
