# 🤖 PMAY Chatbot - MoHUA RAG-based Assistant

A sophisticated chatbot built for the Ministry of Housing and Urban Affairs (MoHUA) to assist users with queries related to the Pradhan Mantri Awas Yojana (PMAY) scheme. This application uses advanced RAG (Retrieval Augmented Generation) with cross-encoder re-ranking to provide accurate and context-aware responses.

## 🌟 Features

- **Intelligent Document Processing**: Upload and process PDF documents containing PMAY-related information
- **Advanced RAG Implementation**: Uses ChromaDB for vector storage and retrieval
- **Cross-Encoder Re-ranking**: Improves response relevance using semantic re-ranking
- **Next.js Interface**: User-friendly chat interface with real-time responses
- **Amazon Bedrock Integration**: Powered by Amazon's Nova Pro model for high-quality responses
- **Context-Aware Responses**: Provides accurate information based on official documents

## 🚨 Prerequisites

- Node.js 18+
- AWS account with access to Amazon Bedrock
- Configured AWS credentials with permissions to access the Nova Pro model

## 🔧 Setup Instructions

1. **Clone the repository**
   \`\`\`sh
   git clone <repository-url>
   cd pmay-chatbot
   \`\`\`

2. **Install dependencies**
   \`\`\`sh
   npm install
   \`\`\`

3. **Set up environment variables**
   Create a `.env.local` file with the following variables:
   \`\`\`
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   \`\`\`

4. **Run the development server**
   \`\`\`sh
   npm run dev
   \`\`\`

5. **Open [http://localhost:3000](http://localhost:3000)** in your browser to see the application.

## 📚 Usage

1. **Upload Documents**
   - Upload PDF documents containing PMAY-related information
   - The system will automatically process and index the content

2. **Ask Questions**
   - Use the chat interface to ask questions about PMAY
   - The chatbot will provide responses based on the uploaded documents
   - View source documents for each response using the expandable section

## 🛠️ Development

### Project Structure

- `app/`: Next.js application files
  - `api/chat/route.ts`: API route for chat functionality with RAG implementation
  - `page.tsx`: Main chat interface
- `components/`: React components
  - `document-upload.tsx`: Component for uploading and processing documents
  - `source-documents.tsx`: Component for displaying source documents
- `hooks/`: Custom React hooks
- `public/`: Static assets

## 🔍 Technical Details

- **Vector Database**: ChromaDB with embeddings
- **Text Splitting**: RecursiveCharacterTextSplitter with 750 token chunks
- **Re-ranking**: Cross-encoder model (ms-marco-MiniLM-L-6-v2)
- **LLM**: Amazon Bedrock Nova Pro model
- **UI Framework**: Next.js with Tailwind CSS styling

## ⚠️ Common Issues and Solutions

1. **ChromaDB/SQLite Compatibility**
   - If you encounter SQLite-related errors, refer to [ChromaDB troubleshooting](https://docs.trychroma.com/troubleshooting#sqlite)

2. **AWS Credentials**
   - Ensure your AWS credentials have the necessary permissions to access Amazon Bedrock
   - Verify the AWS region is correct and supports the Nova Pro model

3. **Document Processing Issues**
   - Check that uploaded PDFs are not password-protected
   - Ensure PDFs are text-based and not scanned images without OCR

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

[Add appropriate license information]

## 🔗 Useful Links

- [PMAY Official Website](https://pmay-urban.gov.in/)
- [MoHUA Official Website](https://mohua.gov.in/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
\`\`\`

Let's update the layout.tsx file to include the proper metadata:

```typescriptreact file="app/layout.tsx"
[v0-no-op-code-block-prefix]import type React from "react"
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
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
