import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { fetchHealth } from '../lib/api';

const Header = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  const [apiOk, setApiOk] = useState(null);
  useEffect(() => {
    fetchHealth()
      .then(() => setApiOk(true))
      .catch(() => setApiOk(false));
  }, []);

  
  const navigation = [
    { name: 'Home', path: '/' },
    { name: 'About', path: '/about' },
    { name: 'Services', path: '/services' },
    // { name: 'Pricing', path: '/pricing' },
    { name: 'Workshops', path: '/workshops' },
    { name: 'Contact', path: '/contact' },
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-50 transition-all duration-300 glassmorphism">
      <div className="container mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          <Link to="/" className="text-2xl font-bold tracking-tighter">
            Superbloom<span className="gradient-text">.</span>
          </Link>

          <nav className="hidden md:flex space-x-8 items-center">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.path}
                className={`text-gray-300 hover:gradient-text transition-colors duration-300 ${
                  isActive(item.path) ? 'gradient-text' : ''
                }`}
              >
                {item.name}
              </Link>
            ))}
            {apiOk !== null && (
              <span className={`text-xs px-2 py-1 rounded-full border ${apiOk ? 'border-green-500 text-green-400' : 'border-red-500 text-red-400'}`}>
                {apiOk ? 'API: OK' : 'API: DOWN'}
              </span>
            )}
            <Link
              to="/contact"
              className="gradient-bg text-white font-semibold py-2 px-5 rounded-full hover:opacity-90 transition-opacity duration-300"
            >
              Let's Talk
            </Link>
          </nav>

          <button
            type="button"
            className="md:hidden text-white"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={mobileMenuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} />
            </svg>
          </button>
        </div>

        {/* Mobile menu */}
        <div
          className={`md:hidden px-2 pb-4 ${
            mobileMenuOpen ? 'block' : 'hidden'
          }`}
        >
          {navigation.map((item) => (
            <Link
              key={item.name}
              to={item.path}
              className={`block py-2 text-gray-300 hover:gradient-text ${
                isActive(item.path) ? 'gradient-text' : ''
              }`}
              onClick={() => setMobileMenuOpen(false)}
            >
              {item.name}
            </Link>
          ))}
          <Link
            to="/contact"
            className="block mt-2 gradient-bg text-white font-semibold py-2 px-5 rounded-full text-center"
            onClick={() => setMobileMenuOpen(false)}
          >
            Let's Talk
          </Link>
        </div>
      </div>
    </header>
  );
};

export default Header;
