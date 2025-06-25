import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { message_id, feedback, content } = body;
    if (!message_id || !feedback || !content) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }
    const backendRes = await fetch(`${BACKEND_URL}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message_id, feedback, content }),
    });
    const data = await backendRes.json();
    return NextResponse.json(data, { status: backendRes.ok ? 200 : 500 });
  } catch {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
} 