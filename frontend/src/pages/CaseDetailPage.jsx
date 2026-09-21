import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { casesAPI, evidenceAPI, kanoonAPI, documentsAPI } from '../api';
import {
  FileText, Clock, Upload, Scale, Lightbulb, AlertTriangle,
  CheckCircle, Sparkles, ChevronDown, ChevronUp, Folder, Search, ExternalLink,
  BookOpen, Plus, Loader, Send, Download
} from 'lucide-react';

const priorityBadge = { critical: 'badge-critical', high: 'badge-high', medium: 'badge-medium', low: 'badge-low' };
const statusBadge = { draft: 'status-draft', filed: 'status-filed', under_investigation: 'status-under_investigation', closed: 'status-closed', evidence_collection: 'status-under_investigation' };
const timelineIcons = { complaint: '📝', fir: '📄', legal: '⚖️', investigation: '🔍', evidence: '📎', status_change: '🔄', court: '🏛️' };

const DOC_TYPES = [
  { id: 'remand_request', name: 'Remand Request', icon: '⚖️' },
  { id: 'seizure_receipt', name: 'Seizure Receipt', icon: '📋' },
  { id: 'medical_letter', name: 'Medical Letter', icon: '🏥' },
  { id: 'court_custody', name: 'Court Custody', icon: '🏛️' },
];

export default function CaseDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const [caseData, setCaseData] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [evidence, setEvidence] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState('overview');
  const [genLoading, setGenLoading] = useState(false);
  const [expandFIR, setExpandFIR] = useState(false);
  const [kanoonQuery, setKanoonQuery] = useState('');
  const [kanoonResults, setKanoonResults] = useState(null);
  const [kanoonLoading, setKanoonLoading] = useState(false);
  const [landmarkJudgments, setLandmarkJudgments] = useState([]);
  const [landmarkLoading, setLandmarkLoading] = useState(false);

  // Timeline add form
  const [showAddEvent, setShowAddEvent] = useState(false);
  const [newEvent, setNewEvent] = useState({ title: '', description: '', event_type: 'investigation', event_date: new Date().toISOString().slice(0, 16) });
  const [addingEvent, setAddingEvent] = useState(false);

  // Document generation
  const [docGenerating, setDocGenerating] = useState({});
  const [docPreviews, setDocPreviews] = useState({});

  useEffect(() => {
    Promise.all([
      casesAPI.get(id).then(r => setCaseData(r.data)),
      casesAPI.getTimeline(id).then(r => setTimeline(r.data)),
      evidenceAPI.list(id).then(r => setEvidence(r.data))
    ]).catch(() => {}).finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    if (tab === 'legal' && landmarkJudgments.length === 0 && !landmarkLoading) {
      loadLandmarkJudgments();
    }
  }, [tab]);

  const loadLandmarkJudgments = async () => {
    setLandmarkLoading(true);
    try {
      const res = await casesAPI.getLandmarkJudgments(id);
      setLandmarkJudgments(res.data.judgments || []);
    } catch { } finally {
      setLandmarkLoading(false);
    }
  };

  const generateFIR = async () => {
    setGenLoading(true);
    try {
      const res = await casesAPI.generateFIR(id);
      setCaseData(res.data);
      const tlRes = await casesAPI.getTimeline(id);
      setTimeline(tlRes.data);
    } catch (e) { alert('Failed to generate FIR'); }
    finally { setGenLoading(false); }
  };

  const searchCaseLaw = async (e) => {
    e?.preventDefault();
    const q = kanoonQuery.trim() || caseData?.category?.replace(/_/g, ' ');
    if (!q) return;
    setKanoonLoading(true);
    try {
      const res = await kanoonAPI.search(q);
      setKanoonResults(res.data);
    } catch {
      alert('Case law search failed');
    } finally {
      setKanoonLoading(false);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const fd = new FormData();
    fd.append('file', file);
    fd.append('title', file.name);
    fd.append('evidence_type', file.type.startsWith('image') ? 'image' : 'document');
    try {
      const res = await evidenceAPI.upload(id, fd);
      setEvidence(p => [...p, res.data]);
    } catch (err) { alert('Upload failed'); }
  };

  const addTimelineEvent = async () => {
    if (!newEvent.title) return;
    setAddingEvent(true);
    try {
      const res = await casesAPI.addTimelineEvent(id, {
        ...newEvent,
        event_date: new Date(newEvent.event_date).toISOString()
      });
      setTimeline(p => [...p, res.data]);
      setNewEvent({ title: '', description: '', event_type: 'investigation', event_date: new Date().toISOString().slice(0, 16) });
      setShowAddEvent(false);
    } catch { alert('Failed to add event'); }
    finally { setAddingEvent(false); }
  };

  const quickGenerateDoc = async (docType) => {
    setDocGenerating(p => ({ ...p, [docType]: true }));
    try {
      const res = await documentsAPI.generate(id, { doc_type: docType });
      setDocPreviews(p => ({ ...p, [docType]: res.data.html }));
    } catch { alert('Document generation failed'); }
    finally { setDocGenerating(p => ({ ...p, [docType]: false })); }
  };

  const downloadDoc = (docType) => {
    const html = docPreviews[docType];
    if (!html) return;
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${docType}_${caseData?.fir_number?.replace(/\//g, '-') || 'document'}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) return <div className="flex justify-center py-20"><div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" /></div>;
  if (!caseData) return <div className="text-center py-20 text-text-muted">Case not found</div>;

  const tabs = [
    { key: 'overview', label: 'Overview', icon: FileText },
    { key: 'timeline', label: 'Case Diary', icon: Clock },
    { key: 'evidence', label: `Evidence (${evidence.length})`, icon: Folder },
    { key: 'legal', label: 'Legal Intel', icon: Scale },
    { key: 'documents', label: 'Documents', icon: BookOpen },
  ];

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="glass-card p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-2">
              {caseData.fir_number && <span className="text-xs px-2.5 py-1 bg-primary/10 text-primary-light rounded-full font-medium">{caseData.fir_number}</span>}
              <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${priorityBadge[caseData.priority]}`}>{caseData.priority}</span>
              <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${statusBadge[caseData.status] || 'status-draft'}`}>{caseData.status.replace('_', ' ')}</span>
            </div>
            <h1 className="text-xl font-bold mb-1">{caseData.title}</h1>
            <p className="text-sm text-text-secondary capitalize">{caseData.category?.replace('_', ' ')} · Filed {caseData.filed_at ? new Date(caseData.filed_at).toLocaleDateString() : 'Not filed yet'}</p>
          </div>
          <div className="flex gap-2 flex-wrap">
            {!caseData.ai_fir_text && (
              <button onClick={generateFIR} disabled={genLoading} className="btn-primary">
                {genLoading ? <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" /> : <><Sparkles className="w-4 h-4" /> Generate FIR</>}
              </button>
            )}
            <Link to={`/documents?caseId=${id}`} className="btn-secondary flex items-center gap-2 text-sm">
              <BookOpen className="w-4 h-4" /> Documents
            </Link>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-surface-2 rounded-xl border border-border overflow-x-auto">
        {tabs.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${tab === t.key ? 'bg-primary/15 text-primary-light' : 'text-text-secondary hover:text-text hover:bg-surface-3/50'}`}>
            <t.icon className="w-4 h-4" /> {t.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {tab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="glass-card p-6 space-y-4">
            <h3 className="font-semibold flex items-center gap-2"><FileText className="w-4 h-4 text-primary" /> Description</h3>
            <p className="text-sm text-text-secondary leading-relaxed whitespace-pre-wrap">{caseData.description}</p>
            {caseData.incident_location && <p className="text-sm text-text-muted">📍 {caseData.incident_location}</p>}
            {caseData.ai_priority_reasoning && (
              <div className="p-3 rounded-xl bg-primary/5 border border-primary/10">
                <p className="text-xs text-primary-light font-medium mb-1">🤖 AI Priority Assessment</p>
                <p className="text-sm text-text-secondary">{caseData.ai_priority_reasoning}</p>
              </div>
            )}
          </div>

          {caseData.ai_fir_text && (
            <div className="glass-card p-6 space-y-3">
              <div className="flex items-center justify-between cursor-pointer" onClick={() => setExpandFIR(!expandFIR)}>
                <h3 className="font-semibold flex items-center gap-2"><Sparkles className="w-4 h-4 text-accent" /> AI-Generated FIR</h3>
                {expandFIR ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </div>
              <div className={`text-sm text-text-secondary whitespace-pre-wrap leading-relaxed ${expandFIR ? '' : 'max-h-[200px] overflow-hidden'} transition-all`}>
                {caseData.ai_fir_text}
              </div>
              {!expandFIR && <div className="bg-gradient-to-t from-surface-2/90 to-transparent h-12 -mt-12 relative z-10" />}
            </div>
          )}

          {caseData.ai_investigation_steps?.length > 0 && (
            <div className="glass-card p-6 space-y-3">
              <h3 className="font-semibold flex items-center gap-2"><Lightbulb className="w-4 h-4 text-warning" /> Investigation Steps</h3>
              <ol className="space-y-2">
                {caseData.ai_investigation_steps.map((step, i) => (
                  <li key={i} className="flex gap-3 text-sm text-text-secondary">
                    <span className="w-6 h-6 rounded-full bg-warning/10 text-warning text-xs flex items-center justify-center flex-shrink-0 font-bold">{i + 1}</span>
                    <span>{typeof step === 'string' ? step : step.description || step.step || JSON.stringify(step)}</span>
                  </li>
                ))}
              </ol>
            </div>
          )}

          {caseData.ai_required_evidence?.length > 0 && (
            <div className="glass-card p-6 space-y-3">
              <h3 className="font-semibold flex items-center gap-2"><AlertTriangle className="w-4 h-4 text-danger" /> Required Evidence</h3>
              <ul className="space-y-2">
                {caseData.ai_required_evidence.map((ev, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-text-secondary">
                    <CheckCircle className="w-4 h-4 text-success/50 flex-shrink-0" />
                    {typeof ev === 'string' ? ev : ev.description || JSON.stringify(ev)}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Case Diary / Timeline Tab */}
      {tab === 'timeline' && (
        <div className="space-y-4">
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="font-semibold flex items-center gap-2"><Clock className="w-4 h-4 text-primary" /> Case Diary</h3>
              <button onClick={() => setShowAddEvent(!showAddEvent)} className="flex items-center gap-2 text-sm px-3 py-1.5 rounded-lg bg-primary/10 text-primary-light hover:bg-primary/20 transition-all">
                <Plus className="w-4 h-4" /> Add Entry
              </button>
            </div>

            {showAddEvent && (
              <div className="mb-6 p-4 rounded-xl bg-surface/50 border border-border space-y-3">
                <h4 className="text-sm font-medium">New Case Diary Entry</h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <input type="text" className="input-field" placeholder="Entry title / action taken" value={newEvent.title} onChange={e => setNewEvent(p => ({ ...p, title: e.target.value }))} />
                  <select className="input-field" value={newEvent.event_type} onChange={e => setNewEvent(p => ({ ...p, event_type: e.target.value }))}>
                    <option value="investigation">Investigation</option>
                    <option value="evidence">Evidence</option>
                    <option value="legal">Legal</option>
                    <option value="court">Court</option>
                    <option value="complaint">Complaint</option>
                    <option value="status_change">Status Change</option>
                  </select>
                  <input type="datetime-local" className="input-field" value={newEvent.event_date} onChange={e => setNewEvent(p => ({ ...p, event_date: e.target.value }))} />
                  <textarea rows={2} className="input-field resize-none" placeholder="Description / notes..." value={newEvent.description} onChange={e => setNewEvent(p => ({ ...p, description: e.target.value }))} />
                </div>
                <div className="flex gap-2">
                  <button onClick={addTimelineEvent} disabled={addingEvent || !newEvent.title} className="btn-primary text-sm flex items-center gap-2">
                    {addingEvent ? <Loader className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />} Add Entry
                  </button>
                  <button onClick={() => setShowAddEvent(false)} className="px-4 py-2 rounded-xl text-sm border border-border text-text-secondary hover:text-text transition-colors">Cancel</button>
                </div>
              </div>
            )}

            {timeline.length === 0 ? (
              <p className="text-center text-text-muted py-8">No case diary entries yet</p>
            ) : (
              <div className="relative pl-8">
                <div className="timeline-line" />
                {timeline.map((evt, i) => (
                  <div key={evt.id} className="relative flex gap-4 pb-8 last:pb-0 animate-fadeIn" style={{ animationDelay: `${i * 100}ms` }}>
                    <div className={`timeline-dot ${evt.is_ai_generated ? 'bg-accent/20 text-accent' : 'bg-primary/20 text-primary-light'}`}>
                      <span className="text-lg">{timelineIcons[evt.event_type] || '📌'}</span>
                    </div>
                    <div className="flex-1 glass-card p-4 ml-2">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium text-sm">{evt.title}</h4>
                        {evt.is_ai_generated && <span className="text-[10px] px-1.5 py-0.5 bg-accent/10 text-accent rounded">AI</span>}
                        <span className="text-[10px] px-1.5 py-0.5 bg-surface-2 text-text-muted rounded ml-auto capitalize">{evt.event_type?.replace(/_/g, ' ')}</span>
                      </div>
                      {evt.description && <p className="text-xs text-text-secondary">{evt.description}</p>}
                      <p className="text-xs text-text-muted mt-2">{new Date(evt.event_date).toLocaleString()}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Evidence Tab */}
      {tab === 'evidence' && (
        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold flex items-center gap-2"><Folder className="w-4 h-4 text-primary" /> Evidence ({evidence.length})</h3>
            <label className="btn-primary cursor-pointer">
              <Upload className="w-4 h-4" /> Upload
              <input type="file" className="hidden" onChange={handleUpload} />
            </label>
          </div>
          {evidence.length === 0 ? (
            <p className="text-center text-text-muted py-8">No evidence uploaded yet</p>
          ) : (
            <div className="space-y-3">
              {evidence.map(ev => (
                <div key={ev.id} className="flex items-center gap-4 p-3 rounded-xl bg-surface/50 border border-border/50">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary-light">
                    {ev.evidence_type === 'image' ? '🖼️' : ev.evidence_type === 'document' ? '📄' : '📎'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{ev.title}</p>
                    <p className="text-xs text-text-muted">{ev.evidence_type} · {ev.file_size ? (ev.file_size / 1024).toFixed(1) + ' KB' : 'N/A'}</p>
                  </div>
                  {ev.ai_analysis && (
                    <span className="text-xs px-2 py-1 bg-accent/10 text-accent rounded-full">AI Analyzed</span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Legal Intel Tab */}
      {tab === 'legal' && (
        <div className="space-y-4">
          {/* Landmark Judgments */}
          <div className="glass-card p-6 space-y-4">
            <h3 className="font-semibold flex items-center gap-2"><BookOpen className="w-4 h-4 text-accent" /> Landmark Judgments</h3>
            {landmarkLoading ? (
              <div className="flex justify-center py-6"><div className="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full" /></div>
            ) : landmarkJudgments.length > 0 ? (
              <div className="space-y-3">
                {landmarkJudgments.map((j, i) => (
                  <a key={i} href={j.url} target="_blank" rel="noopener noreferrer"
                    className="block p-4 rounded-xl bg-surface/50 border border-border/50 hover:border-accent/30 transition-all group">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-accent group-hover:underline">{j.case}</p>
                        <p className="text-xs text-text-muted mt-1">{j.court} · {j.citation}</p>
                        <p className="text-xs text-text-secondary mt-2">{j.significance}</p>
                      </div>
                      <ExternalLink className="w-4 h-4 text-text-muted flex-shrink-0 mt-0.5" />
                    </div>
                  </a>
                ))}
              </div>
            ) : (
              <p className="text-center text-text-muted py-4">No landmark judgments found for this case category.</p>
            )}
          </div>

          {/* Indian Kanoon Search */}
          <form onSubmit={searchCaseLaw} className="glass-card p-6 space-y-3">
            <h3 className="font-semibold flex items-center gap-2"><Search className="w-4 h-4 text-primary" /> Related Case Law (Indian Kanoon)</h3>
            <div className="flex gap-2">
              <input type="text" value={kanoonQuery} onChange={(e) => setKanoonQuery(e.target.value)}
                placeholder={caseData.category?.replace(/_/g, ' ') || 'Search precedents...'} className="input-field flex-1" />
              <button type="submit" disabled={kanoonLoading} className="btn-primary">
                {kanoonLoading ? <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" /> : 'Search'}
              </button>
            </div>
            {kanoonResults?.docs?.length > 0 && (
              <div className="space-y-3 pt-2">
                {kanoonResults.mocked && (
                  <p className="text-xs text-text-muted">Demo results — set KANOON_API_TOKEN for live Indian Kanoon search.</p>
                )}
                {kanoonResults.docs.map((doc) => (
                  <a key={doc.tid} href={doc.url} target="_blank" rel="noopener noreferrer"
                    className="block p-4 rounded-xl bg-surface/50 border border-border/50 hover:border-primary/20 transition-colors">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-sm font-medium">{doc.title}</p>
                      <ExternalLink className="w-4 h-4 text-text-muted flex-shrink-0" />
                    </div>
                    <p className="text-xs text-text-muted mt-1">{doc.author} · {doc.publishdate}</p>
                    <p className="text-xs text-text-secondary mt-2" dangerouslySetInnerHTML={{ __html: doc.snippet }} />
                  </a>
                ))}
              </div>
            )}
          </form>

          {/* Applicable Legal Sections */}
          {caseData.ai_legal_sections?.length > 0 ? (
            <div className="glass-card p-6 space-y-4">
              <h3 className="font-semibold flex items-center gap-2"><Scale className="w-4 h-4 text-primary" /> Applicable Legal Sections</h3>
              <div className="space-y-3">
                {caseData.ai_legal_sections.map((sec, i) => (
                  <div key={i} className="p-4 rounded-xl bg-surface/50 border border-border/50 hover:border-primary/20 transition-colors">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-semibold text-primary-light">{sec.section}</span>
                    </div>
                    <p className="text-sm text-text-secondary">{sec.description}</p>
                    {sec.penalty && <p className="text-xs text-warning mt-1">Penalty: {sec.penalty}</p>}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="glass-card p-8 text-center">
              <Scale className="w-12 h-12 mx-auto mb-3 text-text-muted opacity-30" />
              <p className="text-text-muted">Legal analysis not available. Generate FIR first to get AI legal suggestions.</p>
            </div>
          )}
        </div>
      )}

      {/* Documents Tab */}
      {tab === 'documents' && (
        <div className="space-y-4">
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold flex items-center gap-2"><BookOpen className="w-4 h-4 text-primary" /> Legal Documents</h3>
              <Link to={`/documents?caseId=${id}`} className="btn-primary text-sm">
                <BookOpen className="w-4 h-4" /> Full Document Editor
              </Link>
            </div>
            <p className="text-xs text-text-muted mb-4">Quick-generate official legal documents. Use the Full Editor for custom details.</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {DOC_TYPES.map(dt => (
                <div key={dt.id} className="p-4 rounded-xl bg-surface/50 border border-border/50 space-y-3">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{dt.icon}</span>
                    <div>
                      <h4 className="font-medium text-sm">{dt.name}</h4>
                      <p className="text-xs text-text-muted">Auto-filled from case data</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => quickGenerateDoc(dt.id)} disabled={docGenerating[dt.id]}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-primary/10 text-primary-light text-xs font-medium hover:bg-primary/20 transition-all">
                      {docGenerating[dt.id] ? <Loader className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
                      {docGenerating[dt.id] ? 'Generating...' : 'Generate'}
                    </button>
                    {docPreviews[dt.id] && (
                      <button onClick={() => downloadDoc(dt.id)}
                        className="flex items-center gap-1 px-3 py-2 rounded-lg bg-success/10 text-success text-xs font-medium hover:bg-success/20 transition-all">
                        <Download className="w-3 h-3" /> Download
                      </button>
                    )}
                  </div>
                  {docPreviews[dt.id] && (
                    <p className="text-[10px] text-success flex items-center gap-1"><CheckCircle className="w-3 h-3" /> Generated successfully</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
