"use client"

import { useRef, useEffect, useState } from "react"
import { useChat } from "ai/react"
import MarkdownIt from "markdown-it"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Loader2, Send, Info, Home, FileText, Settings, UserCircle2, Menu } from "lucide-react"
import Image from "next/image"
import { SourceDocuments } from "@/components/source-documents"
import { useMobile } from "@/hooks/use-mobile"

const md = new MarkdownIt()

// Sample source documents for demonstration
const sampleSourceDocs = [
  {
    content:
      "PMAY (Pradhan Mantri Awas Yojana) is a flagship scheme of the Government of India aimed at providing housing for all by 2022.",
    source: "PMAY_Guidelines_2021.pdf",
    relevance: 0.92,
  },
  {
    content:
      "Beneficiaries of PMAY include Economically Weaker Section (EWS), Low Income Group (LIG), and Middle Income Group (MIG).",
    source: "PMAY_Eligibility_Criteria.pdf",
    relevance: 0.85,
  },
]

export default function ChatPage() {
  const { messages, input, handleInputChange, handleSubmit, isLoading, error } = useChat({
    streamProtocol: 'text',
  })
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const isMobile = useMobile()
  const [showSidebar, setShowSidebar] = useState(!isMobile)
  const [activeSection, setActiveSection] = useState("home")

  useEffect(() => {
    setShowSidebar(!isMobile)
  }, [isMobile])

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages])

  useEffect(() => {
    if (error) {
      console.error("useChat error object:", error)
    }
  }, [error])

  const showWelcomeMessage = messages.length === 0 && !isLoading && !error

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div
        className={`${
          showSidebar ? "w-64" : "w-0 -ml-64"
        } bg-blue-800 text-white transition-all duration-300 ease-in-out flex-shrink-0 overflow-hidden`}
      >
        <div className="p-4 h-full flex flex-col">
          <div className="flex flex-col items-center justify-center mb-8">
            <div className="flex items-center mb-2">
              <div className="bg-white p-2 rounded-xl mr-2">
                <Image
                  src="/mohua-logo-removebgpng.png"
                  alt="Government of India Emblem"
                  width={60}
                  height={60}
                  className="object-contain"
                />
              </div>
              <div className="bg-white p-2 rounded-xl">
                <Image
                  src="/pmay-logo-removebg-preview.png"
                  alt="PMAY Logo"
                  width={80}
                  height={80}
                  className="object-contain"
                />
              </div>
            </div>
            <h1 className="text-lg font-bold">PMAY Chatbot</h1>
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
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 p-4 flex items-center justify-between shadow-sm">
          <Button variant="ghost" size="sm" onClick={() => setShowSidebar(!showSidebar)} className="md:hidden">
            <Menu className="h-5 w-5" />
          </Button>
          
          <div className="w-8"></div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 p-4 overflow-hidden">
          <Card className="h-full flex flex-col shadow-lg bg-white">
            <CardContent className="flex-1 p-0 overflow-hidden bg-white">
              <ScrollArea ref={scrollAreaRef} className="h-full overflow-y-auto">
                <div
                  className={`min-h-full flex flex-col transition-all duration-500 ease-in-out bg-white
                  ${showWelcomeMessage ? "items-center justify-center" : "items-stretch justify-start pt-6"}`}
                >
                  {/* Welcome Message Section */}
                  {showWelcomeMessage && (
                    <div className="text-center p-8">
                      <div className="space-y-4 mt-4">
                        <div className="mx-auto p-2 bg-gradient-to-br from-orange-100 to-green-100 rounded-full border-2 border-orange-200 shadow-lg w-28 h-28 flex items-center justify-center">
                          <Image
                            src="/pmay-logo-removebg-preview.png"
                            alt="Government of India Emblem"
                            width={95}
                            height={95}
                            className="object-contain"
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
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
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
                    <div className="space-y-6 w-full px-4 md:px-6 pb-8">
                      {messages.map((message) => (
                        <div
                          key={message.id}
                          className={`flex items-start gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}
                        >
                          {message.role !== "user" && (
                            <Avatar
                              className={`h-10 w-10 border border-gray-200 shadow-md bg-gradient-to-br from-orange-100 to-green-100 ${isLoading && message.id === messages[messages.length - 1]?.id && messages[messages.length - 1].role !== "user" ? "animate-pulse" : ""}`}
                            >
                              <AvatarImage src="/indian-govt-emblem.png" alt="AI Avatar" className="object-contain" />
                              <AvatarFallback className="bg-blue-100 text-blue-800 text-xs">AI</AvatarFallback>
                            </Avatar>
                          )}
                          <div className="flex flex-col max-w-[75%]">
                            <div
                              className={`rounded-xl px-4 py-3 shadow-md 
                              ${
                                message.role === "user"
                                  ? "bg-blue-600 text-white rounded-br-none"
                                  : "bg-gray-200 text-gray-800 rounded-bl-none"
                              }`}
                              dangerouslySetInnerHTML={{ __html: md.render(message.content) }}
                            />
                            {message.role !== "user" && message.id === messages[messages.length - 1]?.id && isLoading && (
                                <div className="ml-auto mt-2 flex items-center">
                                    <Loader2 className="h-4 w-4 text-gray-500 animate-spin mr-1" />
                                    <span className="text-xs text-gray-500">Generating...</span>
                                </div>
                            )}
                            {message.role === "assistant" && <SourceDocuments documents={sampleSourceDocs} />}
                          </div>
                          {message.role === "user" && (
                            <Avatar className="h-10 w-10 border-2 border-blue-200 shadow-md">
                              <AvatarFallback className="bg-blue-600 text-white">
                                <UserCircle2 className="h-5 w-5" />
                              </AvatarFallback>
                            </Avatar>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </ScrollArea>
            </CardContent>

            <CardFooter className="border-t border-gray-200 p-4 bg-gray-50">
              <form onSubmit={handleSubmit} className="flex w-full items-center gap-3">
                <Input
                  placeholder="Ask about PMAY scheme..."
                  value={input}
                  onChange={handleInputChange}
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
            </CardFooter>
          </Card>
        </div>
      </div>
    </div>
  )
}
