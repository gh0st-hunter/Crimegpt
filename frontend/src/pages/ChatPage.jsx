import { useState, useRef, useEffect, useCallback } from 'react';
import { chatAPI } from '../api';
import { useAuth } from '../AuthContext';
import {
  Send, Bot, User, Shield, Sparkles, Laptop, Search, HelpCircle,
  Scale, BookOpen, Globe, Command, ChevronDown, X, Hash, Zap,
  Copy, Check, RotateCcw, MessageSquare
} from 'lucide-react';

// ─── Constants ────────────────────────────────────────────────────────────────

const CONTEXTS = [
  { key: 'general', label: 'General', icon: HelpCircle, desc: 'General assistance', color: '#6366f1' },
  { key: 'victim_guidance', label: 'Victim Aid', icon: Shield, desc: 'Legal rights & safety', color: '#ec4899' },
  { key: 'investigation', label: 'Investigate', icon: Search, desc: 'Investigation help', color: '#f59e0b' },
  { key: 'cybercrime', label: 'Cybercrime', icon: Laptop, desc: 'Cyber awareness', color: '#06b6d4' },
  { key: 'laws', label: 'Laws', icon: Scale, desc: 'BNS/IPC sections', color: '#10b981' },
  { key: 'landmark', label: 'Judgments', icon: BookOpen, desc: 'Court judgments', color: '#8b5cf6' },
];

const LANGUAGES = [
  { code: 'en', label: 'English', flag: '🇬🇧', native: 'English' },
  { code: 'hi', label: 'Hindi', flag: '🇮🇳', native: 'हिंदी' },
  { code: 'ta', label: 'Tamil', flag: '🏳️', native: 'தமிழ்' },
  { code: 'te', label: 'Telugu', flag: '🏳️', native: 'తెలుగు' },
  { code: 'bn', label: 'Bengali', flag: '🏳️', native: 'বাংলা' },
  { code: 'mr', label: 'Marathi', flag: '🏳️', native: 'मराठी' },
  { code: 'gu', label: 'Gujarati', flag: '🏳️', native: 'ગુજરાતી' },
  { code: 'kn', label: 'Kannada', flag: '🏳️', native: 'ಕನ್ನಡ' },
  { code: 'ml', label: 'Malayalam', flag: '🏳️', native: 'മലയാളം' },
];

const SLASH_COMMANDS = [
  { cmd: '/help', desc: 'Show all commands', icon: '📖' },
  { cmd: '/fir', desc: 'FIR filing guide', icon: '📋' },
  { cmd: '/rights', desc: 'Your legal rights', icon: '⚖️' },
  { cmd: '/cyber', desc: 'Cybercrime guidance', icon: '🛡️' },
  { cmd: '/bail', desc: 'Bail types & process', icon: '🏛️' },
  { cmd: '/laws', desc: 'IPC/BNS quick reference', icon: '📚' },
  { cmd: '/sections <crime>', desc: 'Sections for a crime', icon: '🔍', hasArg: true },
  { cmd: '/landmark <crime>', desc: 'Court judgments', icon: '🏅', hasArg: true },
  { cmd: '/drugs', desc: 'NDPS Act guide', icon: '💊' },
  { cmd: '/murder', desc: 'Murder law', icon: '🔴' },
  { cmd: '/dv', desc: 'Domestic violence', icon: '🏠' },
  { cmd: '/pocso', desc: 'Child protection laws', icon: '👶' },
  { cmd: '/rti', desc: 'Right to Information', icon: '📜' },
  { cmd: '/wc', desc: 'White-collar crime', icon: '💼' },
  { cmd: '/missing', desc: 'Missing person guide', icon: '🔎' },
  { cmd: '/evidence', desc: 'Evidence collection', icon: '🧪' },
  { cmd: '/helplines', desc: 'All helpline numbers', icon: '📞' },
  { cmd: '/contacts', desc: 'Complaint portals', icon: '📬' },
  { cmd: '/translate <lang>', desc: 'Switch language (hi/ta/te...)', icon: '🌐', hasArg: true },
];

const QUICK_QUESTIONS = [
  { text: 'How to file an FIR?', cmd: '/fir' },
  { text: 'What are my legal rights?', cmd: '/rights' },
  { text: 'Report cybercrime', cmd: '/cyber' },
  { text: 'Bail process & types', cmd: '/bail' },
  { text: 'All helpline numbers', cmd: '/helplines' },
  { text: 'NDPS & drug offences', cmd: '/drugs' },
  { text: 'Domestic violence laws', cmd: '/dv' },
  { text: 'POCSO — child safety', cmd: '/pocso' },
  { text: 'File RTI for my case', cmd: '/rti' },
  { text: 'White-collar crime', cmd: '/wc' },
];

// ─── Markdown renderer (lightweight) ─────────────────────────────────────────

function renderMarkdown(text) {
  if (!text) return '';

  const lines = text.split('\n');
  const result = [];
  let inTable = false;
  let tableRows = [];
  let i = 0;

  const flushTable = () => {
    if (tableRows.length > 0) {
      result.push(
        <div key={`table-${i}`} className="overflow-x-auto my-3">
          <table className="min-w-full text-xs border-collapse">
            <tbody>
              {tableRows.map((row, ri) => {
                const cells = row.split('|').filter((_, ci) => ci > 0 && ci < row.split('|').length - 1);
                const isHeader = ri === 0;
                return (
                  <tr key={ri} className={isHeader ? 'border-b border-primary/30' : 'border-b border-border/30 hover:bg-surface-3/20'}>
                    {cells.map((cell, ci) => isHeader ? (
                      <th key={ci} className="px-3 py-1.5 text-left font-semibold text-primary-light">{cell.trim()}</th>
                    ) : (
                      <td key={ci} className="px-3 py-1.5 text-text-secondary">{cell.trim()}</td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      );
      tableRows = [];
      inTable = false;
    }
  };

  while (i < lines.length) {
    const line = lines[i];

    // Table detection
    if (line.includes('|') && line.trim().startsWith('|')) {
      if (!inTable) inTable = true;
      // Skip separator rows
      if (!line.match(/^\|[\s\-:|]+\|/)) {
        tableRows.push(line);
      }
      i++;
      continue;
    } else if (inTable) {
      flushTable();
    }

    // Headings
    if (line.startsWith('### ')) {
      result.push(<h4 key={i} className="font-semibold text-sm text-text mt-3 mb-1">{renderInline(line.slice(4))}</h4>);
    } else if (line.startsWith('## ')) {
      result.push(<h3 key={i} className="font-bold text-sm text-primary-light mt-3 mb-1">{renderInline(line.slice(3))}</h3>);
    } else if (line.startsWith('# ')) {
      result.push(<h2 key={i} className="font-bold text-base gradient-text mt-2 mb-2">{renderInline(line.slice(2))}</h2>);
    }
    // Bullet points
    else if (line.match(/^[-*] /)) {
      result.push(
        <div key={i} className="flex gap-2 text-sm text-text-secondary leading-relaxed">
          <span className="text-primary mt-0.5 flex-shrink-0">•</span>
          <span>{renderInline(line.slice(2))}</span>
        </div>
      );
    }
    // Numbered list
    else if (line.match(/^\d+\. /)) {
      const match = line.match(/^(\d+)\. (.*)/);
      result.push(
        <div key={i} className="flex gap-2 text-sm text-text-secondary leading-relaxed">
          <span className="text-accent font-semibold flex-shrink-0 min-w-[1.5rem]">{match[1]}.</span>
          <span>{renderInline(match[2])}</span>
        </div>
      );
    }
    // Empty line
    else if (line.trim() === '') {
      result.push(<div key={i} className="h-1.5" />);
    }
    // Regular paragraph
    else {
      result.push(<p key={i} className="text-sm text-text-secondary leading-relaxed">{renderInline(line)}</p>);
    }

    i++;
  }

  // Flush any remaining table
  flushTable();

  return result;
}

function renderInline(text) {
  // Bold **text**
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i} className="font-semibold text-text">{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith('*') && part.endsWith('*')) {
      return <em key={i} className="italic text-text-secondary">{part.slice(1, -1)}</em>;
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return <code key={i} className="px-1.5 py-0.5 bg-surface-3/60 text-accent text-xs rounded font-mono">{part.slice(1, -1)}</code>;
    }
    return part;
  });
}

// ─── Message component ────────────────────────────────────────────────────────

function Message({ msg, user }) {
  const [copied, setCopied] = useState(false);
  const isUser = msg.role === 'user';

  const copyText = () => {
    navigator.clipboard.writeText(msg.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`flex gap-3 animate-fadeIn group ${isUser ? 'justify-end' : ''}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center flex-shrink-0 shadow-lg">
          <Bot className="w-4 h-4 text-white" />
        </div>
      )}

      <div className={`max-w-[85%] flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={`relative rounded-2xl px-4 py-3 shadow-sm ${
          isUser
            ? 'bg-gradient-to-br from-primary to-primary-dark text-white rounded-br-sm'
            : 'bg-surface-2/80 border border-border/60 rounded-bl-sm backdrop-blur-sm'
        }`}>
          {isUser ? (
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
          ) : (
            <div className="space-y-0.5">
              {renderMarkdown(msg.content)}
            </div>
          )}

          {/* Copy button for assistant */}
          {!isUser && (
            <button
              onClick={copyText}
              className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-md hover:bg-surface-3/50"
            >
              {copied ? <Check className="w-3 h-3 text-success" /> : <Copy className="w-3 h-3 text-text-muted" />}
            </button>
          )}
        </div>

        <span className={`text-[10px] mt-1.5 px-1 ${isUser ? 'text-text-muted' : 'text-text-muted'}`}>
          {msg.time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          {msg.lang && msg.lang !== 'en' && <span className="ml-1 opacity-60">• {LANGUAGES.find(l => l.code === msg.lang)?.flag}</span>}
        </span>
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-xl bg-surface-3 flex items-center justify-center flex-shrink-0 text-sm font-bold text-primary-light shadow-sm">
          {user?.full_name?.charAt(0)?.toUpperCase()}
        </div>
      )}
    </div>
  );
}

// ─── Slash Command Palette ────────────────────────────────────────────────────

function CommandPalette({ input, onSelect, onClose }) {
  const query = input.slice(1).toLowerCase();
  const filtered = SLASH_COMMANDS.filter(c =>
    c.cmd.toLowerCase().includes('/' + query) || c.desc.toLowerCase().includes(query)
  );

  if (!input.startsWith('/') || filtered.length === 0) return null;

  return (
    <div className="absolute bottom-full left-0 right-0 mb-2 bg-surface-2 border border-primary/20 rounded-xl shadow-2xl overflow-hidden z-50 max-h-64 overflow-y-auto">
      <div className="flex items-center gap-2 px-3 py-2 border-b border-border/50 bg-surface/50">
        <Command className="w-3 h-3 text-primary" />
        <span className="text-xs font-medium text-text-muted">Slash Commands</span>
        <button onClick={onClose} className="ml-auto text-text-muted hover:text-text">
          <X className="w-3 h-3" />
        </button>
      </div>
      {filtered.map((c, i) => (
        <button
          key={i}
          onClick={() => onSelect(c.hasArg ? c.cmd.split(' ')[0] + ' ' : c.cmd)}
          className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-primary/10 text-left transition-colors border-b border-border/20 last:border-0"
        >
          <span className="text-lg leading-none w-6 flex-shrink-0">{c.icon}</span>
          <div className="flex-1 min-w-0">
            <code className="text-xs font-mono text-primary-light">{c.cmd}</code>
            <p className="text-[11px] text-text-muted mt-0.5">{c.desc}</p>
          </div>
        </button>
      ))}
    </div>
  );
}

// ─── Language Selector ────────────────────────────────────────────────────────

function LanguageSelector({ selected, onChange }) {
  const [open, setOpen] = useState(false);
  const current = LANGUAGES.find(l => l.code === selected) || LANGUAGES[0];

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-3/50 border border-border hover:border-primary/40 transition-all text-xs"
      >
        <Globe className="w-3.5 h-3.5 text-text-muted" />
        <span className="font-medium">{current.flag} {current.native}</span>
        <ChevronDown className={`w-3 h-3 text-text-muted transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-1.5 bg-surface-2 border border-border rounded-xl shadow-2xl z-50 min-w-[160px] overflow-hidden">
          {LANGUAGES.map(lang => (
            <button
              key={lang.code}
              onClick={() => { onChange(lang.code); setOpen(false); }}
              className={`w-full flex items-center gap-2.5 px-3 py-2 text-left text-xs transition-colors hover:bg-primary/10 ${selected === lang.code ? 'bg-primary/15 text-primary-light' : 'text-text-secondary'}`}
            >
              <span className="text-base">{lang.flag}</span>
              <div>
                <p className="font-medium">{lang.native}</p>
                <p className="text-[10px] text-text-muted">{lang.label}</p>
              </div>
              {selected === lang.code && <Check className="w-3 h-3 ml-auto text-primary" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Main ChatPage ────────────────────────────────────────────────────────────

export default function ChatPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [context, setContext] = useState('general');
  const [language, setLanguage] = useState('en');
  const [loading, setLoading] = useState(false);
  const [showCmdPalette, setShowCmdPalette] = useState(false);
  const [showLangDropdown, setShowLangDropdown] = useState(false);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  // Show command palette when typing /
  useEffect(() => {
    setShowCmdPalette(input.startsWith('/') && input.length > 0);
  }, [input]);

  const handleLanguageChange = (lang) => {
    setLanguage(lang);
    const langInfo = LANGUAGES.find(l => l.code === lang);
    if (lang !== 'en') {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `✅ Language switched to **${langInfo.native} (${langInfo.label})**.\n\nYou can now ask questions in ${langInfo.label} or use slash commands like \`/fir\`, \`/rights\`, \`/cyber\` to get responses in ${langInfo.label}.\n\n💡 *Tip: Type \`/translate en\` to switch back to English.*`,
        time: new Date(),
        lang,
      }]);
    }
  };

  const sendMessage = async (text) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;
    setInput('');
    setShowCmdPalette(false);
    setMessages(p => [...p, { role: 'user', content: msg, time: new Date(), lang: language }]);
    setLoading(true);
    try {
      const res = await chatAPI.send({ message: msg, context, language });
      setMessages(p => [...p, { role: 'assistant', content: res.data.response, time: new Date(), lang: language }]);
    } catch {
      setMessages(p => [...p, { role: 'assistant', content: '❌ Sorry, I encountered an error. Please try again.', time: new Date() }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage();
  };

  const handleCommandSelect = (cmd) => {
    setInput(cmd);
    setShowCmdPalette(false);
    inputRef.current?.focus();
  };

  const clearChat = () => {
    setMessages([]);
  };

  const currentLang = LANGUAGES.find(l => l.code === language) || LANGUAGES[0];
  const currentCtx = CONTEXTS.find(c => c.key === context) || CONTEXTS[0];

  return (
    <div className="flex gap-4 h-[calc(100vh-8rem)] animate-fadeIn">

      {/* ── Left Sidebar ─────────────────────────────────────────────────── */}
      <div className="w-64 flex-shrink-0 space-y-3 hidden lg:flex lg:flex-col overflow-y-auto">

        {/* Context Selector */}
        <div className="glass-card p-4">
          <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3 flex items-center gap-2">
            <Sparkles className="w-3.5 h-3.5 text-accent" /> AI Context
          </h3>
          <div className="space-y-1.5">
            {CONTEXTS.map(c => (
              <button key={c.key} onClick={() => setContext(c.key)}
                className={`w-full flex items-center gap-2.5 p-2.5 rounded-xl text-left transition-all ${context === c.key ? 'bg-primary/15 border border-primary/20' : 'text-text-secondary hover:bg-surface-3/40'}`}
              >
                <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ backgroundColor: c.color + '20' }}>
                  <c.icon className="w-3.5 h-3.5" style={{ color: c.color }} />
                </div>
                <div className="min-w-0">
                  <p className={`text-xs font-medium truncate ${context === c.key ? 'text-primary-light' : ''}`}>{c.label}</p>
                  <p className="text-[10px] text-text-muted truncate">{c.desc}</p>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Language Selector */}
        <div className="glass-card p-4">
          <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3 flex items-center gap-2">
            <Globe className="w-3.5 h-3.5 text-accent" /> Language
          </h3>
          <div className="grid grid-cols-1 gap-1">
            {LANGUAGES.map(lang => (
              <button key={lang.code} onClick={() => handleLanguageChange(lang.code)}
                className={`flex items-center gap-2 px-2.5 py-2 rounded-lg text-left text-xs transition-all ${language === lang.code ? 'bg-accent/15 border border-accent/20 text-accent-light' : 'text-text-secondary hover:bg-surface-3/40'}`}
              >
                <span className="text-sm">{lang.flag}</span>
                <span className="font-medium">{lang.native}</span>
                {language === lang.code && <Check className="w-3 h-3 ml-auto text-accent" />}
              </button>
            ))}
          </div>
        </div>

        {/* Quick Commands */}
        <div className="glass-card p-4">
          <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3 flex items-center gap-2">
            <Hash className="w-3.5 h-3.5 text-accent" /> Quick Commands
          </h3>
          <div className="space-y-1">
            {QUICK_QUESTIONS.map((q, i) => (
              <button key={i} onClick={() => sendMessage(q.cmd)}
                className="w-full text-left text-[11px] p-2 rounded-lg text-text-secondary hover:text-text hover:bg-surface-3/40 transition-colors flex items-center gap-2 group">
                <Zap className="w-3 h-3 text-accent/60 group-hover:text-accent flex-shrink-0" />
                {q.text}
              </button>
            ))}
          </div>
        </div>

      </div>

      {/* ── Main Chat Area ────────────────────────────────────────────────── */}
      <div className="flex-1 glass-card flex flex-col overflow-hidden min-w-0">

        {/* Header */}
        <div className="p-3 border-b border-border flex items-center gap-3 flex-shrink-0 flex-wrap gap-y-2">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg">
            <Bot className="w-4.5 h-4.5 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-sm">CrimeGPT Assistant</h2>
            <div className="flex items-center gap-2 text-[10px] text-text-muted">
              <span className="capitalize" style={{ color: currentCtx.color }}>
                {currentCtx.label}
              </span>
              <span>•</span>
              <span>{currentLang.flag} {currentLang.native}</span>
            </div>
          </div>

          <div className="ml-auto flex items-center gap-2">
            {/* Status indicator */}
            <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-success/10 border border-success/20">
              <div className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
              <span className="text-[10px] text-success">Online</span>
            </div>

            {/* Clear chat */}
            {messages.length > 0 && (
              <button onClick={clearChat}
                className="p-1.5 rounded-lg text-text-muted hover:text-text hover:bg-surface-3/50 transition-colors"
                title="Clear chat">
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>

        {/* Context tabs — mobile */}
        <div className="px-3 pt-2 pb-0 flex gap-1.5 overflow-x-auto lg:hidden border-b border-border/50 pb-2">
          {CONTEXTS.map(c => (
            <button key={c.key} onClick={() => setContext(c.key)}
              className={`flex-shrink-0 flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[11px] font-medium transition-all ${context === c.key ? 'bg-primary/20 text-primary-light border border-primary/20' : 'bg-surface-3/30 text-text-muted hover:text-text'}`}
            >
              <c.icon className="w-3 h-3" />
              {c.label}
            </button>
          ))}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center mb-4 animate-float shadow-lg">
                <Bot className="w-10 h-10 text-primary-light" />
              </div>
              <h3 className="text-lg font-bold mb-2 gradient-text">How can I help you?</h3>
              <p className="text-sm text-text-muted max-w-md mb-6">
                Ask me anything about filing complaints, legal rights, investigation procedures, or cybercrime prevention.
              </p>

              {/* Command hints */}
              <div className="grid grid-cols-2 gap-2 max-w-sm w-full">
                {[
                  { cmd: '/fir', label: 'File an FIR', icon: '📋', color: '#6366f1' },
                  { cmd: '/rights', label: 'Legal Rights', icon: '⚖️', color: '#ec4899' },
                  { cmd: '/cyber', label: 'Cybercrime', icon: '🛡️', color: '#06b6d4' },
                  { cmd: '/helplines', label: 'Helplines', icon: '📞', color: '#10b981' },
                ].map(item => (
                  <button key={item.cmd} onClick={() => sendMessage(item.cmd)}
                    className="flex items-center gap-2.5 p-3 rounded-xl bg-surface-2/60 border border-border/60 hover:border-primary/30 hover:bg-surface-3/40 transition-all text-left group">
                    <span className="text-xl">{item.icon}</span>
                    <div>
                      <p className="text-xs font-medium text-text">{item.label}</p>
                      <code className="text-[10px] text-text-muted font-mono">{item.cmd}</code>
                    </div>
                  </button>
                ))}
              </div>

              <p className="text-[11px] text-text-muted mt-5">
                💡 Type <code className="px-1 py-0.5 bg-surface-3/60 rounded text-accent font-mono">/help</code> to see all slash commands
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <Message key={i} msg={msg} user={user} />
          ))}

          {/* Loading indicator */}
          {loading && (
            <div className="flex gap-3 animate-fadeIn">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center flex-shrink-0 shadow-lg">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-surface-2/80 border border-border/60 rounded-2xl rounded-bl-sm px-4 py-3">
                <div className="flex gap-1.5 items-center">
                  <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0s' }} />
                  <div className="w-2 h-2 rounded-full bg-primary/70 animate-bounce" style={{ animationDelay: '0.15s' }} />
                  <div className="w-2 h-2 rounded-full bg-primary/40 animate-bounce" style={{ animationDelay: '0.3s' }} />
                  <span className="text-xs text-text-muted ml-2">AI is thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input Area */}
        <div className="p-3 border-t border-border flex-shrink-0">
          {/* Mobile language bar */}
          <div className="flex items-center gap-2 mb-2 lg:hidden">
            <Globe className="w-3.5 h-3.5 text-text-muted" />
            <div className="flex gap-1 overflow-x-auto">
              {LANGUAGES.slice(0, 5).map(lang => (
                <button key={lang.code} onClick={() => handleLanguageChange(lang.code)}
                  className={`flex-shrink-0 px-2 py-0.5 rounded-full text-[10px] border transition-all ${language === lang.code ? 'bg-accent/20 border-accent/40 text-accent-light' : 'border-border/50 text-text-muted hover:text-text'}`}>
                  {lang.flag} {lang.code.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="relative flex gap-2">
            {/* Command palette */}
            <div className="relative flex-1">
              <CommandPalette
                input={input}
                onSelect={handleCommandSelect}
                onClose={() => setShowCmdPalette(false)}
              />
              <div className="relative">
                {input.startsWith('/') && (
                  <div className="absolute left-3 top-1/2 -translate-y-1/2 z-10">
                    <Command className="w-4 h-4 text-primary" />
                  </div>
                )}
                <input
                  ref={inputRef}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === 'Escape' && setShowCmdPalette(false)}
                  placeholder={`Ask anything or type / for commands... ${currentLang.flag}`}
                  className={`input-field w-full pr-4 ${input.startsWith('/') ? 'pl-10 border-primary/40' : ''}`}
                  disabled={loading}
                />
              </div>
            </div>

            <button type="submit" disabled={loading || !input.trim()} className="btn-primary px-4 flex-shrink-0">
              <Send className="w-4 h-4" />
            </button>
          </form>

          <p className="text-[10px] text-text-muted mt-2 text-center">
            <MessageSquare className="w-3 h-3 inline mr-1" />
            CrimeGPT provides legal guidance only — not a substitute for professional legal advice.
          </p>
        </div>
      </div>
    </div>
  );
}
