import React from 'react';
import { Copy, Check } from 'lucide-react';

interface WhatsAppPreviewProps {
  text: string;
  title: string;
  isSent: boolean;
  onCopy: (text: string) => void;
}

const formatWhatsAppText = (text: string) => {
  // Simple regex to basic HTML formatting for preview purposes
  // Note: This is a visual approximation
  let formatted = text
    .replace(/\*(.*?)\*/g, '<strong>$1</strong>') // Bold
    .replace(/_(.*?)_/g, '<em>$1</em>') // Italics
    .replace(/\n/g, '<br />'); // Newlines

  return { __html: formatted };
};

export const WhatsAppPreview: React.FC<WhatsAppPreviewProps> = ({ text, title, isSent, onCopy }) => {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = () => {
    onCopy(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="mb-6 last:mb-0">
      <div className="flex justify-between items-center mb-2 px-1">
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">{title}</span>
        <button 
          onClick={handleCopy}
          className="flex items-center gap-1 text-xs font-medium text-blue-600 hover:text-blue-700 transition-colors"
        >
          {copied ? <Check size={14} /> : <Copy size={14} />}
          {copied ? 'Copied' : 'Copy Text'}
        </button>
      </div>
      
      <div className={`relative p-3 rounded-lg max-w-[90%] text-sm leading-relaxed shadow-sm ${
        isSent ? 'bg-[#dcf8c6] ml-auto rounded-tr-none' : 'bg-white mr-auto rounded-tl-none'
      }`}>
        <div 
          className="whitespace-pre-wrap text-gray-800"
          dangerouslySetInnerHTML={formatWhatsAppText(text)} 
        />
        <div className="text-[10px] text-gray-500 text-right mt-1 flex justify-end gap-1 items-center">
          <span>{new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
          {isSent && <span className="text-blue-500">✓✓</span>}
        </div>
      </div>
    </div>
  );
};
