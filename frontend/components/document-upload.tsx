import React, { useRef, useState } from "react";
import { Button } from "@/components/ui/button";

export function DocumentUpload({ onUpload }: { onUpload?: () => void }) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    setSuccess(null);
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.type !== "application/pdf") {
      setError("Only PDF files are supported.");
      return;
    }
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      // Call FastAPI backend directly (adjust URL as needed)
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.error || "Upload failed.");
      } else {
        setSuccess(data.message || "Upload successful.");
        if (onUpload) onUpload();
      }
    } catch {
      setError("Network or server error.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="space-y-2">
      <input
        ref={fileInputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={handleFileChange}
        disabled={uploading}
      />
      <Button
        type="button"
        onClick={() => fileInputRef.current?.click()}
        disabled={uploading}
        className="bg-blue-600 hover:bg-blue-700 text-white"
      >
        {uploading ? "Uploading..." : "Upload PDF Document"}
      </Button>
      {error && <div className="text-red-600 text-sm">{error}</div>}
      {success && <div className="text-green-600 text-sm">{success}</div>}
    </div>
  );
}

export default DocumentUpload; 