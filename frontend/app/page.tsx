"use client"

import { useRef, useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Input } from "@/components/ui/input"
import { Loader2, Send, Info, Home, FileText, Settings, Menu, ArrowLeft } from "lucide-react"
import Image from "next/image"
import { SourceDocument, SourceDocuments } from "@/components/source-documents"
import { useMobile } from "@/hooks/use-mobile"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

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

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessageType[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  const [isAssistantStreaming, setIsAssistantStreaming] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const isMobile = useMobile()
  const [showSidebar, setShowSidebar] = useState(!isMobile)
  const [activeSection, setActiveSection] = useState("home")
  const [userMessageCount, setUserMessageCount] = useState(0); // New state to trigger scroll

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

  const showWelcomeMessage = messages.length === 0 && !isLoading && !error

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: ChatMessageType = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
    }

    setMessages((prevMessages) => [...prevMessages, userMessage])
    setInput('')
    setIsLoading(true)
    setError(null)
    setUserMessageCount(prevCount => prevCount + 1); // Increment to trigger scroll

    const newAssistantMessageId = `ai-response-${Date.now()}`

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ messages: [userMessage] }),
      })

      if (!response.ok || !response.body) {
        const errorText = await response.text()
        throw new Error(`API request failed with status ${response.status}: ${errorText}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let assistantResponseContent = ''
      let assistantSources: SourceDocument[] = [];

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        // console.log('Frontend: Raw chunk received:', chunk.length, 'bytes')
        const sseMessages = chunk.split('\n\n').filter(msg => msg.startsWith('data: ')).map(msg => msg.substring(6))

        for (const sseMessage of sseMessages) {
          // console.log('Frontend: Processing SSE message:', sseMessage)
          try {
            const parsedData = JSON.parse(sseMessage)
            // console.log('Frontend: Parsed SSE data:', parsedData)
            
            if (parsedData.type === 'text') {
              const content = parsedData.content;
              if (content) {
                assistantResponseContent += content;
                if (!isAssistantStreaming) {
                  setIsAssistantStreaming(true);
                }
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
            console.error('Failed to parse SSE message:', sseMessage, jsonError)
          }
        }
      }
    } catch (err) {
      console.error('Error during streaming:', err)
      setError(err instanceof Error ? err : new Error('An unknown error occurred.'))
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          id: Date.now().toString(),
          role: 'assistant',
          content: 'I apologize, but I encountered an error while processing your request. Please try again.',
        },
      ])
    } finally {
      setIsLoading(false)
      setIsAssistantStreaming(false);
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Sidebar */}
      <div
        className={`fixed top-0 left-0 h-screen z-50 ${
          showSidebar ? "w-64" : "w-0 -ml-64"
        } bg-blue-800 text-white transition-all duration-300 ease-in-out overflow-hidden
        ${isMobile ? "shadow-xl" : ""}`}
      >
        <div className="p-4 h-full flex flex-col">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-lg font-bold">PMAY Chatbot</h1>
            {isMobile && (
              <Button
                variant="ghost"
                size="icon"
                className="text-white hover:bg-blue-700"
                onClick={() => setShowSidebar(false)}
              >
                <ArrowLeft className="h-6 w-6" />
              </Button>
            )}
          </div>

          <nav className="space-y-1 mb-6">
            <Button
              variant="ghost"
              className={`w-full justify-start text-white hover:bg-blue-700 ${
                activeSection === "home" ? "bg-blue-700" : ""
              }`}
              onClick={() => setActiveSection("home")}
            >
              <Home className="mr-2 h-5 w-5" />
              Home
            </Button>
            <Button
              variant="ghost"
              className={`w-full justify-start text-white hover:bg-blue-700 ${
                activeSection === "documents" ? "bg-blue-700" : ""
              }`}
              onClick={() => setActiveSection("documents")}
            >
              <FileText className="mr-2 h-5 w-5" />
              Documents
            </Button>
            <Button
              variant="ghost"
              className={`w-full justify-start text-white hover:bg-blue-700 ${
                activeSection === "settings" ? "bg-blue-700" : ""
              }`}
              onClick={() => setActiveSection("settings")}
            >
              <Settings className="mr-2 h-5 w-5" />
              Settings
            </Button>
          </nav>

          {/* Dynamic Content Based on Active Section */}
          <div className="flex-1 overflow-y-auto">
            {activeSection === "home" && (
              <div className="space-y-4">
                <div className="text-sm text-blue-200">
                  <h3 className="font-semibold mb-2">Quick Actions</h3>
                  <ul className="space-y-1 text-xs">
                    <li>• Ask about PMAY eligibility</li>
                    <li>• Check application status</li>
                    <li>• Learn about benefits</li>
                    <li>• Find nearest office</li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className={`flex-1 flex flex-col h-full ${!isMobile && showSidebar ? "ml-64" : "ml-0"}`}>
        {/* Header */}
        <header className="bg-white border-b border-gray-200 p-4 flex items-center justify-between shadow-sm shrink-0 relative h-20">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setShowSidebar(!showSidebar)}
          >
            <Menu className="h-6 w-6" />
          </Button>

          <div className={`absolute left-1/2 -translate-x-1/2 flex items-center space-x-4 transition-opacity duration-500 ${messages.length > 0 ? 'opacity-100' : 'opacity-0'}`}>
            <Image
              src="/mohua-logo-removebgpng.png"
              alt="MoHUA Logo"
              width={64}
              height={64}
              className="h-16 w-auto"
              priority
            />
            <Image
              src="/pmay-logo.svg"
              alt="PMAY Logo"
              width={64}
              height={64}
              className="h-16 w-auto"
              priority
            />
            {/* <span className="font-bold text-lg text-blue-800 dark:text-blue-200">PMAY Chatbot</span> */}
          </div>

          {/* Spacer div to push the button to the right on larger screens */}
          <div className="flex-1 hidden lg:block"></div>

          {/* Right-aligned content (e.g., existing user avatar or settings) */}
          <div className="flex items-center space-x-4">
            {/* Add any other right-aligned header content here if it exists in the original header */}
          </div>
        </header>

        {/* Scrollable Chat Messages Area */}
        <div className="flex-1 overflow-y-auto">
          <div
            className={`flex flex-col px-4 md:px-6 bg-white pt-6 pb-8
            ${showWelcomeMessage ? "items-center justify-center" : "items-stretch justify-start"}`}
          >
            {/* Welcome Message Section */}
            {showWelcomeMessage && (
              <div className="text-center p-8">
                <div className="space-y-4 mt-4">
                  <div className="mx-auto p-2 bg-gradient-to-br from-orange-100 to-green-100 rounded-full border-2 border-orange-200 shadow-lg w-40 h-40 flex items-center justify-center">
                    <div className="flex items-center space-x-4">
                      <Image
                        src="/mohua-logo-removebgpng.png"
                        alt="MoHUA Logo"
                        width={65}
                        height={65}
                        className="object-contain"
                      />
                      <Image
                        src="/pmay-logo.svg"
                        alt="PMAY Logo"
                        width={65}
                        height={65}
                        className="object-contain"
                      />
                    </div>
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
                    className={`flex items-start gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    {message.role === "assistant" && (
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
                    )}
                    <div
                      className={`relative w-fit overflow-hidden max-w-[80%] rounded-lg px-4 pb-2 pt-3 ${message.role === "user" ? "bg-blue-500 text-white" : "bg-gray-100 text-gray-800"}`}
                    >
                      <div className="prose prose-sm leading-normal text-gray-900 break-words">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
                      </div>
                      {message.sources && message.sources.length > 0 && message.role !== "user" && (
                        <SourceDocuments documents={message.sources} />
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

        {/* Input Area (fixed at bottom) */}
        <div className="border-t border-gray-200 p-4 bg-gray-50 shrink-0">
          <form onSubmit={handleSubmit} className="flex w-full items-center gap-3">
            <Input
              placeholder="Ask about PMAY scheme..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-1 bg-white border-gray-300 focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 text-gray-900 placeholder:text-gray-500 rounded-lg py-3 px-4"
              disabled={isLoading}
              aria-label="Chat input"
            />
            <Button
              type="submit"
              size="lg"
              className="bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-5 py-3 shadow-md hover:shadow-lg transition-all duration-200 transform hover:-translate-y-0.5 disabled:bg-blue-400 disabled:transform-none disabled:shadow-none"
              disabled={isLoading || !input.trim()}
              aria-label="Send message"
            >
              {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
            </Button>
          </form>
        </div>
      </div>
    </div>
  )
}
