import { Link, useLocation } from 'react-router-dom';
import { motion } from 'motion/react';
import { useAuth } from '../hooks/useAuth';

const navItems = [
  { path: '/', label: 'Home', icon: '🏠' },
  { path: '/case', label: 'Case', icon: '📋', requiresCase: true },
  { path: '/history', label: 'History', icon: '📚', requiresAuth: true },
  { path: '/profile', label: 'Profile', icon: '👤', requiresAuth: true },
];

export function MobileNav() {
  const location = useLocation();
  const { user } = useAuth();

  const filteredItems = navItems.filter(item => {
    if (item.requiresAuth && !user) return false;
    return true;
  });

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-surface-1 border-t border-surface-3 px-2 py-2 md:hidden z-50">
      <div className="flex justify-around items-center max-w-md mx-auto">
        {filteredItems.map((item) => {
          const isActive = location.pathname === item.path;

          return (
            <Link
              key={item.path}
              to={item.path}
              className="relative flex flex-col items-center py-1 px-3"
            >
              <motion.div
                className={`text-xl mb-0.5 transition-transform ${isActive ? 'scale-110' : ''}`}
                whileTap={{ scale: 0.9 }}
              >
                {item.icon}
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
