import { NextResponse } from 'next/server';
import { process_document } from '../../../backend/core/document_processor';
import { add_to_vector_collection } from '../../../backend/core/vector_store';
// import { list_uploaded_documents } from '../../../backend/core/vector_store';

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

// TODO: Implement GET by calling backend Python API for document listing
export async function GET() {
  try {
    // const docs = list_uploaded_documents();
    return NextResponse.json({ documents: [] }); // Placeholder for now
  } catch (error) {
    console.error('Error in GET upload endpoint:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 