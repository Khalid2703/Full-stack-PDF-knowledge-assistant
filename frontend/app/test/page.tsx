'use client';

export default function TestPage() {
  return (
    <div className="min-h-screen bg-red-500 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-xl">
        <h1 className="text-4xl font-bold text-blue-600 mb-4">
          Tailwind Test Page
        </h1>
        <p className="text-gray-700 mb-4">
          If you see colors and styling, Tailwind is working!
        </p>
        <div className="space-y-2">
          <div className="bg-blue-100 p-4 rounded">Blue background</div>
          <div className="bg-green-100 p-4 rounded">Green background</div>
          <div className="bg-purple-100 p-4 rounded">Purple background</div>
        </div>
        <button className="mt-4 bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition">
          Click me!
        </button>
      </div>
    </div>
  );
}
