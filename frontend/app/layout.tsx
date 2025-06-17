import type React from "react"
import "./globals.css"
import type { Metadata } from "next"
import { Inter } from 'next/font/google'
import { ThemeProvider } from "@/components/theme-provider"

const inter = Inter({ subsets: ["latin"] })

// Update the metadata
export const metadata: Metadata = {
  title: "PMAY Chatbot - MoHUA RAG-based Assistant",
  description: "AI chatbot for the Ministry of Housing and Urban Affairs to assist with PMAY scheme queries",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ThemeProvider defaultTheme="system" enableSystem>
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
