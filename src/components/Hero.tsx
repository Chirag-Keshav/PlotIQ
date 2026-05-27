import { motion } from "motion/react";

export default function Hero() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.5,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } },
  };

  return (
    <div className="relative min-h-screen w-full flex items-center justify-start px-8 md:px-24 overflow-hidden">
      {/* Background Video */}
      <div className="absolute inset-0 z-0">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="w-full h-full object-cover scale-105"
        >
          <source
            src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260403_050628_c4e32401-fab4-4a27-b7a8-6e9291cd5959.mp4"
            type="video/mp4"
          />
        </video>
        {/* Absolute Black Overlay for depth */}
        <div className="absolute inset-0 bg-black/60 backdrop-blur-[2px]" />
      </div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="relative z-10 max-w-4xl pt-20"
      >
        <motion.h1
          variants={itemVariants}
          className="text-6xl md:text-8xl font-bold tracking-tight text-white leading-[1.1] mb-8"
        >
          Discovering land <br />
          with intelligence.
        </motion.h1>

        <motion.p
          variants={itemVariants}
          className="text-xl md:text-2xl text-white/70 max-w-2xl mb-12"
        >
          AI-powered due diligence for a transparent and secure land investment journey.
        </motion.p>

        <motion.div variants={itemVariants} className="flex flex-wrap gap-4">
          <button className="btn-primary">
            Get Started
          </button>
          <button className="btn-secondary">
            View Map
          </button>
        </motion.div>
      </motion.div>

      {/* Decorative Gradient */}
      <div className="absolute bottom-0 left-0 w-full h-32 bg-gradient-to-t from-black to-transparent z-10" />
    </div>
  );
}
