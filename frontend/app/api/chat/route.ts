import { NextResponse } from 'next/server';
import { type CoreMessage } from 'ai';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();

    const lastUserMessage = messages.findLast((message: CoreMessage) => message.role === 'user');

    if (!lastUserMessage) {
      return NextResponse.json({
        error: "No user message found in the request."
      }, { status: 400 });
    }

    // Make request to backend chat endpoint
    const backendResponse = await fetch(`${BACKEND_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: lastUserMessage.content }),
    });

    if (!backendResponse.ok) {
      const errorText = await backendResponse.text().catch(() => null);
      console.error('Backend error:', backendResponse.status, errorText);
      throw new Error(`Backend request failed with status ${backendResponse.status}: ${errorText}`);
    }

    // Directly return the backend response body as a stream
    return new Response(backendResponse.body, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache, no-transform',
        'Connection': 'keep-alive',
        'X-Vercel-AI-Data-Stream': backendResponse.headers.get('X-Vercel-AI-Data-Stream') || 'v1', // Pass through X-Vercel-AI-Data-Stream header
      },
    });

  } catch (error) {
    console.error('Error in chat endpoint:', error);
    if (error instanceof Error && error.message.includes("Backend request failed with status")) {
        return NextResponse.json(
            { error: error.message },
            { status: 500 }
        );
    }
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
