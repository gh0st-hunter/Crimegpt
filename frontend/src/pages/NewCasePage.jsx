import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { casesAPI } from '../api';
import { Sparkles, FileText, Send, AlertCircle, Wand2, ArrowRight } from 'lucide-react';

const categories = [
  { value: 'cybercrime', label: '💻 Cybercrime' }, { value: 'theft', label: '🔓 Theft' },
  { value: 'fraud', label: '💰 Fraud' }, { value: 'assault', label: '👊 Assault' },
  { value: 'domestic_violence', label: '🏠 Domestic Violence' },
  { value: 'sexual_harassment', label: '⚠️ Sexual Harassment' },
  { value: 'murder', label: '🔴 Murder' }, { value: 'kidnapping', label: '🚨 Kidnapping' },
  { value: 'drug_offense', label: '💊 Drug Offense' }, { value: 'property_crime', label: '🏘️ Property Crime' },
  { value: 'white_collar', label: '🏢 White Collar' }, { value: 'other', label: '📋 Other' },
];

export default function NewCasePage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState('ai'); // 'ai' or 'manual'
  const [complaint, setComplaint] = useState('');
  const [form, setForm] = useState({ title: '', description: '', category: 'cybercrime', incident_location: '', incident_date: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAISubmit = async (e) => {
    e.preventDefault(); setError(''); setLoading(true);
    try {
      const res = await casesAPI.fromComplaint({ complaint_text: complaint, category: form.category || null });
      navigate(`/cases/${res.data.id}`);
    } catch (err) { setError(err.response?.data?.detail || 'Failed to create case'); }
    finally { setLoading(false); }
  };

  const handleManualSubmit = async (e) => {
    e.preventDefault(); setError(''); setLoading(true);
    try {
      const payload = { ...form };
      if (payload.incident_date) payload.incident_date = new Date(payload.incident_date).toISOString();
      else delete payload.incident_date;
      const res = await casesAPI.create(payload);
      navigate(`/cases/${res.data.id}`);
    } catch (err) { setError(err.response?.data?.detail || 'Failed'); }
    finally { setLoading(false); }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fadeIn">
      <div>
        <h1 className="text-2xl font-bold">File New Case</h1>
        <p className="text-text-secondary">Submit a complaint or create a case manually</p>
      </div>

      {/* Mode Toggle */}
      <div className="flex gap-2 p-1 bg-surface-2 rounded-xl border border-border">
        {[
          { key: 'ai', icon: Sparkles, label: 'AI-Powered FIR', desc: 'Describe your complaint naturally' },
          { key: 'manual', icon: FileText, label: 'Manual Entry', desc: 'Fill in case details' },
        ].map(m => (
          <button key={m.key} onClick={() => setMode(m.key)}
            className={`flex-1 flex items-center gap-3 p-4 rounded-xl transition-all ${mode === m.key ? 'bg-primary/15 border border-primary/30' : 'hover:bg-surface-3/50'}`}>
            <m.icon className={`w-5 h-5 ${mode === m.key ? 'text-primary-light' : 'text-text-muted'}`} />
            <div className="text-left">
              <p className={`text-sm font-medium ${mode === m.key ? 'text-primary-light' : ''}`}>{m.label}</p>
              <p className="text-xs text-text-muted">{m.desc}</p>
            </div>
          </button>
        ))}
      </div>

      {error && <div className="p-3 rounded-xl bg-danger/10 border border-danger/20 flex items-center gap-2 text-danger text-sm"><AlertCircle className="w-4 h-4" /> {error}</div>}

      {/* AI Mode */}
      {mode === 'ai' ? (
        <form onSubmit={handleAISubmit} className="glass-card p-6 space-y-5">
          <div className="flex items-center gap-2 text-sm text-accent">
            <Wand2 className="w-4 h-4" />
            <span>AI will automatically generate FIR, identify legal sections, and recommend investigation steps</span>
          </div>
          <div>
            <label className="text-sm font-medium text-text-secondary mb-1.5 block">Crime Category</label>
            <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
              {categories.map(c => (
                <button key={c.value} type="button" onClick={() => setForm(p => ({ ...p, category: c.value }))}
                  className={`p-2 rounded-lg text-xs font-medium transition-all text-center ${form.category === c.value ? 'bg-primary/20 border border-primary/40 text-primary-light' : 'bg-surface border border-border text-text-secondary hover:border-primary/20'}`}>
                  {c.label}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-text-secondary mb-1.5 block">Describe Your Complaint</label>
            <textarea value={complaint} onChange={e => setComplaint(e.target.value)}
              placeholder="Describe what happened in detail. Include dates, locations, people involved, and any evidence you have. The AI will generate a structured FIR from your description..."
              className="input-field min-h-[200px] resize-y" required minLength={20} />
            <p className="text-xs text-text-muted mt-1">{complaint.length} characters (minimum 20)</p>
          </div>
          <button type="submit" disabled={loading || complaint.length < 20} className="btn-primary w-full justify-center">
            {loading ? <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" /> : <><Sparkles className="w-4 h-4" /> Generate FIR with AI</>}
          </button>
        </form>
      ) : (
        <form onSubmit={handleManualSubmit} className="glass-card p-6 space-y-5">
          <div>
            <label className="text-sm font-medium text-text-secondary mb-1.5 block">Case Title</label>
            <input value={form.title} onChange={e => setForm(p => ({ ...p, title: e.target.value }))} placeholder="Brief title" className="input-field" required minLength={5} />
          </div>
          <div>
            <label className="text-sm font-medium text-text-secondary mb-1.5 block">Category</label>
            <select value={form.category} onChange={e => setForm(p => ({ ...p, category: e.target.value }))} className="input-field">
              {categories.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
            </select>
          </div>
          <div>
            <label className="text-sm font-medium text-text-secondary mb-1.5 block">Description</label>
            <textarea value={form.description} onChange={e => setForm(p => ({ ...p, description: e.target.value }))}
              placeholder="Detailed description..." className="input-field min-h-[150px] resize-y" required minLength={20} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-text-secondary mb-1.5 block">Incident Location</label>
              <input value={form.incident_location} onChange={e => setForm(p => ({ ...p, incident_location: e.target.value }))} placeholder="Location" className="input-field" />
            </div>
            <div>
              <label className="text-sm font-medium text-text-secondary mb-1.5 block">Incident Date</label>
              <input type="datetime-local" value={form.incident_date} onChange={e => setForm(p => ({ ...p, incident_date: e.target.value }))} className="input-field" />
            </div>
          </div>
          <button type="submit" disabled={loading} className="btn-primary w-full justify-center">
            {loading ? <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" /> : <><Send className="w-4 h-4" /> Submit Case</>}
          </button>
        </form>
      )}
    </div>
  );
}
