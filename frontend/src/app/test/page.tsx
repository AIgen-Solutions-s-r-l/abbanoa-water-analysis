export default function TestPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
        Test Page - No Auth Required
      </h1>
      <p className="text-gray-600 dark:text-gray-400 mb-4">
        If you can see this, the Next.js app is working correctly!
      </p>
      <div className="space-y-2">
        <p className="text-sm text-gray-500">
          Frontend running on: http://localhost:8502
        </p>
        <p className="text-sm text-gray-500">
          Mock API running on: http://localhost:8001
        </p>
      </div>
      <div className="mt-8">
        <a 
          href="/auth/login" 
          className="text-blue-600 hover:text-blue-700 underline"
        >
          Go to Login Page
        </a>
      </div>
    </div>
  );
} 