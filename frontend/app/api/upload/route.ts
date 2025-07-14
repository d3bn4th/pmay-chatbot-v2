import { NextResponse } from 'next/server';
// import { list_uploaded_documents } from '../../../backend/core/vector_store';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(req: Request) {
  try {
    const formData = await req.formData();
    const file = formData.get('file') as File;
    
    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      );
    }

    // Proxy the file upload to the FastAPI backend
    const backendFormData = new FormData();
    backendFormData.append('file', file);
    const backendResponse = await fetch(`${BACKEND_URL}/upload`, {
      method: 'POST',
      body: backendFormData,
    });
    const data = await backendResponse.json();
    if (!backendResponse.ok) {
      return NextResponse.json(
        { error: data.error || 'Upload failed.' },
        { status: backendResponse.status }
      );
    }
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in upload endpoint:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 

export async function GET() {
  try {
    // Proxy the GET request to the FastAPI backend
    const backendResponse = await fetch(`${BACKEND_URL}/upload`, {
      method: 'GET',
    });
    const data = await backendResponse.json();
    if (!backendResponse.ok) {
      return NextResponse.json(
        { error: data.error || 'Failed to fetch documents.' },
        { status: backendResponse.status }
      );
    }
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in GET upload endpoint:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 