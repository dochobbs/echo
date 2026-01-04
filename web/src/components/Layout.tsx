import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function Layout() {
  const { user, signOut } = useAuth();
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-echo-600 rounded-lg flex items-center justify-center">
              <svg
                className="w-5 h-5 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
            </div>
            <span className="font-semibold text-gray-900">Echo</span>
          </Link>

          <nav className="flex items-center gap-1">
            <Link
              to="/"
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive('/')
                  ? 'bg-echo-50 text-echo-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Home
            </Link>
            {user && (
              <>
                <Link
                  to="/history"
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive('/history')
                      ? 'bg-echo-50 text-echo-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  History
                </Link>
                <Link
                  to="/profile"
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive('/profile')
                      ? 'bg-echo-50 text-echo-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  Profile
                </Link>
              </>
            )}
            {user ? (
              <button
                onClick={() => signOut()}
                className="px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-100"
              >
                Sign out
              </button>
            ) : (
              <Link
                to="/login"
                className="px-3 py-2 rounded-lg text-sm font-medium text-echo-600 hover:bg-echo-50"
              >
                Sign in
              </Link>
            )}
          </nav>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-4">
        <div className="max-w-4xl mx-auto px-4 text-center text-sm text-gray-500">
          Echo - Your AI Medical Attending
        </div>
      </footer>
    </div>
  );
}
