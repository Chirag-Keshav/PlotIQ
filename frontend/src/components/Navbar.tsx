import { motion } from "motion/react";
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/clerk-react";

export default function Navbar() {
  const navItems = ["Discovery", "Intelligence", "Verification", "Growth"];

  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
      className="fixed top-6 left-1/2 -translate-x-1/2 w-[calc(100%-48px)] max-w-7xl z-50 px-6 py-4 glass-nav flex items-center justify-between"
    >
      <div className="flex items-center gap-2">
        <span className="text-2xl font-bold tracking-tighter text-white">PlotIQ</span>
      </div>

      <div className="hidden md:flex items-center gap-8">
        {navItems.map((item) => (
          <a
            key={item}
            href={`#${item.toLowerCase()}`}
            className="text-sm font-medium text-white/60 hover:text-white transition-colors"
          >
            {item}
          </a>
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
              elements: {
                avatarBox: "w-9 h-9 border border-white/20"
              }
            }}
          />
        </SignedIn>
        <button className="px-5 py-2 bg-white text-black text-sm font-bold rounded-lg hover:scale-105 transition-transform">
          Start Discovery
        </button>
      </div>
    </motion.nav>
  );
}
