import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { AnalyzerConsole } from './components/AnalyzerConsole';
import { ChartSimulator } from './components/ChartSimulator';
import { VisionSimulator } from './components/VisionSimulator';
import { TradeJournal } from './components/TradeJournal';
import { BotSetupGuide } from './components/BotSetupGuide';
import { SystemConfigManager } from './components/SystemConfigManager';

export default function App() {
  const [activeTab, setActiveTab] = useState<'analyzer' | 'chart' | 'vision' | 'journal' | 'setup' | 'config'>('analyzer');

  return (
    <div className="min-h-screen bg-zinc-100/60 text-zinc-900 font-sans antialiased flex flex-col">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {activeTab === 'analyzer' && <AnalyzerConsole onNavigateToConfig={() => setActiveTab('config')} />}
        {activeTab === 'chart' && <ChartSimulator />}
        {activeTab === 'vision' && <VisionSimulator />}
        {activeTab === 'journal' && <TradeJournal />}
        {activeTab === 'config' && <SystemConfigManager />}
        {activeTab === 'setup' && <BotSetupGuide />}
      </main>

      <footer className="border-t border-zinc-200 bg-white py-4 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-wrap items-center justify-between text-xs text-zinc-500 gap-2">
          <span>Pocket Option AI Analyzer Bot • Institutional Quantitative Engine</span>
          <span>Confirmation &gt; Prediction • Strict 70% Confluence Gate</span>
        </div>
      </footer>
    </div>
  );
}
