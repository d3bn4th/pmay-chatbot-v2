"use client"

import { useRef, useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Loader2, Info, Home, FileText, Settings, ArrowLeft } from "lucide-react"
import Image from "next/image"
import { SourceDocument, SourceDocuments } from "@/components/source-documents"
import { useMobile } from "@/hooks/use-mobile"
import MarkdownMessage from "@/components/markdown-message"
import { LanguageSelector } from "@/components/language-selector"
import DocumentUpload from "@/components/document-upload";
import { ModelSelector } from "@/components/model-selector";
import SidebarQuickLinks from "@/components/sidebar-quick-links";

// Define a custom message type that includes an 'id' and optional sources
interface ChatMessageType {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: SourceDocument[];
}

// Thinking dots animation component
const ThinkingDots = () => {
  return (
    <div className="flex space-x-1 items-center">
      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
    </div>
  );
};

// Add this above the ChatPage component
const SAMPLE_QUESTIONS = [
  "What is PMAY?",
  "How to apply for PMAY?",
  "What is the eligibility criteria?",
  "What is Pradhan Mantri Awas Yojana (Urban) and its objectives and scope?",
  "What is In-Situ Slum Redevelopment?",
  "What is Credit Linked Subsidy Scheme (CLSS)?",
  "What is Affordable Housing in Partnership (AHP)?",
  "What is Beneficiary led individual house construction enhancements (BLC)?",
  "Who is defined as a beneficiary under Pradhan Mantri Awas Yojana (Urban) Scheme?",
];

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessageType[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const [isAssistantStreaming, setIsAssistantStreaming] = useState(false)
  const [selectedLanguage, setSelectedLanguage] = useState("en")
  const [showSampleQuestions, setShowSampleQuestions] = useState(false);
  // New state for abort controller and last user message
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  const [lastUserMessage, setLastUserMessage] = useState<ChatMessageType | null>(null);
  const [selectedModel, setSelectedModel] = useState("llama3.2:1b");

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const isMobile = useMobile()
  const [showSidebar, setShowSidebar] = useState(!isMobile)
  const [activeSection, setActiveSection] = useState("home")
  const [userMessageCount, setUserMessageCount] = useState(0); // New state to trigger scroll
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    setShowSidebar(!isMobile)
  }, [isMobile])

  // New useEffect for scrolling only when user sends a message
  useEffect(() => {
    if (userMessageCount > 0 && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
      // console.log("User message sent, scrolling to end.", messagesEndRef.current);
    }
  }, [userMessageCount]);

  useEffect(() => {
    if (error) {
      // console.error("Chat error object:", error) // Changed from useChat error
    }
  }, [error])

  useEffect(() => {
    // Only show on first visit and if no messages have been sent
    if (typeof window !== 'undefined') {
      const hasVisited = localStorage.getItem('pmay_has_visited');
      if (!hasVisited && messages.length === 0) {
        setShowSampleQuestions(true);
      }
    }
  }, [messages.length]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);
    if (showSampleQuestions) {
      setShowSampleQuestions(false);
      if (typeof window !== 'undefined') {
        localStorage.setItem('pmay_has_visited', 'true');
      }
    }
  };

  const showWelcomeMessage = messages.length === 0 && !isLoading && !error

  const handleSubmit = async (e?: React.FormEvent<HTMLFormElement>, overrideMessage?: ChatMessageType) => {
    if (e) e.preventDefault();
    const messageToSend = overrideMessage || {
      id: Date.now().toString(),
      role: 'user',
      content: input,
    };
    if (!messageToSend.content.trim() || isLoading) return;

    if (!overrideMessage) {
      setMessages((prevMessages) => [...prevMessages, messageToSend]);
      setInput('');
      setUserMessageCount(prevCount => prevCount + 1); // Increment to trigger scroll
    }
    setIsLoading(true);
    setError(null);
    setLastUserMessage(messageToSend);
    const newAbortController = new AbortController();
    setAbortController(newAbortController);
    const newAssistantMessageId = `ai-response-${Date.now()}`;
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ messages: [messageToSend], model: selectedModel }),
        signal: newAbortController.signal,
      });
      if (!response.ok || !response.body) {
        const errorText = await response.text();
        throw new Error(`API request failed with status ${response.status}: ${errorText}`);
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantResponseContent = '';
      let assistantSources: SourceDocument[] = [];
      setIsAssistantStreaming(true);
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        const sseMessages = chunk.split('\n\n').filter(msg => msg.startsWith('data: ')).map(msg => msg.substring(6));
        for (const sseMessage of sseMessages) {
          try {
            const parsedData = JSON.parse(sseMessage);
            if (parsedData.type === 'text') {
              const content = parsedData.content;
              if (content) {
                assistantResponseContent += content;
              }
            } else if (parsedData.type === 'sources') {
              if (parsedData.sources) {
                assistantSources = parsedData.sources;
              }
            }
            setMessages((prevMessages) => {
              const existingAssistantMessageIndex = prevMessages.findIndex(
                (msg) => msg.id === newAssistantMessageId
              );
              if (existingAssistantMessageIndex !== -1) {
                // Update existing assistant message
                return prevMessages.map((msg, index) =>
                  index === existingAssistantMessageIndex
                    ? { ...msg, content: assistantResponseContent, sources: assistantSources }
                    : msg
                );
              } else {
                // Add new assistant message (first chunk)
                return [
                  ...prevMessages,
                  {
                    id: newAssistantMessageId,
                    role: 'assistant',
                    content: assistantResponseContent,
                    sources: assistantSources
                  },
                ];
              }
            });
          } catch (jsonError) {
            console.error('Failed to parse SSE message:', sseMessage, jsonError);
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof DOMException && err.name === 'AbortError') {
        setMessages((prevMessages) => [
          ...prevMessages,
          {
            id: Date.now().toString(),
            role: 'assistant',
            content: 'Response stopped by user.',
          },
        ]);
      } else if (err instanceof Error) {
        console.error('Error during streaming:', err);
        setError(err);
        setMessages((prevMessages) => [
          ...prevMessages,
          {
            id: Date.now().toString(),
            role: 'assistant',
            content: 'I apologize, but I encountered an error while processing your request. Please try again.',
          },
        ]);
      } else {
        setError(new Error('An unknown error occurred.'));
        setMessages((prevMessages) => [
          ...prevMessages,
          {
            id: Date.now().toString(),
            role: 'assistant',
            content: 'I apologize, but I encountered an error while processing your request. Please try again.',
          },
        ]);
      }
    } finally {
      setIsLoading(false);
      setIsAssistantStreaming(false);
      setAbortController(null);
    }
  };

  // Stop response handler
  const handleStopResponse = () => {
    if (abortController) {
      abortController.abort();
    }
  };

  // Regenerate response handler
  const handleRegenerate = () => {
    if (lastUserMessage) {
      handleSubmit(undefined, lastUserMessage);
    }
  };

  // Add handler for sample question click
  const handleSampleQuestionClick = (question: string) => {
    setInput(question);
    if (showSampleQuestions) {
      setShowSampleQuestions(false);
      if (typeof window !== 'undefined') {
        localStorage.setItem('pmay_has_visited', 'true');
      }
    }
    // Optionally focus the input
    formRef.current?.querySelector('input')?.focus();
    // Submit the form programmatically after setting input
    setTimeout(() => {
      if (formRef.current) {
        formRef.current.requestSubmit();
      }
    }, 0);
  };

  return (
    <div className="flex flex-col h-screen bg-[#FAFAF6]">
      {/* Sidebar */}
      <div
        className={`fixed top-0 left-0 h-screen z-50 ${
          showSidebar ? "w-80" : "w-0 -ml-80"
        } bg-blue-800 text-white transition-all duration-300 ease-in-out overflow-hidden
        ${isMobile ? "shadow-xl" : ""}`}
      >
        <div className="p-4 h-full flex flex-col">
          {/* Desktop-only: MoHUA and PMAY logos above the title */}
          <div className="hidden lg:flex justify-center items-center mb-4">
            <Image
              src="/pmay-logo-new.png"
              alt="PMAY Logo"
              width={300}
              height={200}
              className="object-contain rounded-lg shadow bg-white p-2"
              priority
            />
          </div>
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-xl font-bold w-full text-center">PMAY Chatbot</h1>
            {isMobile && (
              <Button
                variant="ghost"
                size="icon"
                className="text-white hover:bg-blue-700 absolute right-4"
                onClick={() => setShowSidebar(false)}
              >
                <ArrowLeft className="h-6 w-6" />
              </Button>
            )}
          </div>

          <nav className="space-y-1 mb-6">
            <Button
              variant="ghost"
              className={`w-full justify-start text-white hover:bg-blue-700 text-base ${
                activeSection === "home" ? "bg-blue-700" : ""
              }`}
              onClick={() => setActiveSection("home")}
            >
              <Home className="mr-2 h-5 w-5" />
              Home
            </Button>
            <Button
              variant="ghost"
              className={`w-full justify-start text-white hover:bg-blue-700 text-base ${
                activeSection === "documents" ? "bg-blue-700" : "" 
              }`}
              onClick={() => setActiveSection("documents")}
            >
              <FileText className="mr-2 h-5 w-5" />
              Documents
            </Button>
            <Button
              variant="ghost"
              className={`w-full justify-start text-white hover:bg-blue-700 text-base ${
                activeSection === "settings" ? "bg-blue-700" : "" 
              }`}
              onClick={() => setActiveSection("settings")}
            >
              <Settings className="mr-2 h-5 w-5" />
              Settings
            </Button>
          </nav>
          {/* Show DocumentUpload in sidebar when Documents is selected */}
          {activeSection === "documents" && (
            <div className="mt-2">
              <h2 className="text-lg font-semibold mb-4">Upload Documents</h2>
              <DocumentUpload />
            </div>
          )}
          {/* Language Selector and Model Selector only in Settings */}
          {activeSection === "settings" && (
            <>
              <div className="mb-8 px-2 pl-2">
                <LanguageSelector
                  selectedLanguage={selectedLanguage}
                  onLanguageChange={setSelectedLanguage}
                />
              </div>
              <div className="mb-8 px-2 pl-2">
                <ModelSelector selectedModel={selectedModel} onModelChange={setSelectedModel} />
              </div>
            </>
          )}

          {/* Dynamic Content Based on Active Section */}
          <div className="flex-1 overflow-y-auto">
            {activeSection === "home" && (
              <SidebarQuickLinks />
            )}
          </div>
          {/* Remove QuickActions from here */}
        </div>
      </div>

      {/* Main Content */}
      <div className={`flex-1 flex flex-col h-full ${!isMobile && showSidebar ? "ml-80" : "ml-0"} bg-[#FAFAF6]`}>
        {/* Centered Chat Card */}
        <div className="flex-1 flex flex-col items-center">
          <div className="w-full max-w-5xl flex flex-col flex-1 h-full bg-[#FAFAF6] rounded-2xl p-8 relative">
            {/* Scrollable Chat Messages Area */}
            <div className="flex-1 overflow-auto pb-32 bg-[#FAFAF6]"> {/* Reduced bottom padding for tighter spacing */}
              <div
                className={`flex flex-col px-4 md:px-6 bg-[#FAFAF6] pt-6 pb-8
                ${showWelcomeMessage ? "items-center justify-center" : "items-stretch justify-start"}`}
              >
                {/* Welcome Message Section */}
                {showWelcomeMessage && (
                  <div className="text-center p-8">
                    <div className="space-y-4 mt-2">
                      <div className="mx-auto bg-white border-2 border-orange-200 shadow-lg w-44 h-44 flex items-center justify-center rounded-full overflow-hidden">
                        <Image
                          src="/chatbot-logo.png"
                          alt="Chatbot Logo"
                          width={140}
                          height={140}
                          className="object-contain mx-auto"
                          style={{ maxHeight: '90%', maxWidth: '90%' }}
                        />
                      </div>
                      
                      <h3 className="text-3xl font-bold text-blue-800">PMAY Chatbot</h3>
                      <p className="text-lg text-gray-600 max-w-md mx-auto">
                        Ask questions about the Pradhan Mantri Awas Yojana (PMAY) scheme and get accurate,
                        context-aware responses.
                      </p>
                      <div className="flex items-center justify-center mt-3">
                        <Info className="h-4 w-4 text-blue-600 mr-2" />
                        <span className="text-sm text-blue-600">Powered by RAG with cross-encoder re-ranking</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Initial Loading Spinner */}
                {isLoading && messages.length === 0 && (
                  <div className="flex-1 flex items-center justify-center">
                    <Loader2 className="h-12 w-12 text-blue-600 animate-spin" />
                  </div>
                )}

                {/* Error Message */}
                {error && (
                  <div className="flex-1 flex items-center justify-center text-center p-8">
                    <div className="space-y-3 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
                      <svg
                        className="h-12 w-12 mx-auto text-red-500"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.1-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                        />
                      </svg>
                      <h3 className="text-xl font-semibold">Oops! Something went wrong.</h3>
                      <p className="text-sm">{error.message || "Please try again later."}</p>
                      <Button onClick={() => window.location.reload()} variant="destructive" size="sm">
                        Refresh
                      </Button>
                    </div>
                  </div>
                )}

                {/* Messages List */}
                {messages.length > 0 && (
                  <div className="space-y-6 w-full">
                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex items-start gap-3 ${message.role === "user" ? "justify-end" : "justify-start"} animate-fade-in-slide-up`}
                      >
                        {message.role === "assistant" && (
                          <Avatar className="h-10 w-10 border border-gray-200 shadow-md">
                            <div className="rounded-full w-full h-full bg-white flex items-center justify-center">
                              <Image
                                src="/chatbot-avatar.png"
                                alt="bot-avatar"
                                width={30}
                                height={30}
                                className="rounded-full"
                              />
                            </div>
                          </Avatar>
                        )}
                        <div
                          className={`relative w-fit overflow-hidden max-w-[80%] rounded-lg px-4 pb-2 pt-3 ${message.role === "user" ? "bg-blue-700 text-white" : "bg-gray-100 text-gray-800"}`}
                        >
                          <div className={`prose prose-sm prose-blue prose-a:text-blue-600 prose-a:underline leading-normal break-words ${message.role === "user" ? "text-white" : "text-gray-900"}`}>
                            {message.role === "assistant" ? (
                              <MarkdownMessage>{message.content}</MarkdownMessage>
                            ) : (
                              message.content
                            )}
                          </div>
                          {message.sources && message.sources.length > 0 && message.role !== "user" && (
                            <SourceDocuments documents={message.sources} />
                          )}
                          {/* Thumbs up/down for assistant messages */}
                          {message.role === "assistant" && (
                            <></>
                          )}
                        </div>
                        {message.role === "user" && (
                          <Avatar className="h-10 w-10 border border-gray-200 shadow-md">
                            <AvatarFallback className="bg-gray-300 text-gray-800 text-xs">You</AvatarFallback>
                          </Avatar>
                        )}
                      </div>
                    ))}
                    {isLoading && !isAssistantStreaming && (
                      <div className="flex items-start gap-3">
                        <Avatar className="h-10 w-10 border border-gray-200 shadow-md">
                          <div className="rounded-full w-full h-full bg-white flex items-center justify-center">
                            <Image
                              src="/bot-avatar.png"
                              alt="bot-avatar"
                              width={30}
                              height={30}
                              className="rounded-full"
                            />
                          </div>
                        </Avatar>
                        <div className="relative w-fit overflow-hidden max-w-[80%] rounded-lg px-4 pb-2 pt-3 bg-gray-100 text-gray-800">
                          <ThinkingDots />
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </div>
                )}
              </div>
            </div>
            {/* White background to hide chat below input */}
            <div className="fixed bottom-0 left-0 right-0 h-24 bg-[#FAFAF6] z-40" />
            {/* Sample Questions Bar */}
            <div className="fixed bottom-24 left-74 right-0 z-50 px-4 mb-0 pointer-events-none">
              <div className="mx-auto w-full max-w-3xl flex gap-3 overflow-x-auto pointer-events-auto py-1 px-2 scrollbar-none" style={{ WebkitOverflowScrolling: 'touch', scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
                {SAMPLE_QUESTIONS.map((q, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="whitespace-nowrap bg-blue-50 hover:bg-blue-100 border border-blue-200 text-blue-800 rounded-full px-6 py-3 text-sm font-medium shadow transition focus:outline-none focus:ring-2 focus:ring-blue-400"
                    onClick={() => handleSampleQuestionClick(q)}
                    tabIndex={0}
                    style={{ marginTop: 4, marginBottom: 4 }}
                  >
                    {q}
                  </button>
                ))}
                <style>{`.scrollbar-none::-webkit-scrollbar { display: none; } .scrollbar-none { -ms-overflow-style: none; scrollbar-width: none; }`}</style>
              </div>
            </div>
            {/* Centered, rectangle chat input at the bottom of the viewport */}
            <div className="fixed bottom-0 left-74 right-0 z-50 px-4 mb-4 pointer-events-none">
              <form ref={formRef} onSubmit={handleSubmit} className="mx-auto flex items-center w-full max-w-3xl bg-white rounded-xl shadow-2xl border border-gray-100 px-6 py-3 gap-2 pointer-events-auto">
                <input
                  type="text"
                  placeholder="Ask about PMAY scheme..."
                  value={input}
                  onChange={handleInputChange}
                  className="flex-1 bg-transparent border-none outline-none text-gray-700 text-lg placeholder:text-gray-400 px-2"
                  disabled={isLoading}
                  aria-label="Chat input"
                />
                {/* Send or Stop Button (toggle) */}
                {isLoading || isAssistantStreaming ? (
                  <button
                    type="button"
                    onClick={handleStopResponse}
                    aria-label="Stop response"
                    className="flex-shrink-0 w-12 h-12 flex items-center justify-center rounded-full transition disabled:opacity-50 focus:outline-none"
                  >
                    <span className="w-10 h-10 flex items-center justify-center rounded-full bg-blue-100 hover:bg-blue-200 transition">
                      <svg width="20" height="20" fill="none" stroke="#2563eb" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="5" y="5" width="10" height="10" rx="2" /></svg>
                    </span>
                  </button>
                ) : (
                  <button
                    type="submit"
                    className="flex-shrink-0 w-12 h-12 flex items-center justify-center rounded-full transition disabled:opacity-50 focus:outline-none"
                    disabled={!input.trim()}
                    aria-label="Send message"
                  >
                    <span className="w-10 h-10 flex items-center justify-center rounded-full bg-blue-100 hover:bg-blue-200 transition">
                      <svg width="24" height="24" fill="none" stroke="#2563eb" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mx-auto"><line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" /></svg>
                    </span>
                  </button>
                )}
                {/* Regenerate Button */}
                <button
                  type="button"
                  onClick={handleRegenerate}
                  disabled={isLoading || !lastUserMessage}
                  aria-label="Regenerate response"
                  className="flex-shrink-0 w-12 h-12 flex items-center justify-center rounded-full transition disabled:opacity-50 focus:outline-none"
                >
                  <span className="w-10 h-10 flex items-center justify-center rounded-full bg-blue-100 hover:bg-blue-200 transition">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="1 4 1 10 7 10" />
                      <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
                    </svg>
                  </span>
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
