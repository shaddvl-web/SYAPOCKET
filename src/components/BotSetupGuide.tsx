import React, { useState } from 'react';
import { Terminal, Copy, Check, Shield, Server, Cpu } from 'lucide-react';

export const BotSetupGuide: React.FC = () => {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 1500);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white border border-zinc-200 rounded-xl p-5 shadow-xs space-y-4">
        <div className="flex items-center gap-2">
          <Terminal className="w-5 h-5 text-blue-600" />
          <h2 className="font-semibold text-zinc-900 text-sm">Deployment & Configuration Playbook</h2>
        </div>
        <p className="text-xs text-zinc-600">
          The Telegram Bot is 100% self-contained in Python 3.12 with asynchronous event loops, SQLite WAL persistence, and optional FastAPI webhook serving.
        </p>

        {/* Step 1: BotFather */}
        <div className="p-4 rounded-xl bg-zinc-50 border border-zinc-200/70 space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-xs text-zinc-900">Step 1: Obtain Token from @BotFather</span>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-zinc-200 text-zinc-700">Telegram</span>
          </div>
          <ol className="list-decimal list-inside text-xs text-zinc-600 space-y-1">
            <li>Search for <strong>@BotFather</strong> on Telegram and send <code>/newbot</code>.</li>
            <li>Choose a display name and unique username ending in <code>bot</code>.</li>
            <li>Copy the resulting HTTP API token (e.g. <code>123456789:ABCdefGHI...</code>).</li>
          </ol>
        </div>

        {/* Step 2: Environment file */}
        <div className="p-4 rounded-xl bg-zinc-50 border border-zinc-200/70 space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-xs text-zinc-900">Step 2: Configure .env Variables</span>
            <button
              onClick={() => copyToClipboard('cp .env.example .env', 'env-copy')}
              className="text-[11px] flex items-center gap-1 text-blue-600 hover:text-blue-800"
            >
              {copiedKey === 'env-copy' ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
              Copy command
            </button>
          </div>
          <div className="bg-zinc-950 text-zinc-200 font-mono text-xs p-3 rounded-lg overflow-x-auto">
            <p>TELEGRAM_BOT_TOKEN="your_token_here"</p>
            <p>ADMIN_IDS="your_telegram_chat_id"</p>
            <p>BOT_MODE="polling"</p>
            <p>PORT=3000</p>
          </div>
        </div>

        {/* Step 3: Run modes */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl border border-zinc-200 bg-white shadow-2xs space-y-2">
            <div className="flex items-center gap-2 text-zinc-900 font-semibold text-xs">
              <Cpu className="w-4 h-4 text-blue-600" /> Windows
            </div>
            <p className="text-xs text-zinc-500">Run the preconfigured batch script:</p>
            <div className="bg-zinc-900 text-zinc-200 font-mono text-[11px] p-2 rounded">
              run_windows.bat
            </div>
          </div>

          <div className="p-4 rounded-xl border border-zinc-200 bg-white shadow-2xs space-y-2">
            <div className="flex items-center gap-2 text-zinc-900 font-semibold text-xs">
              <Server className="w-4 h-4 text-blue-600" /> Linux / VPS
            </div>
            <p className="text-xs text-zinc-500">Run the automated bash runner:</p>
            <div className="bg-zinc-900 text-zinc-200 font-mono text-[11px] p-2 rounded">
              ./run_linux.sh polling
            </div>
          </div>

          <div className="p-4 rounded-xl border border-zinc-200 bg-white shadow-2xs space-y-2">
            <div className="flex items-center gap-2 text-zinc-900 font-semibold text-xs">
              <Shield className="w-4 h-4 text-blue-600" /> Docker Compose
            </div>
            <p className="text-xs text-zinc-500">Multi-stage container with persistent volume:</p>
            <div className="bg-zinc-900 text-zinc-200 font-mono text-[11px] p-2 rounded">
              docker compose up -d
            </div>
          </div>
        </div>

        {/* Interactive Command Reference */}
        <div className="border-t border-zinc-100 pt-4">
          <h3 className="font-semibold text-zinc-900 text-xs uppercase tracking-wider mb-3">
            Supported Telegram Commands
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 text-xs">
            <div className="p-2.5 rounded-lg bg-zinc-50 border border-zinc-100">
              <code className="font-bold text-blue-600">/start</code>
              <p className="text-zinc-500 text-[11px] mt-0.5">Welcome screen, disclaimer, main menu</p>
            </div>
            <div className="p-2.5 rounded-lg bg-zinc-50 border border-zinc-100">
              <code className="font-bold text-blue-600">/analyze</code>
              <p className="text-zinc-500 text-[11px] mt-0.5">Interactive Asset/TF/Expiration selector</p>
            </div>
            <div className="p-2.5 rounded-lg bg-zinc-50 border border-zinc-100">
              <code className="font-bold text-blue-600">/signal</code>
              <p className="text-zinc-500 text-[11px] mt-0.5">Immediate 1-click quantitative recommendation</p>
            </div>
            <div className="p-2.5 rounded-lg bg-zinc-50 border border-zinc-100">
              <code className="font-bold text-blue-600">/screenshot</code>
              <p className="text-zinc-500 text-[11px] mt-0.5">Vision AI analysis of uploaded chart</p>
            </div>
            <div className="p-2.5 rounded-lg bg-zinc-50 border border-zinc-100">
              <code className="font-bold text-blue-600">/demo</code>
              <p className="text-zinc-500 text-[11px] mt-0.5">Interactive paper trade journal logger</p>
            </div>
            <div className="p-2.5 rounded-lg bg-zinc-50 border border-zinc-100">
              <code className="font-bold text-blue-600">/stats</code>
              <p className="text-zinc-500 text-[11px] mt-0.5">Win rate, net PnL, discipline metrics</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
