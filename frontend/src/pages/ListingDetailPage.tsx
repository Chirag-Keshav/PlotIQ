import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useListing } from '../hooks/useListing';
// import { BreadcrumbNav, ListingHeader, TabNav } from '../components/listing';
// Tabs
// import OverviewTab from '../components/listing/tabs/OverviewTab';
// import AIScoreTab from '../components/listing/tabs/AIScoreTab';
// import LegalDocsTab from '../components/listing/tabs/LegalDocsTab';
// import PriceIntelligenceTab from '../components/listing/tabs/PriceIntelligenceTab';
// import LocationIntelligenceTab from '../components/listing/tabs/LocationIntelligenceTab';
// import FutureGrowthTab from '../components/listing/tabs/FutureGrowthTab';
// import RiskSummaryTab from '../components/listing/tabs/RiskSummaryTab';

export default function ListingDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: listing, isLoading } = useListing(id || null);
  const [activeTab, setActiveTab] = useState('overview');

  if (isLoading) {
    return <div className="text-white text-center py-20">Loading...</div>;
  }

  if (!listing) {
    return <div className="text-white text-center py-20">Listing not found</div>;
  }

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'score', label: 'AI Score' },
    { id: 'legal', label: 'Legal Docs' },
    { id: 'price', label: 'Price Intel' },
    { id: 'location', label: 'Location Intel' },
    { id: 'growth', label: 'Future Growth' },
    { id: 'risk', label: 'Risk Summary' },
  ];

  return (
    <div className="min-h-screen bg-black text-white pt-20 px-8 max-w-7xl mx-auto">
      <Link to="/discover" className="text-white/50 hover:text-white mb-6 inline-block">
        ← Back to Map
      </Link>
      
      <div className="mb-8">
        <h1 className="text-4xl font-bold">{listing.title}</h1>
        <p className="text-xl text-white/60">{listing.locality} • {listing.area_sqyd} sqyd</p>
        <div className="mt-4 text-3xl font-mono font-bold">₹{listing.price_lakhs}L</div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-4 border-b border-white/10 mb-8 overflow-x-auto">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 whitespace-nowrap ${
              activeTab === tab.id ? 'border-b-2 border-white text-white' : 'text-white/50 hover:text-white/80'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="bg-white/5 border border-white/10 rounded-xl p-6 min-h-[400px]">
        {activeTab === 'overview' && <div>Overview Content</div>}
        {activeTab === 'score' && <div>AI Confidence Score: {listing.confidence_score}</div>}
        {activeTab === 'legal' && <div>Legal Documents Tracker</div>}
        {activeTab === 'price' && <div>Price Intelligence & Comparables</div>}
        {activeTab === 'location' && <div>Location & POI Map</div>}
        {activeTab === 'growth' && <div>Future Infrastructure Growth Signals</div>}
        {activeTab === 'risk' && <div>Risk & Fraud Summary</div>}
      </div>
    </div>
  );
}
