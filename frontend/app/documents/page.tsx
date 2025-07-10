"use client";
import React, { useEffect, useState } from "react";
import DocumentUpload from "@/components/document-upload";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      // Call FastAPI backend directly (adjust URL as needed)
      const response = await fetch("http://localhost:8000/upload", {
        method: "GET",
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.error || "Failed to fetch documents.");
        setDocuments([]);
      } else {
        setDocuments(data.documents || []);
      }
    } catch {
      setError("Network or server error.");
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  return (
    <div className="max-w-2xl mx-auto py-8 space-y-8">
      <Card>
        <CardHeader>
          <CardTitle>Upload New Document</CardTitle>
        </CardHeader>
        <CardContent>
          <DocumentUpload onUpload={fetchDocuments} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Already Uploaded Documents</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div>Loading...</div>
          ) : error ? (
            <div className="text-red-600">{error}</div>
          ) : documents.length === 0 ? (
            <div>No documents uploaded yet.</div>
          ) : (
            <ul className="list-disc pl-5 space-y-1">
              {documents.map((doc) => (
                <li key={doc}>{doc}</li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 