import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import GlassCard from "./components/GlassCard";
import { Shield, Brain, BarChart3, Globe } from "lucide-react";
import { motion } from "motion/react";
import DiscoverPage from "./pages/DiscoverPage";
import { RequireAuth, RequireAdmin } from "./lib/RequireAuth";

function HomePage() {
  return (
    <main className="relative min-h-screen bg-black overflow-x-hiddenSelection">
      <Navbar />
      <Hero />
      
      {/* Intelligence Section */}
      <section className="relative z-20 py-24 px-8 md:px-24 bg-black">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6">Our Intelligence Tiers</h2>
            <p className="text-gray-400 max-w-xl text-lg">
              Advanced neural networks analyze thousands of data points to ensure your investment is protected from every angle.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <GlassCard>
              <div className="h-12 w-12 rounded-lg bg-white/10 flex items-center justify-center mb-6">
                <Brain className="text-white h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold mb-3">AI Discovery</h3>
              <p className="text-sm text-gray-400">Deep search across jurisdictional records to find high-potential land assets.</p>
            </GlassCard>

            <GlassCard>
              <div className="h-12 w-12 rounded-lg bg-white/10 flex items-center justify-center mb-6">
                <Shield className="text-white h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Instant Verification</h3>
              <p className="text-sm text-gray-400">Blockchain-backed verification of ownership and historical claim data.</p>
            </GlassCard>

            <GlassCard>
              <div className="h-12 w-12 rounded-lg bg-white/10 flex items-center justify-center mb-6">
                <BarChart3 className="text-white h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Growth Analytics</h3>
              <p className="text-sm text-gray-400">Predictive modeling for land value appreciation based on infrastructure trends.</p>
            </GlassCard>

            <GlassCard>
              <div className="h-12 w-12 rounded-lg bg-white/10 flex items-center justify-center mb-6">
                <Globe className="text-white h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Spatial Survey</h3>
              <p className="text-sm text-gray-400">High-resolution satellite topography and environmental risk assessment.</p>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* Verification Placeholder Section */}
      <section className="relative z-20 py-24 px-8 md:px-24 border-t border-white/10 bg-gradient-to-b from-black to-[#050505]">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center gap-16">
          <div className="flex-1">
            <h2 className="text-4xl md:text-5xl font-bold mb-8 leading-tight">
              Liquid Verification. <br />
              <span className="text-white/40">Real-time certainty.</span>
            </h2>
            <p className="text-gray-400 text-lg mb-10">
              Stop waiting for months on traditional due diligence. PlotIQ delivers state-certified reports in seconds using our proprietary verification pipeline.
            </p>
            <div className="space-y-6">
              {[
                "Title Search & Chain of Custody",
                "Environmental Conflict Delta",
                "Infrastructure Proximity Score",
                "Legal Encumbrance Audit"
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-4 text-white/80">
                  <div className="h-2 w-2 rounded-full bg-white" />
                  <span className="font-medium">{item}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="flex-1 w-full flex justify-center">
            <div className="relative w-full aspect-square max-w-md">
              <div className="absolute inset-0 bg-white/5 rounded-3xl border border-white/20 backdrop-blur-2xl overflow-hidden shadow-2xl">
                <div className="p-8 h-full flex flex-col">
                  <div className="flex justify-between items-center mb-8">
                    <div className="h-10 w-10 bg-white text-black rounded-lg flex items-center justify-center font-bold">PIQ</div>
                    <div className="px-3 py-1 bg-green-500/20 text-green-400 text-xs font-bold rounded-full border border-green-500/30">VERIFIED</div>
                  </div>
                  <div className="space-y-4 mb-auto">
                    <div className="h-4 w-3/4 bg-white/10 rounded" />
                    <div className="h-4 w-1/2 bg-white/10 rounded" />
                    <div className="h-32 w-full bg-white/5 rounded-xl border border-white/10" />
                  </div>
                  <div className="pt-6 border-t border-white/10">
                    <div className="flex justify-between items-center text-xs text-white/40 mb-2">
                      <span>Trust Score</span>
                      <span>98.2%</span>
                    </div>
                    <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        whileInView={{ width: "98.2%" }}
                        transition={{ duration: 1.5, ease: "easeOut" }}
                        className="h-full bg-white"
                      />
                    </div>
                  </div>
                </div>
              </div>
              <div className="absolute -top-6 -right-6 h-32 w-32 bg-white/10 blur-3xl rounded-full" />
              <div className="absolute -bottom-6 -left-6 h-32 w-32 bg-white/10 blur-3xl rounded-full" />
            </div>
          </div>
        </div>
      </section>

      <footer className="relative z-20 py-12 px-8 border-t border-white/5 text-center text-white/30 text-sm">
        <p>&copy; 2026 PlotIQ Systems Inc. All human rights reserved.</p>
      </footer>
    </main>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/discover" element={
          <RequireAuth>
            <DiscoverPage />
          </RequireAuth>
        } />
        {/* Mock remaining routes for POC */}
        <Route path="/listings/:id" element={<div>Listing Detail</div>} />
        <Route path="/sell" element={<RequireAuth><div>Sell Page</div></RequireAuth>} />
        <Route path="/admin" element={<RequireAdmin><div>Admin Dashboard</div></RequireAdmin>} />
        <Route path="/legal" element={<div>Legal Disclaimers</div>} />
      </Routes>
    </BrowserRouter>
  );
}
