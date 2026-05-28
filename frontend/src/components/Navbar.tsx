import { Link, useLocation } from "react-router-dom";
import { motion } from "motion/react";
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/clerk-react";

const NAV_LINKS = [
  { label: "Discover", to: "/discover" },
  { label: "List a Plot", to: "/sell" },
  { label: "Legal", to: "/legal" },
];

export default function Navbar() {
  const { pathname } = useLocation();

  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
      className="fixed top-6 left-1/2 -translate-x-1/2 w-[calc(100%-48px)] max-w-7xl z-50 px-6 py-4 glass-nav flex items-center justify-between"
    >
      <Link to="/" className="flex items-center gap-2">
        <span className="text-2xl font-bold tracking-tighter text-white">PlotIQ</span>
      </Link>

      <div className="hidden md:flex items-center gap-8">
        {NAV_LINKS.map(({ label, to }) => (
          <Link
            key={to}
            to={to}
            className={`text-sm font-medium transition-colors ${
              pathname === to ? "text-white" : "text-white/60 hover:text-white"
            }`}
          >
            {label}
          </Link>
        ))}
      </div>

      <div className="flex items-center gap-4">
        <SignedOut>
          <SignInButton mode="modal">
            <button className="px-5 py-2 bg-white/10 text-white text-sm font-bold rounded-lg hover:bg-white/20 transition-colors border border-white/20">
              Sign In
            </button>
          </SignInButton>
        </SignedOut>
        <SignedIn>
          <UserButton
            appearance={{
              elements: { avatarBox: "w-9 h-9 border border-white/20" },
            }}
          />
        </SignedIn>
        <Link to="/discover" className="btn-primary text-sm">
          Start Discovery
        </Link>
      </div>
    </motion.nav>
  );
}
