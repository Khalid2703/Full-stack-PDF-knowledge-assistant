'use client';

import Link from 'next/link';

export default function AnalyticsPage() {
  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">Analytics</h1>
        <p className="text-gray-600 mb-6">Usage insights and document analytics will appear here.</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 border rounded-lg">
            <h3 className="text-sm font-medium">Chats</h3>
            <p className="text-2xl font-bold">—</p>
            <p className="text-xs text-gray-500">Conversations started</p>
          </div>

          <div className="p-4 border rounded-lg">
            <h3 className="text-sm font-medium">Documents</h3>
            <p className="text-2xl font-bold">—</p>
            <p className="text-xs text-gray-500">Uploaded files</p>
          </div>

          <div className="p-4 border rounded-lg">
            <h3 className="text-sm font-medium">Embeddings</h3>
            <p className="text-2xl font-bold">—</p>
            <p className="text-xs text-gray-500">Vectors stored</p>
          </div>
        </div>

        <div className="mt-8 border rounded p-4">
          <h2 className="font-medium mb-2">Document Activity</h2>
          <p className="text-sm text-gray-500">Recent uploads and processing status will be shown here.</p>

          <div className="mt-4">
            <Link href="/upload">
              <a className="text-sm text-blue-600">Go to Uploads</a>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
