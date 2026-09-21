import { useState, useEffect } from 'react';
import { datasetAPI } from '../api';
import { Search, Scale, BookOpen, ExternalLink, ChevronDown, ChevronUp, Filter } from 'lucide-react';

const ACTS = [
  { id: '', label: 'All Acts' },
  { id: 'BNS', label: 'BNS 2023', fullName: 'Bharatiya Nyaya Sanhita', color: '#3b82f6' },
  { id: 'BNSS', label: 'BNSS 2023', fullName: 'Bharatiya Nagarik Suraksha Sanhita', color: '#8b5cf6' },
  { id: 'BSA', label: 'BSA 2023', fullName: 'Bharatiya Sakshya Adhiniyam', color: '#10b981' },
  { id: 'IT_ACT', label: 'IT Act', fullName: 'Information Technology Act 2000', color: '#f59e0b' },
];

const CATEGORIES = [
  { id: '', label: 'All Categories' },
  { id: 'cybercrime', label: '💻 Cybercrime' },
  { id: 'fraud', label: '💰 Fraud' },
  { id: 'theft', label: '🔓 Theft' },
  { id: 'assault', label: '⚡ Assault' },
  { id: 'murder', label: '🔴 Murder' },
  { id: 'kidnapping', label: '🔗 Kidnapping' },
  { id: 'domestic_violence', label: '🏠 Domestic Violence' },
  { id: 'sexual_harassment', label: '🛡️ Sexual Harassment' },
  { id: 'drug_offense', label: '💊 Drug Offense' },
  { id: 'all', label: '🌐 Procedural / All' },
];

const ACT_COLORS = { BNS: '#3b82f6', BNSS: '#8b5cf6', BSA: '#10b981', IT_ACT: '#f59e0b' };

export default function LegalSectionsPage() {
  const [sections, setSections] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedAct, setSelectedAct] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [expanded, setExpanded] = useState({});
  const [showFilters, setShowFilters] = useState(false);

  const fetchSections = async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (selectedAct) params.act = selectedAct;
      if (selectedCategory) params.category = selectedCategory;
      const res = await datasetAPI.getLegalSections(params);
      setSections(res.data.sections);
      setTotal(res.data.total);
    } catch {
      // fallback empty
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchSections(); }, [selectedAct, selectedCategory]);
  useEffect(() => {
    const t = setTimeout(fetchSections, 400);
    return () => clearTimeout(t);
  }, [search]);

  const toggleExpand = (id) => setExpanded(p => ({ ...p, [id]: !p[id] }));

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-primary/15 flex items-center justify-center text-2xl">⚖️</div>
          <div>
            <h1 className="text-xl font-bold">Legal Sections Browser</h1>
            <p className="text-sm text-text-secondary">BNS · BNSS · BSA · IT Act — with IPC/CrPC cross-references</p>
          </div>
          <span className="ml-auto text-xs text-text-muted px-3 py-1 bg-surface-2 rounded-full border border-border">{total} sections</span>
        </div>

        {/* Act tabs */}
        <div className="flex gap-2 mt-4 flex-wrap">
          {ACTS.map(act => (
            <button key={act.id} onClick={() => setSelectedAct(act.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all border ${selectedAct === act.id ? 'border-primary/40 bg-primary/15 text-primary-light' : 'border-border bg-surface-2 text-text-secondary hover:text-text'}`}>
              {act.label}
              {act.fullName && <span className="hidden sm:inline text-[10px] opacity-60 ml-1">— {act.fullName}</span>}
            </button>
          ))}
          <button onClick={() => setShowFilters(!showFilters)} className="ml-auto flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium border border-border bg-surface-2 text-text-secondary hover:text-text transition-all">
            <Filter className="w-3 h-3" /> Filters {showFilters ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
        </div>
      </div>

      {/* Search + Filters */}
      <div className="glass-card p-4 space-y-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
          <input type="text" value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Search by section number, offence, or description..."
            className="input-field w-full pl-10" />
        </div>
        {showFilters && (
          <div className="flex flex-wrap gap-2 pt-1">
            {CATEGORIES.map(cat => (
              <button key={cat.id} onClick={() => setSelectedCategory(cat.id)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${selectedCategory === cat.id ? 'bg-primary/20 text-primary-light border border-primary/30' : 'bg-surface-2 text-text-secondary border border-border hover:text-text'}`}>
                {cat.label}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Sections List */}
      {loading ? (
        <div className="flex justify-center py-16">
          <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
        </div>
      ) : sections.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <Scale className="w-12 h-12 mx-auto mb-3 text-text-muted opacity-30" />
          <p className="text-text-muted">No sections found. Try different search terms or filters.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {sections.map((sec, i) => {
            const color = ACT_COLORS[sec.act] || '#6b7280';
            const isExpanded = expanded[i];
            return (
              <div key={i} className="glass-card overflow-hidden hover:border-primary/20 transition-all">
                <div className="flex items-start gap-4 p-4 cursor-pointer" onClick={() => toggleExpand(i)}>
                  {/* Act badge */}
                  <div className="flex-shrink-0 mt-0.5">
                    <span className="text-xs font-bold px-2 py-1 rounded-lg" style={{ backgroundColor: color + '20', color }}>
                      {sec.act?.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-bold text-sm" style={{ color }}>{sec.section}</span>
                      <span className="font-semibold text-sm text-text">{sec.offence}</span>
                    </div>
                    <p className="text-xs text-text-secondary line-clamp-2">{sec.description}</p>
                    <div className="flex items-center gap-3 mt-2">
                      <span className="text-xs text-warning">⚡ {sec.penalty}</span>
                      {sec.old_section && (
                        <span className="text-xs text-text-muted">Replaces: {sec.old_section}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex-shrink-0 text-text-muted">
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </div>
                </div>
                {isExpanded && (
                  <div className="border-t border-border/50 bg-surface/30 p-4 space-y-3">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                      <div>
                        <span className="text-text-muted font-medium">Full Description</span>
                        <p className="text-text-secondary mt-1">{sec.description}</p>
                      </div>
                      <div>
                        <span className="text-text-muted font-medium">Penalty / Punishment</span>
                        <p className="text-warning mt-1 font-medium">{sec.penalty}</p>
                      </div>
                      {sec.old_section && (
                        <div>
                          <span className="text-text-muted font-medium">Old Section (IPC/CrPC/IEA)</span>
                          <p className="text-text-secondary mt-1">{sec.old_section}</p>
                        </div>
                      )}
                      {sec.crime_category && (
                        <div>
                          <span className="text-text-muted font-medium">Crime Category</span>
                          <p className="text-text-secondary mt-1 capitalize">{sec.crime_category?.replace(/_/g, ' ')}</p>
                        </div>
                      )}
                    </div>
                    {sec.landmark_cases?.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-text-muted mb-2">🏛️ Landmark Cases</p>
                        <div className="space-y-1">
                          {sec.landmark_cases.map((lc, j) => (
                            <div key={j} className="flex items-center gap-2 text-xs">
                              <BookOpen className="w-3 h-3 text-primary flex-shrink-0" />
                              <span className="text-primary-light">{lc}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Info footer */}
      <div className="glass-card p-4">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center text-xs text-text-muted">
          <div>
            <span className="block font-semibold text-text mb-1">🇮🇳 BNS 2023</span>
            Replaces IPC 1860 · Effective from 1 July 2024
          </div>
          <div>
            <span className="block font-semibold text-text mb-1">📋 BNSS 2023</span>
            Replaces CrPC 1973 · Procedural law
          </div>
          <div>
            <span className="block font-semibold text-text mb-1">🔍 BSA 2023</span>
            Replaces Indian Evidence Act 1872
          </div>
        </div>
      </div>
    </div>
  );
}
