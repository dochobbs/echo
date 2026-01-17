import { Link, useLocation } from 'react-router-dom';
import { motion } from 'motion/react';
import { useAuth } from '../hooks/useAuth';
import { HomeIcon, HistoryIcon, UserIcon, StethoscopeIcon, LoginIcon, FolderIcon } from './icons';

export function MobileNav() {
  const location = useLocation();
  const { user } = useAuth();

  const navItems = [
    { path: '/', label: 'Home', Icon: HomeIcon },
    { path: '/case', label: 'Case', Icon: StethoscopeIcon, requiresCase: true },
    ...(user ? [
      { path: '/history', label: 'History', Icon: HistoryIcon },
      { path: '/patients', label: 'Patients', Icon: FolderIcon },
      { path: '/profile', label: 'Profile', Icon: UserIcon },
    ] : [
      { path: '/login', label: 'Sign in', Icon: LoginIcon },
    ]),
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-surface-1 border-t border-surface-3 px-2 py-2 md:hidden z-50">
      <div className="flex justify-around items-center max-w-md mx-auto">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.Icon;

          return (
            <Link
              key={item.path}
              to={item.path}
              className="relative flex flex-col items-center py-1 px-3"
            >
              <motion.div
                className={`mb-0.5 transition-colors ${isActive ? 'text-echo-400' : 'text-gray-500'}`}
                whileTap={{ scale: 0.9 }}
              >
                <Icon size={22} />
              </motion.div>
              <span className={`text-xs font-medium ${isActive ? 'text-echo-400' : 'text-gray-500'}`}>
                {item.label}
              </span>
              
              {isActive && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-1 h-1 bg-echo-400 rounded-full"
                  transition={{ type: "spring", stiffness: 500, damping: 30 }}
                />
              )}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
