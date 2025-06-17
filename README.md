# 🤖 PMAY Chatbot - MoHUA RAG-based Assistant

A sophisticated chatbot built for the Ministry of Housing and Urban Affairs (MoHUA) to assist users with queries related to the Pradhan Mantri Awas Yojana (PMAY) scheme. This application uses advanced RAG (Retrieval Augmented Generation) with cross-encoder re-ranking to provide accurate and context-aware responses.

## 🌟 Features

- **Intelligent Document Processing**: Upload and process PDF documents containing PMAY-related information
- **Advanced RAG Implementation**: Uses ChromaDB for vector storage and retrieval
- **Cross-Encoder Re-ranking**: Improves response relevance using semantic re-ranking
- **Modern Interface**: User-friendly chat interface with real-time responses
- **Context-Aware Responses**: Provides accurate information based on official documents
- **Document Management**: Upload, process, and manage PMAY-related documents
- **Source Attribution**: View source documents for each response

## 🚨 Prerequisites

- Node.js 18+
- Python 3.8+
- AWS account with access to Amazon Bedrock
- Configured AWS credentials with permissions to access the Nova Pro model

## 🔧 Setup Instructions

### Backend Setup

1. **Set up Python virtual environment**
   ```sh
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install Python dependencies**
   ```sh
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Set up environment variables**
   Create a `.env` file in the backend directory:
   ```
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   ```

### Frontend Setup

1. **Install Node.js dependencies**
   ```sh
   cd frontend
   npm install
   ```

2. **Set up environment variables**
   Create a `.env.local` file in the frontend directory:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Run the development servers**

   In one terminal (backend):
   ```sh
   cd backend
   uvicorn api.main:app --reload
   ```

   In another terminal (frontend):
   ```sh
   cd frontend
   npm run dev
   ```

4. **Open [http://localhost:3000](http://localhost:3000)** in your browser to see the application.

## 📚 Project Structure

```
pmay-chatbot/
├── backend/
│   ├── api/            # FastAPI application
│   ├── core/           # Core business logic
│   ├── models/         # Data models
│   ├── utils/          # Utility functions
│   ├── docs/           # Documentation files
│   └── requirements.txt
├── frontend/
│   ├── app/           # Next.js pages and API routes
│   ├── components/    # React components
│   ├── hooks/         # Custom React hooks
│   ├── lib/           # Utility functions
│   └── public/        # Static assets
└── models/            # Shared model definitions
```

## 🛠️ Technical Stack

### Backend
- **Framework**: FastAPI
- **Vector Database**: ChromaDB
- **Text Processing**: LangChain
- **LLM Integration**: Amazon Bedrock
- **Document Processing**: PyPDF2, Unstructured

### Frontend
- **Framework**: Next.js 14
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **State Management**: React Hooks
- **API Client**: Axios

## 🔍 Technical Details

- **Vector Database**: ChromaDB with embeddings
- **Text Splitting**: RecursiveCharacterTextSplitter with 750 token chunks
- **Re-ranking**: Cross-encoder model (ms-marco-MiniLM-L-6-v2)
- **LLM**: Amazon Bedrock Nova Pro model
- **Document Processing**: PDF parsing with metadata extraction
- **API**: RESTful endpoints with FastAPI
- **Authentication**: JWT-based authentication (optional)

## ⚠️ Common Issues and Solutions

1. **ChromaDB/SQLite Compatibility**
   - If you encounter SQLite-related errors, refer to [ChromaDB troubleshooting](https://docs.trychroma.com/troubleshooting#sqlite)

2. **AWS Credentials**
   - Ensure your AWS credentials have the necessary permissions to access Amazon Bedrock
   - Verify the AWS region is correct and supports the Nova Pro model

3. **Document Processing Issues**
   - Check that uploaded PDFs are not password-protected
   - Ensure PDFs are text-based and not scanned images without OCR

4. **Development Environment**
   - Make sure both backend and frontend servers are running
   - Check that environment variables are properly set
   - Verify network connectivity between frontend and backend

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Useful Links

- [PMAY Official Website](https://pmay-urban.gov.in/)
- [MoHUA Official Website](https://mohua.gov.in/)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
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
