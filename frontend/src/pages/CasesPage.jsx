import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { casesAPI } from '../api';
import { Search, Filter, PlusCircle, FileText, ChevronRight } from 'lucide-react';

const priorities = ['', 'critical', 'high', 'medium', 'low'];
const statuses = ['', 'draft', 'filed', 'under_investigation', 'evidence_collection', 'closed'];
const categories = ['', 'cybercrime', 'theft', 'fraud', 'assault', 'domestic_violence', 'murder', 'kidnapping', 'other'];

const priorityBadge = { critical: 'badge-critical', high: 'badge-high', medium: 'badge-medium', low: 'badge-low' };
const statusBadge = { draft: 'status-draft', filed: 'status-filed', under_investigation: 'status-under_investigation', closed: 'status-closed' };

export default function CasesPage() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ search: '', priority: '', status: '', category: '' });

  const loadCases = () => {
    setLoading(true);
    const params = {};
    if (filters.search) params.search = filters.search;
    if (filters.priority) params.priority = filters.priority;
    if (filters.status) params.status = filters.status;
    if (filters.category) params.category = filters.category;
    casesAPI.list(params).then(r => setCases(r.data)).catch(() => setCases([])).finally(() => setLoading(false));
  };

  useEffect(() => { loadCases(); }, [filters.priority, filters.status, filters.category]);

  const handleSearch = (e) => {
    e.preventDefault();
    loadCases();
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Cases</h1>
          <p className="text-text-secondary">Manage and track all cases</p>
        </div>
        <Link to="/cases/new" className="btn-primary"><PlusCircle className="w-4 h-4" /> New Case</Link>
      </div>

      {/* Filters */}
      <div className="glass-card p-4">
        <div className="flex flex-wrap gap-3">
          <form onSubmit={handleSearch} className="flex-1 min-w-[200px] relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
            <input value={filters.search} onChange={e => setFilters(p => ({ ...p, search: e.target.value }))}
              placeholder="Search by title or FIR number..." className="input-field pl-10" />
          </form>
          {[
            { key: 'priority', opts: priorities, label: 'Priority' },
            { key: 'status', opts: statuses, label: 'Status' },
            { key: 'category', opts: categories, label: 'Category' },
          ].map(f => (
            <select key={f.key} value={filters[f.key]} onChange={e => setFilters(p => ({ ...p, [f.key]: e.target.value }))}
              className="input-field w-auto min-w-[140px]">
              <option value="">All {f.label}</option>
              {f.opts.filter(Boolean).map(o => <option key={o} value={o}>{o.replace('_', ' ')}</option>)}
            </select>
          ))}
        </div>
      </div>

      {/* Case List */}
      {loading ? (
        <div className="flex justify-center py-12"><div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" /></div>
      ) : cases.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <FileText className="w-16 h-16 mx-auto mb-4 text-text-muted opacity-30" />
          <h3 className="text-xl font-semibold mb-2">No Cases Found</h3>
          <p className="text-text-secondary mb-4">Create your first case to get started</p>
          <Link to="/cases/new" className="btn-primary inline-flex"><PlusCircle className="w-4 h-4" /> Create Case</Link>
        </div>
      ) : (
        <div className="space-y-3">
          {cases.map((c, i) => (
            <Link key={c.id} to={`/cases/${c.id}`}
              className="glass-card p-4 flex items-center gap-4 group cursor-pointer"
              style={{ animationDelay: `${i * 50}ms` }}>
              <div className={`w-3 h-3 rounded-full flex-shrink-0 ${c.priority === 'critical' ? 'bg-critical animate-pulse' : c.priority === 'high' ? 'bg-high' : c.priority === 'medium' ? 'bg-medium' : 'bg-low'}`} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-medium truncate group-hover:text-primary-light transition-colors">{c.title}</h3>
                  {c.fir_number && <span className="text-xs px-2 py-0.5 bg-primary/10 text-primary-light rounded-full">{c.fir_number}</span>}
                </div>
                <div className="flex items-center gap-3 text-xs text-text-muted">
                  <span className="capitalize">{c.category?.replace('_', ' ')}</span>
                  <span>•</span>
                  <span>{new Date(c.created_at).toLocaleDateString()}</span>
                  {c.complainant && <><span>•</span><span>{c.complainant.full_name}</span></>}
                </div>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${priorityBadge[c.priority] || 'badge-medium'}`}>{c.priority}</span>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusBadge[c.status] || 'status-draft'}`}>{c.status?.replace('_', ' ')}</span>
              <ChevronRight className="w-4 h-4 text-text-muted group-hover:text-primary transition-colors" />
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
