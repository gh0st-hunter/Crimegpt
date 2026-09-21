import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { casesAPI, datasetAPI } from '../api';
import {
  FileText, Clock, CheckCircle, AlertTriangle, ArrowUpRight,
  TrendingUp, Shield, Activity, Zap, BarChart3, Database, Loader, BookOpen, Scale
} from 'lucide-react';

const priorityColors = { critical: 'badge-critical', high: 'badge-high', medium: 'badge-medium', low: 'badge-low' };
const statusColors = { draft: 'status-draft', filed: 'status-filed', under_investigation: 'status-under_investigation', closed: 'status-closed' };

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [seedMsg, setSeedMsg] = useState('');

  useEffect(() => {
    casesAPI.getStats().then(res => setStats(res.data)).catch(() => {
      setStats({ total_firs: 0, pending_cases: 0, closed_cases: 0, critical_cases: 0, high_priority: 0,
        medium_priority: 0, low_priority: 0, categories: {}, monthly_trend: [], status_distribution: {},
        recent_cases: [], pending_reminders: 0 });
    }).finally(() => setLoading(false));
  }, []);

  const handleSeedData = async () => {
    setSeeding(true);
    setSeedMsg('');
    try {
      const res = await datasetAPI.seed();
      setSeedMsg(`✅ ${res.data.message}`);
      // Refresh stats
      const statsRes = await casesAPI.getStats();
      setStats(statsRes.data);
    } catch (e) {
      setSeedMsg(`❌ ${e.response?.data?.detail || 'Seeding failed. Only officers/admins can seed data.'}`);
    } finally {
      setSeeding(false);
    }
  };

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" /></div>;

  const statCards = [
    { label: 'Total FIRs', value: stats.total_firs, icon: FileText, color: 'from-primary to-primary-dark', bg: 'bg-primary/10' },
    { label: 'Pending Cases', value: stats.pending_cases, icon: Clock, color: 'from-warning to-yellow-600', bg: 'bg-warning/10' },
    { label: 'Closed Cases', value: stats.closed_cases, icon: CheckCircle, color: 'from-success to-emerald-600', bg: 'bg-success/10' },
    { label: 'Critical Cases', value: stats.critical_cases, icon: AlertTriangle, color: 'from-danger to-red-700', bg: 'bg-danger/10' },
  ];

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Welcome */}
      <div className="glass-card p-6 relative overflow-hidden">
        <div className="absolute right-0 top-0 w-64 h-64 bg-gradient-to-bl from-primary/10 to-transparent rounded-full -translate-y-1/2 translate-x-1/4" />
        <div className="relative">
          <h1 className="text-2xl font-bold mb-1">Welcome back, <span className="gradient-text">{user?.full_name}</span></h1>
          <p className="text-text-secondary">
            {user?.role === 'officer' ? 'Manage your cases and investigations efficiently with AI assistance.' : 'Track your complaints and get AI-powered legal guidance.'}
          </p>
          <div className="flex gap-3 mt-4 flex-wrap">
            <Link to="/cases/new" className="btn-primary"><Zap className="w-4 h-4" /> New Case</Link>
            <Link to="/chat" className="btn-secondary"><Shield className="w-4 h-4" /> AI Assistant</Link>
            <Link to="/documents" className="btn-secondary"><BookOpen className="w-4 h-4" /> Documents</Link>
            <Link to="/legal-sections" className="btn-secondary"><Scale className="w-4 h-4" /> Legal Sections</Link>
            {user?.role !== 'victim' && (
              <button onClick={handleSeedData} disabled={seeding} className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border border-border bg-surface-2 text-text-secondary hover:text-text hover:bg-surface-3 transition-all">
                {seeding ? <Loader className="w-4 h-4 animate-spin" /> : <Database className="w-4 h-4" />}
                {seeding ? 'Loading...' : 'Load Demo Data'}
              </button>
            )}
          </div>
          {seedMsg && <p className="mt-3 text-sm text-text-secondary">{seedMsg}</p>}
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((s, i) => (
          <div key={i} className="glass-card p-5 group" style={{ animationDelay: `${i * 100}ms` }}>
            <div className="flex items-center justify-between mb-3">
              <div className={`w-10 h-10 rounded-xl ${s.bg} flex items-center justify-center`}>
                <s.icon className={`w-5 h-5 bg-gradient-to-r ${s.color} bg-clip-text`} style={{ color: s.color.includes('primary') ? '#818cf8' : s.color.includes('warning') ? '#fbbf24' : s.color.includes('success') ? '#34d399' : '#f87171' }} />
              </div>
              <ArrowUpRight className="w-4 h-4 text-text-muted group-hover:text-primary transition-colors" />
            </div>
            <p className="text-3xl font-bold">{s.value}</p>
            <p className="text-sm text-text-secondary mt-1">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Priority Distribution & Recent Cases */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Priority */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2"><Activity className="w-5 h-5 text-primary" /> Priority Distribution</h3>
          <div className="space-y-3">
            {[
              { label: 'Critical', count: stats.critical_cases, color: 'bg-critical', total: stats.total_firs },
              { label: 'High', count: stats.high_priority, color: 'bg-high', total: stats.total_firs },
              { label: 'Medium', count: stats.medium_priority, color: 'bg-medium', total: stats.total_firs },
              { label: 'Low', count: stats.low_priority, color: 'bg-low', total: stats.total_firs },
            ].map((p, i) => (
              <div key={i}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-text-secondary">{p.label}</span>
                  <span className="font-medium">{p.count}</span>
                </div>
                <div className="w-full h-2 bg-surface rounded-full overflow-hidden">
                  <div className={`h-full ${p.color} rounded-full transition-all duration-1000`}
                    style={{ width: `${p.total ? (p.count / p.total) * 100 : 0}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Cases */}
        <div className="glass-card p-6 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold flex items-center gap-2"><TrendingUp className="w-5 h-5 text-accent" /> Recent Cases</h3>
            <Link to="/cases" className="text-sm text-primary-light hover:underline">View All</Link>
          </div>
          {stats.recent_cases.length === 0 ? (
            <div className="text-center py-8 text-text-muted">
              <FileText className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>No cases yet. Create your first case!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {stats.recent_cases.map((c, i) => (
                <Link key={c.id} to={`/cases/${c.id}`}
                  className="flex items-center gap-4 p-3 rounded-xl hover:bg-surface-3/50 transition-all group">
                  <div className={`w-2 h-2 rounded-full ${c.priority === 'critical' ? 'bg-critical' : c.priority === 'high' ? 'bg-high' : c.priority === 'medium' ? 'bg-medium' : 'bg-low'}`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate group-hover:text-primary-light transition-colors">{c.title}</p>
                    <p className="text-xs text-text-muted">{c.fir_number || 'No FIR'} · {c.category.replace('_', ' ')}</p>
                  </div>
                  <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${statusColors[c.status] || 'status-draft'}`}>
                    {c.status.replace('_', ' ')}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Categories */}
      {Object.keys(stats.categories).length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2"><BarChart3 className="w-5 h-5 text-primary" /> Crime Categories</h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {Object.entries(stats.categories).map(([cat, count]) => (
              <div key={cat} className="text-center p-3 rounded-xl bg-surface/50 hover:bg-primary/5 transition-colors border border-border/50">
                <p className="text-2xl font-bold gradient-text">{count}</p>
                <p className="text-xs text-text-muted mt-1 capitalize">{cat.replace('_', ' ')}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
