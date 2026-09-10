import React from 'react';
import { Bot, ShieldCheck, Activity, Terminal } from 'lucide-react';

interface NavbarProps {
  activeTab: 'analyzer' | 'chart' | 'vision' | 'journal' | 'setup' | 'config';
  setActiveTab: (tab: 'analyzer' | 'chart' | 'vision' | 'journal' | 'setup' | 'config') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  return (
    <header className="border-b border-zinc-200 bg-white sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-sm">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-zinc-900 tracking-tight">Pocket Option AI Analyzer</span>
              <span className="px-2 py-0.5 text-xs font-medium rounded-md bg-zinc-100 text-zinc-700 border border-zinc-200">
                v1.0.0
              </span>
            </div>
            <p className="text-xs text-zinc-500 hidden sm:block">Quantitative Decision-Support & Confluence Engine</p>
          </div>
        </div>

        <nav className="flex items-center gap-1 sm:gap-2">
          <button
            id="nav-analyzer-btn"
            onClick={() => setActiveTab('analyzer')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'analyzer'
                ? 'bg-zinc-900 text-white'
                : 'text-zinc-600 hover:text-zinc-900 hover:bg-zinc-100'
            }`}
          >
            Live Analyzer
          </button>
          <button
            id="nav-chart-btn"
            onClick={() => setActiveTab('chart')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'chart'
                ? 'bg-zinc-900 text-white'
                : 'text-zinc-600 hover:text-zinc-900 hover:bg-zinc-100'
            }`}
          >
            SMC Chart
          </button>
          <button
            id="nav-vision-btn"
            onClick={() => setActiveTab('vision')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'vision'
                ? 'bg-zinc-900 text-white'
                : 'text-zinc-600 hover:text-zinc-900 hover:bg-zinc-100'
            }`}
          >
            Vision AI
          </button>
          <button
            id="nav-journal-btn"
            onClick={() => setActiveTab('journal')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'journal'
                ? 'bg-zinc-900 text-white'
                : 'text-zinc-600 hover:text-zinc-900 hover:bg-zinc-100'
            }`}
          >
            Journal & Stats
          </button>
          <button
            id="nav-config-btn"
            onClick={() => setActiveTab('config')}
            className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition-colors flex items-center gap-1.5 ${
              activeTab === 'config'
                ? 'bg-blue-600 text-white shadow-xs'
                : 'text-blue-600 hover:bg-blue-50 border border-blue-200'
            }`}
          >
            ⚙️ System Config
          </button>
          <button
            id="nav-setup-btn"
            onClick={() => setActiveTab('setup')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              activeTab === 'setup'
                ? 'bg-zinc-900 text-white'
                : 'text-zinc-600 hover:text-zinc-900 hover:bg-zinc-100'
            }`}
          >
            Bot Setup
          </button>
        </nav>
      </div>
    </header>
  );
};
