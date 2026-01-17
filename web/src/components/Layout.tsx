import { Outlet, Link, useLocation } from 'react-router-dom';
import { motion } from 'motion/react';
import { useAuth } from '../hooks/useAuth';
import { MobileNav } from './MobileNav';
import { LogOutIcon } from './icons';
import { EchoLogo } from './EchoLogo';

export function Layout() {
  const { user, signOut } = useAuth();
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen flex flex-col bg-surface-0">
      <header className="bg-surface-1 border-b border-surface-3 sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 group">
            <EchoLogo size={36} />
            <span className="font-semibold text-gray-100 tracking-wide group-hover:text-echo-400 transition-colors">
              Echo
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-1">
            {[
              { path: '/', label: 'Home' },
              ...(user ? [
                { path: '/history', label: 'History' },
                { path: '/patients', label: 'Patients' },
                { path: '/profile', label: 'Profile' },
                ...(user.role === 'admin' ? [{ path: '/admin', label: 'Admin' }] : []),
              ] : []),
            ].map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className="relative px-4 py-2 rounded-xl text-sm font-medium transition-all"
              >
                <span className={isActive(item.path) ? 'text-echo-400' : 'text-gray-400 hover:text-gray-200'}>
                  {item.label}
                </span>
                {isActive(item.path) && (
                  <motion.div
                    layoutId="navIndicator"
                    className="absolute bottom-0 left-2 right-2 h-0.5 bg-echo-500 rounded-full"
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  />
                )}
              </Link>
            ))}

            {user ? (
              <motion.button
                onClick={() => signOut()}
                className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium text-gray-400 hover:text-gray-200 hover:bg-surface-3 transition-all"
                whileHover={{ x: 2 }}
                whileTap={{ scale: 0.98 }}
              >
                <LogOutIcon size={16} />
                Sign out
              </motion.button>
            ) : (
              <Link
                to="/login"
                className="px-4 py-2 rounded-xl text-sm font-medium text-echo-400 hover:bg-echo-500/10 transition-all"
              >
                Sign in
              </Link>
            )}
          </nav>
        </div>
      </header>

      <main className="flex-1 pb-20 md:pb-0">
        <Outlet />
      </main>

      <footer className="hidden md:block bg-surface-1 border-t border-surface-3 py-4">
        <div className="max-w-4xl mx-auto px-4 text-center text-sm text-gray-500">
          <span className="text-gradient font-medium">Echo</span>
          <span className="mx-2">·</span>
          Your AI Medical Attending
        </div>
      </footer>

      <MobileNav />
    </div>
  );
}
