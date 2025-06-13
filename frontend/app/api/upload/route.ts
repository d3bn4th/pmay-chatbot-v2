import { NextResponse } from 'next/server';
import { process_document } from '../../../backend/core/document_processor';
import { add_to_vector_collection } from '../../../backend/core/vector_store';

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

    const content = await file.arrayBuffer();
    const splits = process_document(Buffer.from(content), file.name);
    
    if (!splits || splits.length === 0) {
      return NextResponse.json(
        { error: 'Invalid or empty document' },
        { status: 400 }
      );
    }

    const chunks_added = add_to_vector_collection(splits, file.name);
    
    return NextResponse.json({
      message: `Successfully processed ${file.name}`,
      chunks_added
    });
  } catch (error) {
    console.error('Error in upload endpoint:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 