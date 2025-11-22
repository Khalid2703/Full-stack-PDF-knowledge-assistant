import jsPDF from 'jspdf';

export const exportToJSON = (data: any, filename: string) => {
  const jsonStr = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonStr], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${filename}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

export const exportToPDF = (
  content: string,
  filename: string,
  title?: string
) => {
  const doc = new jsPDF();
  
  // Add title
  if (title) {
    doc.setFontSize(18);
    doc.text(title, 20, 20);
    doc.setFontSize(12);
  }
  
  // Split content into lines
  const lines = doc.splitTextToSize(content, 170);
  
  // Add content
  let y = title ? 35 : 20;
  lines.forEach((line: string) => {
    if (y > 280) {
      doc.addPage();
      y = 20;
    }
    doc.text(line, 20, y);
    y += 7;
  });
  
  // Save PDF
  doc.save(`${filename}.pdf`);
};

export const exportChatToPDF = (messages: any[], filename: string) => {
  const doc = new jsPDF();
  
  // Title
  doc.setFontSize(18);
  doc.text('Chat Export - Regnova', 20, 20);
  doc.setFontSize(10);
  doc.text(`Generated: ${new Date().toLocaleString()}`, 20, 28);
  
  let y = 40;
  
  messages.forEach((msg, index) => {
    // Check if need new page
    if (y > 270) {
      doc.addPage();
      y = 20;
    }
    
    // Role header
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.text(msg.role === 'user' ? 'You:' : 'Assistant:', 20, y);
    y += 7;
    
    // Message content
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    const lines = doc.splitTextToSize(msg.content, 170);
    lines.forEach((line: string) => {
      if (y > 280) {
        doc.addPage();
        y = 20;
      }
      doc.text(line, 20, y);
      y += 6;
    });
    
    y += 5; // Space between messages
  });
  
  doc.save(`${filename}.pdf`);
};

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};
