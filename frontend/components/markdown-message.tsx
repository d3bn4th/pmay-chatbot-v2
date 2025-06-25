import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Components } from "react-markdown";

// Custom renderer for code blocks with copy button
const CodeBlock: Components["code"] = (props) => {
  const [copied, setCopied] = React.useState(false);
  const { children, inline = false, ...rest } = props as { children: React.ReactNode; inline?: boolean };
  const code = String(children).replace(/\n$/, "");

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  };

  if (inline) {
    return <code className="bg-gray-100 rounded px-1 py-0.5 font-mono text-sm">{children}</code>;
  }
  return (
    <div className="relative group my-4">
      <pre className="bg-gray-900 text-gray-100 rounded-lg p-4 overflow-x-auto text-sm font-mono">
        <code {...rest}>{code}</code>
      </pre>
      <button
        onClick={handleCopy}
        className="absolute top-2 right-2 bg-gray-800 text-gray-200 px-2 py-1 rounded text-xs opacity-0 group-hover:opacity-100 transition-opacity border border-gray-700 hover:bg-gray-700"
        title="Copy code"
      >
        {copied ? "Copied!" : "Copy"}
      </button>
    </div>
  );
};

const MarkdownMessage = ({ children }: { children: string }) => (
  <ReactMarkdown
    remarkPlugins={[remarkGfm]}
    components={{
      code: CodeBlock,
      a: (props) => (
        <a
          {...props}
          className="text-blue-600 underline hover:text-blue-800 break-all"
          target="_blank"
          rel="noopener noreferrer"
        />
      ),
      h1: (props) => <h1 className="text-2xl font-bold mt-4 mb-2" {...props} />,
      h2: (props) => <h2 className="text-xl font-semibold mt-4 mb-2" {...props} />,
      h3: (props) => <h3 className="text-lg font-semibold mt-3 mb-1" {...props} />,
      ul: (props) => <ul className="list-disc ml-6 my-2" {...props} />,
      ol: (props) => <ol className="list-decimal ml-6 my-2" {...props} />,
      li: (props) => <li className="mb-1" {...props} />,
      blockquote: (props) => <blockquote className="border-l-4 border-blue-300 pl-4 italic text-gray-600 my-2" {...props} />,
      table: (props) => <table className="min-w-full border border-gray-300 my-4" {...props} />,
      th: (props) => <th className="border px-2 py-1 bg-gray-100" {...props} />,
      td: (props) => <td className="border px-2 py-1" {...props} />,
      p: (props) => <p className="my-2" {...props} />,
    }}
  >
    {children}
  </ReactMarkdown>
);

export default MarkdownMessage; 