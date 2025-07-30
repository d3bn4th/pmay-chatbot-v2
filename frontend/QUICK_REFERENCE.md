# PMAY Chatbot Frontend - Quick Reference

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## 📁 Key Files & Their Purpose

| File | Purpose | Key Features |
|------|---------|--------------|
| `app/page.tsx` | Main chat interface | Real-time chat, voice input, streaming |
| `app/layout.tsx` | Root layout | Theme provider, metadata, global styles |
| `app/api/chat/route.ts` | Chat API proxy | Backend communication, streaming |
| `app/api/upload/route.ts` | Upload handler | File validation, progress tracking |
| `components/markdown-message.tsx` | Markdown renderer | Code blocks, links, tables |
| `components/text-to-speech.tsx` | TTS functionality | Audio generation, controls |
| `components/document-upload.tsx` | File upload | Drag & drop, validation |
| `components/language-selector.tsx` | Language switching | EN/HI support, persistence |
| `components/model-selector.tsx` | AI model selection | Model options, persistence |
| `components/sidebar-quick-links.tsx` | Quick links | PMAY resources, contacts |
| `components/source-documents.tsx` | Source display | Document references, relevance |
| `components/transliterate-input.tsx` | Hindi input | Transliteration, preview |
| `lib/translations.ts` | Translation data | EN/HI translations, type safety |
| `hooks/use-translation.ts` | Translation hook | Language switching, context |

## 🔄 Data Flow

### Chat Request
```
User Input → API Route → Backend → Streaming Response → UI Update
     ↓
1. Validate input
2. Send to backend
3. Stream response
4. Update UI
```

### Document Upload
```
File Selection → Validation → Upload → Processing → Success
     ↓
1. Check file type
2. Upload to backend
3. Process PDF
4. Add to knowledge base
```

## 🎨 UI Components

### Core Components
1. **Chat Interface**: Real-time messaging with streaming
2. **Voice Input**: Speech-to-text with browser APIs
3. **Document Upload**: Drag-and-drop PDF upload
4. **Text-to-Speech**: Audio output in EN/HI
5. **Language Selector**: EN/HI interface switching
6. **Model Selector**: AI model selection
7. **Quick Links**: PMAY resources and contacts
8. **Source Documents**: Reference display

### UI Library (`components/ui/`)
- **Button**: Variants, sizes, states
- **Input**: Text input with validation
- **Card**: Content containers
- **Avatar**: User avatars
- **Progress**: Loading indicators
- **Scroll Area**: Custom scrollbars
- **Select**: Dropdown selections

## 🌐 Internationalization

### Translation System
```typescript
// Translation keys
export const translations = {
  en: { pma_y_chatbot: "PMAY Chatbot", ... },
  hi: { pma_y_chatbot: "पीएमएवाई चैटबॉट", ... }
}

// Usage in components
const { t } = useTranslation();
const text = t('pma_y_chatbot');
```

### Language Support
- **English**: Primary interface language
- **Hindi**: Full translation support
- **Persistence**: Remember user preference
- **Dynamic Switching**: Real-time language changes

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Mobile Features
- **Touch Targets**: 44px minimum
- **Swipe Gestures**: Touch-friendly interactions
- **Voice Input**: Mobile-optimized speech recognition
- **Responsive Layout**: Adaptive UI components

## 🔌 API Integration

### Backend Communication
```typescript
// Chat endpoint
const response = await fetch(`${BACKEND_URL}/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message, model }),
});

// Streaming response
const reader = response.body?.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  // Process streaming data
}
```

### Error Handling
```typescript
try {
  // API call
} catch (error) {
  if (error instanceof Error) {
    setError(error.message);
  }
}
```

## 🎯 State Management

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
- **localStorage**: User preferences, selected model
- **Session Storage**: Temporary chat state
- **Cookies**: Language and theme preferences

## ♿ Accessibility

### WCAG Compliance
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader**: ARIA labels and roles
- **Color Contrast**: High contrast ratios
- **Focus Management**: Clear focus indicators
- **Alternative Text**: Images and icons

### Voice Input
- **Speech Recognition**: Browser-based STT
- **Language Detection**: Automatic switching
- **Visual Feedback**: Clear listening indicators
- **Error Handling**: Graceful fallbacks

## ⚡ Performance

### Optimization
1. **Code Splitting**: Dynamic imports
2. **Image Optimization**: Next.js Image component
3. **Font Loading**: Optimized font loading
4. **Caching**: Browser and CDN caching
5. **Bundle Analysis**: Regular monitoring

### Metrics
- **FCP**: < 1.5s
- **LCP**: < 2.5s
- **CLS**: < 0.1
- **FID**: < 100ms

## 🧪 Testing

### Test Strategy
```bash
# Unit tests
npm test

# E2E tests
npm run test:e2e

# Accessibility tests
npm run test:a11y
```

### Coverage Areas
- **Component Rendering**: All UI components
- **User Interactions**: Click, type, drag events
- **API Integration**: Backend communication
- **Error Handling**: Network and server errors
- **Accessibility**: Screen reader and keyboard

## 🚀 Deployment

### Environment Setup
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=PMAY Chatbot
NEXT_PUBLIC_VERSION=1.0.0
```

### Build Commands
```bash
# Development
npm run dev

# Production build
npm run build

# Start production
npm start

# Linting
npm run lint
```

### Deployment Platforms
1. **Vercel**: Recommended for Next.js
2. **Netlify**: Alternative option
3. **AWS Amplify**: Enterprise
4. **Docker**: Containerized

## 🔒 Security

### Measures
1. **Input Validation**: Sanitize all inputs
2. **CORS Configuration**: Proper cross-origin handling
3. **Content Security Policy**: XSS protection
4. **HTTPS Enforcement**: Secure communication
5. **Rate Limiting**: API abuse prevention

### Data Protection
- **No Sensitive Data**: No PII in frontend
- **Secure Communication**: HTTPS for all API calls
- **Session Management**: Secure session handling
- **File Upload Security**: Validate file types and sizes

## 📊 Monitoring

### Tools
- **Google Analytics**: User behavior tracking
- **Sentry**: Error monitoring and reporting
- **Lighthouse**: Performance and accessibility audits
- **WebPageTest**: Performance testing

### Metrics
- **Web Vitals**: Core Web Vitals tracking
- **Error Tracking**: Sentry integration
- **Analytics**: User behavior tracking
- **Uptime Monitoring**: Service availability

## 🛠️ Development

### Adding Features
1. **Components**: Add to `components/` directory
2. **API Routes**: Add to `app/api/` directory
3. **Translations**: Update `lib/translations.ts`
4. **Styling**: Use Tailwind CSS classes
5. **Testing**: Add corresponding tests

### Common Patterns
```typescript
// Translation usage
const { t } = useTranslation();
const text = t('key_name');

// API call with error handling
try {
  const response = await fetch('/api/endpoint', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Request failed');
  const result = await response.json();
} catch (error) {
  console.error('Error:', error);
}

// State management
const [state, setState] = useState(initialValue);
const updateState = (newValue) => setState(newValue);
```

## 📚 Dependencies

### Core Dependencies
| Package | Purpose |
|---------|---------|
| `next` | React framework |
| `react` | UI library |
| `typescript` | Type safety |
| `tailwindcss` | Styling |
| `lucide-react` | Icons |
| `react-markdown` | Markdown rendering |
| `ai` | AI SDK |
| `zod` | Validation |

### Development Dependencies
| Package | Purpose |
|---------|---------|
| `eslint` | Code linting |
| `@types/react` | TypeScript types |
| `postcss` | CSS processing |
| `tailwindcss-animate` | Animations |

## 🎯 Best Practices

1. **Component Structure**: Keep components small and focused
2. **State Management**: Use local state for UI, context for global
3. **Error Handling**: Always handle errors gracefully
4. **Performance**: Optimize for Core Web Vitals
5. **Accessibility**: Follow WCAG guidelines
6. **Testing**: Write tests for critical functionality
7. **Documentation**: Keep docs updated
8. **Security**: Validate all inputs and outputs 