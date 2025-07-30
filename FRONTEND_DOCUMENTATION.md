# PMAY Chatbot Frontend - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [API Integration](#api-integration)
5. [User Interface](#user-interface)
6. [State Management](#state-management)
7. [Internationalization](#internationalization)
8. [Accessibility](#accessibility)
9. [Performance](#performance)
10. [Testing](#testing)
11. [Deployment](#deployment)

## Overview

The PMAY (Pradhan Mantri Awas Yojana) Chatbot Frontend is a modern, responsive web application built with Next.js 15 and React 19. It provides an intuitive interface for users to interact with the AI-powered PMAY chatbot, offering features like real-time chat, document upload, text-to-speech, and multi-language support.

### Key Features
- **Real-time Chat**: Streaming responses with typing indicators
- **Document Upload**: Drag-and-drop PDF upload with processing
- **Text-to-Speech**: Audio output in English and Hindi
- **Multi-language Support**: English and Hindi interface
- **Voice Input**: Speech-to-text functionality
- **Responsive Design**: Mobile-first approach
- **Accessibility**: WCAG compliant interface
- **Theme Support**: Light/dark mode with system preference

## Architecture

```
frontend/
├── app/                    # Next.js 15 App Router
│   ├── page.tsx           # Main chat interface
│   ├── layout.tsx         # Root layout with providers
│   ├── globals.css        # Global styles
│   └── api/               # API route handlers
│       ├── chat/          # Chat endpoint proxy
│       ├── upload/        # Document upload
│       └── feedback/      # User feedback
├── components/            # React components
│   ├── ui/               # Reusable UI components
│   ├── markdown-message.tsx # Markdown rendering
│   ├── text-to-speech.tsx # TTS functionality
│   ├── document-upload.tsx # File upload
│   ├── language-selector.tsx # Language switching
│   ├── model-selector.tsx # AI model selection
│   ├── sidebar-quick-links.tsx # Quick links
│   ├── source-documents.tsx # Source display
│   ├── transliterate-input.tsx # Input transliteration
│   └── theme-provider.tsx # Theme management
├── hooks/                # Custom React hooks
│   ├── use-mobile.tsx    # Mobile detection
│   └── use-translation.ts # Translation hook
├── lib/                  # Utility libraries
│   ├── translations.ts   # Translation data
│   └── utils.ts         # Helper functions
├── public/              # Static assets
└── package.json         # Dependencies and scripts
```

## Core Components

### 1. Main Chat Interface (`app/page.tsx`)

**Purpose**: Central chat interface with all interactive features.

**Key Features**:
- **Real-time Messaging**: Streaming responses with typing indicators
- **Voice Input**: Speech-to-text with browser APIs
- **Message History**: Persistent chat history
- **Response Controls**: Stop, regenerate, and feedback
- **Sample Questions**: Quick access to common queries
- **Mobile Responsive**: Adaptive layout for all devices

**State Management**:
```typescript
interface ChatMessageType {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: SourceDocument[];
}
```

**Key Functions**:
- `handleSubmit()`: Process user messages
- `handleStopResponse()`: Abort streaming responses
- `handleRegenerate()`: Regenerate last response
- `handleStartListening()`: Start speech recognition
- `handleStopListening()`: Stop speech recognition

### 2. Layout System (`app/layout.tsx`)

**Purpose**: Root layout with global providers and metadata.

**Features**:
- **Theme Provider**: System/light/dark theme support
- **Font Loading**: Inter font optimization
- **Metadata**: SEO and social media tags
- **Global Styles**: CSS-in-JS with Tailwind

### 3. API Route Handlers (`app/api/`)

#### Chat Route (`api/chat/route.ts`)
**Purpose**: Proxy to backend chat endpoint with streaming support.

**Features**:
- **Streaming**: Real-time response streaming
- **Error Handling**: Graceful error management
- **CORS**: Cross-origin request handling
- **Headers**: Proper content-type and cache headers

#### Upload Route (`api/upload/route.ts`)
**Purpose**: Handle document uploads to backend.

**Features**:
- **File Validation**: PDF format checking
- **Progress Tracking**: Upload progress indicators
- **Error Handling**: Network and server error management

#### Feedback Route (`api/feedback/route.ts`)
**Purpose**: Collect and forward user feedback.

**Features**:
- **Feedback Types**: Thumbs up/down responses
- **Message Tracking**: Link feedback to specific messages
- **Analytics**: Usage pattern analysis

## User Interface Components

### 1. Markdown Message (`components/markdown-message.tsx`)

**Purpose**: Render markdown responses with syntax highlighting.

**Features**:
- **Code Blocks**: Copy-to-clipboard functionality
- **Links**: External link handling with security
- **Tables**: Responsive table rendering
- **Lists**: Ordered and unordered lists
- **Blockquotes**: Styled quote blocks

**Custom Components**:
```typescript
const CodeBlock: Components["code"] = (props) => {
  // Copy functionality with visual feedback
  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  };
};
```

### 2. Text-to-Speech (`components/text-to-speech.tsx`)

**Purpose**: Convert text responses to audio output.

**Features**:
- **Multi-language**: English and Hindi support
- **Audio Controls**: Play, pause, stop functionality
- **Loading States**: Visual feedback during processing
- **Error Handling**: Graceful failure management
- **Memory Management**: Automatic cleanup of audio objects

**Key Functions**:
- `handleSpeak()`: Generate and play audio
- `stopAudio()`: Cleanup audio resources
- **Abort Controller**: Cancel ongoing requests

### 3. Document Upload (`components/document-upload.tsx`)

**Purpose**: Handle PDF document uploads with drag-and-drop.

**Features**:
- **Drag & Drop**: Visual feedback for file uploads
- **File Validation**: PDF format and size checking
- **Progress Tracking**: Upload status indicators
- **Error Handling**: User-friendly error messages
- **Success Feedback**: Upload confirmation

**Upload Flow**:
```
File Selection → Validation → Upload → Processing → Success
```

### 4. Language Selector (`components/language-selector.tsx`)

**Purpose**: Switch between English and Hindi interfaces.

**Features**:
- **Language Switching**: Instant interface translation
- **Persistence**: Remember user preference
- **Accessibility**: Screen reader support
- **Visual Feedback**: Clear language indicators

### 5. Model Selector (`components/model-selector.tsx`)

**Purpose**: Choose different AI models for responses.

**Features**:
- **Model Options**: Multiple AI model choices
- **Persistence**: Remember selected model
- **Performance**: Model-specific optimizations
- **User Preference**: Customizable model selection

### 6. Sidebar Quick Links (`components/sidebar-quick-links.tsx`)

**Purpose**: Provide quick access to PMAY resources.

**Features**:
- **Official Portals**: Direct links to government sites
- **Application Forms**: Online application access
- **Support Resources**: Helpline and contact information
- **Emergency Contacts**: 24/7 support access

**Link Categories**:
- Official Portals
- Application & Forms
- Support & Help
- Resources

### 7. Source Documents (`components/source-documents.tsx`)

**Purpose**: Display source documents for responses.

**Features**:
- **Document List**: Show referenced sources
- **Relevance Scores**: Display document relevance
- **Expandable View**: Show/hide source details
- **Document Metadata**: File names and relevance

### 8. Transliterate Input (`components/transliterate-input.tsx`)

**Purpose**: Support Hindi input with English keyboard.

**Features**:
- **Transliteration**: English to Hindi conversion
- **Real-time Preview**: Live transliteration display
- **Input Modes**: Toggle between languages
- **Keyboard Support**: Standard keyboard input

## State Management

### Local State
```typescript
// Chat state
const [messages, setMessages] = useState<ChatMessageType[]>([])
const [input, setInput] = useState('')
const [isLoading, setIsLoading] = useState(false)

// UI state
const [selectedLanguage, setSelectedLanguage] = useState("en")
const [selectedModel, setSelectedModel] = useState("llama3.2:1b")
const [isListening, setIsListening] = useState(false)

// Streaming state
const [abortController, setAbortController] = useState<AbortController | null>(null)
const [isAssistantStreaming, setIsAssistantStreaming] = useState(false)
```

### Persistence
- **localStorage**: User preferences and settings
- **Session Storage**: Temporary chat state
- **Cookies**: Language and theme preferences

## Internationalization

### Translation System (`lib/translations.ts`)

**Purpose**: Multi-language support for the entire application.

**Features**:
- **Comprehensive Coverage**: All UI text translated
- **Context-Aware**: Different translations for different contexts
- **Maintainable**: Centralized translation management
- **Type Safety**: TypeScript support for translation keys

**Translation Keys**:
```typescript
export const translations = {
  en: {
    pma_y_chatbot: "PMAY Chatbot",
    home: "Home",
    // ... comprehensive translations
  },
  hi: {
    pma_y_chatbot: "पीएमएवाई चैटबॉट",
    home: "होम",
    // ... Hindi translations
  }
}
```

### Translation Hook (`hooks/use-translation.ts`)

**Purpose**: Provide translation functionality to components.

**Features**:
- **Type Safety**: TypeScript support for translation keys
- **Context Provider**: React context for language state
- **Dynamic Switching**: Real-time language changes
- **Fallback Support**: Default to English if translation missing

## Accessibility

### WCAG Compliance
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: ARIA labels and roles
- **Color Contrast**: High contrast ratios
- **Focus Management**: Clear focus indicators
- **Alternative Text**: Images and icons have alt text

### Voice Input Support
- **Speech Recognition**: Browser-based speech-to-text
- **Language Detection**: Automatic language switching
- **Visual Feedback**: Clear listening indicators
- **Error Handling**: Graceful fallback for unsupported browsers

### Responsive Design
- **Mobile First**: Optimized for mobile devices
- **Touch Targets**: Adequate touch target sizes
- **Viewport Adaptation**: Responsive breakpoints
- **Performance**: Optimized for slower connections

## Performance

### Optimization Strategies

1. **Code Splitting**: Dynamic imports for components
2. **Image Optimization**: Next.js Image component
3. **Font Loading**: Optimized font loading
4. **Caching**: Browser and CDN caching
5. **Bundle Analysis**: Regular bundle size monitoring

### Performance Metrics
- **First Contentful Paint (FCP)**: < 1.5s
- **Largest Contentful Paint (LCP)**: < 2.5s
- **Cumulative Layout Shift (CLS)**: < 0.1
- **First Input Delay (FID)**: < 100ms

### Loading States
- **Skeleton Screens**: Placeholder content
- **Progressive Loading**: Content loads in stages
- **Error Boundaries**: Graceful error handling
- **Retry Mechanisms**: Automatic retry on failure

## API Integration

### Backend Communication

**Chat Endpoint**:
```typescript
const response = await fetch(`${BACKEND_URL}/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: userMessage, model: selectedModel }),
});
```

**Streaming Response**:
```typescript
const reader = response.body?.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  // Process streaming data
}
```

**Error Handling**:
```typescript
try {
  // API call
} catch (error) {
  if (error instanceof Error) {
    setError(error.message);
  }
}
```

### Real-time Features

1. **Streaming Responses**: Real-time text generation
2. **Typing Indicators**: Visual feedback during processing
3. **Abort Controllers**: Cancel ongoing requests
4. **Retry Logic**: Automatic retry on network issues

## Testing

### Test Strategy

1. **Unit Tests**: Component-level testing
2. **Integration Tests**: API integration testing
3. **E2E Tests**: Full user journey testing
4. **Accessibility Tests**: WCAG compliance testing

### Test Coverage Areas

- **Component Rendering**: All UI components
- **User Interactions**: Click, type, drag events
- **API Integration**: Backend communication
- **Error Handling**: Network and server errors
- **Accessibility**: Screen reader and keyboard navigation

### Testing Tools

- **Jest**: Unit and integration testing
- **React Testing Library**: Component testing
- **Cypress**: End-to-end testing
- **axe-core**: Accessibility testing

## Deployment

### Build Process

```bash
# Development
npm run dev

# Production build
npm run build

# Start production server
npm start

# Linting
npm run lint
```

### Environment Configuration

**Environment Variables**:
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=PMAY Chatbot
NEXT_PUBLIC_VERSION=1.0.0
```

### Deployment Platforms

1. **Vercel**: Recommended for Next.js
2. **Netlify**: Alternative deployment option
3. **AWS Amplify**: Enterprise deployment
4. **Docker**: Containerized deployment

### Performance Monitoring

- **Web Vitals**: Core Web Vitals tracking
- **Error Tracking**: Sentry integration
- **Analytics**: User behavior tracking
- **Uptime Monitoring**: Service availability

## Security

### Security Measures

1. **Input Validation**: Sanitize all user inputs
2. **CORS Configuration**: Proper cross-origin handling
3. **Content Security Policy**: XSS protection
4. **HTTPS Enforcement**: Secure communication
5. **Rate Limiting**: API abuse prevention

### Data Protection

- **No Sensitive Data**: No PII stored in frontend
- **Secure Communication**: HTTPS for all API calls
- **Session Management**: Secure session handling
- **File Upload Security**: Validate file types and sizes

## Maintenance

### Regular Tasks

1. **Dependency Updates**: Security and feature updates
2. **Performance Monitoring**: Regular performance audits
3. **Accessibility Audits**: WCAG compliance checks
4. **User Feedback**: Collect and analyze user feedback
5. **Error Monitoring**: Track and fix errors

### Monitoring Tools

- **Google Analytics**: User behavior tracking
- **Sentry**: Error monitoring and reporting
- **Lighthouse**: Performance and accessibility audits
- **WebPageTest**: Performance testing

## Conclusion

The PMAY Chatbot Frontend is a modern, accessible, and performant web application that provides an excellent user experience for interacting with the AI-powered PMAY chatbot. Its modular architecture, comprehensive internationalization, and robust error handling make it suitable for government services where reliability and accessibility are paramount.

The frontend's ability to handle various user interactions, provide real-time feedback, and maintain high performance across different devices and network conditions ensures a smooth user experience for citizens seeking information about the PMAY scheme. 