import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import GlassCard from "./components/GlassCard";
import { Shield, Brain, BarChart3, Globe } from "lucide-react";
import { motion } from "motion/react";
import DiscoverPage from "./pages/DiscoverPage";
import ListingDetailPage from "./pages/ListingDetailPage";
import SellerPage from "./pages/SellerPage";
import AdminDashboard from "./pages/AdminDashboard";
import LegalPage from "./pages/LegalPage";
import { RequireAuth, RequireAdmin } from "./lib/RequireAuth";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 60_000 },
  },
});

function HomePage() {
  return (
    <main className="relative min-h-screen bg-black overflow-x-hidden">
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
            {[
              { icon: Brain, title: "AI Discovery", desc: "Deep search across jurisdictional records to find high-potential land assets." },
              { icon: Shield, title: "Instant Verification", desc: "AI-backed verification of ownership and historical claim data." },
              { icon: BarChart3, title: "Growth Analytics", desc: "Predictive modeling for land value appreciation based on infrastructure trends." },
              { icon: Globe, title: "Spatial Survey", desc: "High-resolution satellite topography and environmental risk assessment." },
            ].map(({ icon: Icon, title, desc }) => (
              <GlassCard key={title}>
                <div className="h-12 w-12 rounded-lg bg-white/10 flex items-center justify-center mb-6">
                  <Icon className="text-white h-6 w-6" />
                </div>
                <h3 className="text-xl font-semibold mb-3">{title}</h3>
                <p className="text-sm text-gray-400">{desc}</p>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      {/* Verification Section */}
      <section className="relative z-20 py-24 px-8 md:px-24 border-t border-white/10 bg-gradient-to-b from-black to-[#050505]">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center gap-16">
          <div className="flex-1">
            <h2 className="text-4xl md:text-5xl font-bold mb-8 leading-tight">
              Liquid Verification. <br />
              <span className="text-white/40">Real-time certainty.</span>
            </h2>
            <p className="text-gray-400 text-lg mb-10">
              Stop waiting on traditional due diligence. PlotIQ delivers AI-powered reports using our verification pipeline.
            </p>
            <div className="space-y-6">
              {["Title Search & Chain of Custody", "Environmental Conflict Delta", "Infrastructure Proximity Score", "Legal Encumbrance Audit"].map((item, i) => (
                <div key={i} className="flex items-center gap-4 text-white/80">
                  <div className="h-2 w-2 rounded-full bg-white" />
                  <span className="font-medium">{item}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="flex-1 w-full flex justify-center">
            <div className="relative w-full aspect-square max-w-md">
              <div className="absolute inset-0 bg-white/5 rounded-3xl border border-white/20 backdrop-blur-2xl overflow-hidden shadow-2xl p-8 flex flex-col">
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
                    <span>Trust Score</span><span>98.2%</span>
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
          </div>
        </div>
      </section>

      <footer className="relative z-20 py-12 px-8 border-t border-white/5 text-center text-white/30 text-sm">
        <p>&copy; 2026 PlotIQ Systems Inc. &middot; <a href="/legal" className="hover:text-white/60 transition-colors">Legal & Disclaimers</a></p>
      </footer>
    </main>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/discover" element={<DiscoverPage />} />
          <Route path="/listings/:id" element={<ListingDetailPage />} />
          <Route path="/sell" element={<RequireAuth><SellerPage /></RequireAuth>} />
          <Route path="/admin" element={<RequireAdmin><AdminDashboard /></RequireAdmin>} />
          <Route path="/legal" element={<LegalPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
