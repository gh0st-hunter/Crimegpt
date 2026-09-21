import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { casesAPI, documentsAPI } from '../api';
import {
  FileText, Scale, Printer, Download, ChevronDown, ChevronUp,
  Loader, AlertCircle, CheckCircle, Eye, ClipboardList
} from 'lucide-react';

const DOC_TYPES = [
  { id: 'remand_request', name: 'Remand Request Letter', icon: '⚖️', color: '#3b82f6', desc: 'Formal petition to Magistrate for police custody extension', badge: 'BNSS § 187' },
  { id: 'seizure_receipt', name: 'Seizure Receipt (Panchnama)', icon: '📋', color: '#f59e0b', desc: 'Official acknowledgement of items seized during investigation', badge: 'BNSS § 105' },
  { id: 'medical_letter', name: 'Medical Treatment Letter', icon: '🏥', color: '#10b981', desc: 'Request for medical examination of accused or victim', badge: 'BNSS § 51/184' },
  { id: 'court_custody', name: 'Court Custody Letter', icon: '🏛️', color: '#8b5cf6', desc: 'Formal production warrant and custody transfer document', badge: 'BNSS § 187' },
];

const FIELD_CONFIGS = {
  remand_request: [
    { key: 'officer_name', label: 'Officer Name', placeholder: 'Sub-Inspector Rajesh Kumar' },
    { key: 'officer_rank', label: 'Officer Rank', placeholder: 'Sub-Inspector' },
    { key: 'officer_badge', label: 'Badge Number', placeholder: 'DL/2024/001' },
    { key: 'police_station', label: 'Police Station', placeholder: 'Cybercrime PS, New Delhi' },
    { key: 'magistrate_name', label: 'Magistrate Name', placeholder: 'The Ld. Chief Judicial Magistrate' },
    { key: 'court_name', label: 'Court Name', placeholder: 'Chief Judicial Magistrate Court' },
    { key: 'accused_name', label: 'Accused Name', placeholder: 'As per arrest memo' },
    { key: 'accused_age', label: 'Accused Age', placeholder: '35' },
    { key: 'accused_address', label: 'Accused Address', placeholder: 'As per FIR' },
    { key: 'arrest_date', label: 'Date of Arrest', placeholder: 'DD/MM/YYYY' },
    { key: 'additional_notes', label: 'Additional Grounds', placeholder: 'Any specific grounds for remand...', multiline: true },
  ],
  seizure_receipt: [
    { key: 'officer_name', label: 'Officer Name', placeholder: 'Sub-Inspector Name' },
    { key: 'officer_rank', label: 'Officer Rank', placeholder: 'Sub-Inspector' },
    { key: 'officer_badge', label: 'Badge Number', placeholder: 'DL/2024/001' },
    { key: 'police_station', label: 'Police Station', placeholder: 'Crime Branch, Delhi' },
    { key: 'accused_name', label: 'Person from Whom Seized', placeholder: 'Name of person' },
    { key: 'accused_age', label: 'Age', placeholder: '35' },
    { key: 'accused_address', label: 'Address', placeholder: 'Full address' },
    { key: 'arrest_date', label: 'Date of Seizure', placeholder: 'DD/MM/YYYY' },
    { key: 'items_seized', label: 'Items Seized (comma-separated)', placeholder: 'Mobile Phone, Laptop, Cash Rs.5000, Documents', multiline: true },
  ],
  medical_letter: [
    { key: 'officer_name', label: 'Officer Name', placeholder: 'Officer Name' },
    { key: 'officer_rank', label: 'Officer Rank', placeholder: 'Sub-Inspector' },
    { key: 'officer_badge', label: 'Badge Number', placeholder: 'DL/2024/001' },
    { key: 'police_station', label: 'Police Station', placeholder: 'Crime Branch' },
    { key: 'hospital_name', label: 'Hospital Name', placeholder: 'Government District Hospital' },
    { key: 'doctor_name', label: 'Doctor Name', placeholder: 'Medical Officer / CMO' },
    { key: 'accused_name', label: 'Person Name', placeholder: 'Name of accused/victim' },
    { key: 'accused_age', label: 'Age / Sex', placeholder: '35 / Male' },
    { key: 'accused_address', label: 'Address', placeholder: 'Full address' },
    { key: 'additional_notes', label: 'Purpose / Notes', placeholder: 'Specific examination required...', multiline: true },
  ],
  court_custody: [
    { key: 'officer_name', label: 'Officer Name', placeholder: 'Officer Name' },
    { key: 'officer_rank', label: 'Officer Rank', placeholder: 'Inspector' },
    { key: 'officer_badge', label: 'Badge Number', placeholder: 'DL/2024/001' },
    { key: 'police_station', label: 'Police Station', placeholder: 'Crime Branch' },
    { key: 'magistrate_name', label: 'Magistrate Name', placeholder: 'Chief Judicial Magistrate' },
    { key: 'court_name', label: 'Court Name', placeholder: 'CJM Court' },
    { key: 'accused_name', label: 'Accused Name', placeholder: 'Accused full name' },
    { key: 'accused_age', label: 'Accused Age', placeholder: '35' },
    { key: 'accused_address', label: 'Accused Address', placeholder: 'Full address' },
    { key: 'arrest_date', label: 'Date of Arrest', placeholder: 'DD/MM/YYYY' },
    { key: 'additional_notes', label: 'Additional Grounds', placeholder: 'Further grounds for judicial custody...', multiline: true },
  ],
};

export default function DocumentsPage() {
  const [searchParams] = useSearchParams();
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [selectedDocType, setSelectedDocType] = useState(null);
  const [formData, setFormData] = useState({});
  const [previewHtml, setPreviewHtml] = useState('');
  const [generating, setGenerating] = useState(false);
  const [step, setStep] = useState(1); // 1=select case, 2=select type, 3=fill details, 4=preview
  const [error, setError] = useState('');

  useEffect(() => {
    casesAPI.list({ limit: 50 }).then(r => {
      setCases(r.data);
      const caseId = searchParams.get('caseId');
      if (caseId) {
        const found = r.data.find(c => c.id === caseId);
        if (found) { setSelectedCase(found); setStep(2); }
      }
    }).catch(() => {});
  }, []);

  const selectDocType = (type) => {
    setSelectedDocType(type);
    // Auto-fill from case data
    const defaults = {};
    if (selectedCase) {
      defaults.police_station = selectedCase.assigned_officer?.station || '';
    }
    setFormData(defaults);
    setStep(3);
  };

  const generateDocument = async () => {
    if (!selectedCase || !selectedDocType) return;
    setGenerating(true);
    setError('');
    try {
      const res = await documentsAPI.generate(selectedCase.id, {
        doc_type: selectedDocType.id,
        ...formData
      });
      setPreviewHtml(res.data.html);
      setStep(4);
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to generate document');
    } finally {
      setGenerating(false);
    }
  };

  const downloadDocument = () => {
    const blob = new Blob([previewHtml], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedDocType?.id}_${selectedCase?.fir_number?.replace(/\//g, '-') || 'document'}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const printDocument = () => {
    const win = window.open('', '_blank');
    win.document.write(previewHtml);
    win.document.close();
    win.print();
  };

  const reset = () => {
    setSelectedDocType(null);
    setPreviewHtml('');
    setFormData({});
    setStep(selectedCase ? 2 : 1);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-primary/15 flex items-center justify-center text-2xl">📄</div>
          <div>
            <h1 className="text-xl font-bold">Legal Document Generator</h1>
            <p className="text-sm text-text-secondary">Auto-generate official legal documents from case data</p>
          </div>
        </div>
        {/* Progress Steps */}
        <div className="flex items-center gap-2 mt-4 overflow-x-auto">
          {['Select Case', 'Document Type', 'Fill Details', 'Preview & Download'].map((label, i) => (
            <div key={i} className="flex items-center gap-2">
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all ${step > i + 1 ? 'bg-success/20 text-success' : step === i + 1 ? 'bg-primary/20 text-primary-light' : 'bg-surface-2 text-text-muted'}`}>
                {step > i + 1 ? <CheckCircle className="w-3 h-3" /> : <span className="w-3 h-3 rounded-full border border-current flex items-center justify-center text-[8px] font-bold">{i+1}</span>}
                {label}
              </div>
              {i < 3 && <span className="text-text-muted text-xs">›</span>}
            </div>
          ))}
        </div>
      </div>

      {/* Step 1: Select Case */}
      {step === 1 && (
        <div className="glass-card p-6 space-y-4">
          <h3 className="font-semibold flex items-center gap-2"><ClipboardList className="w-4 h-4 text-primary" /> Select a Case</h3>
          {cases.length === 0 ? (
            <p className="text-center text-text-muted py-8">No cases found. Create a case first.</p>
          ) : (
            <div className="grid gap-3">
              {cases.map(c => (
                <button key={c.id} onClick={() => { setSelectedCase(c); setStep(2); }}
                  className="text-left p-4 rounded-xl border border-border/50 bg-surface/30 hover:border-primary/30 hover:bg-primary/5 transition-all">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-sm">{c.title}</p>
                      <p className="text-xs text-text-muted mt-0.5">{c.fir_number || 'No FIR'} · {c.category?.replace(/_/g, ' ')} · {c.status}</p>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full ${c.priority === 'critical' ? 'bg-red-500/20 text-red-400' : c.priority === 'high' ? 'bg-orange-500/20 text-orange-400' : 'bg-blue-500/20 text-blue-400'}`}>{c.priority}</span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Step 2: Select Document Type */}
      {step === 2 && selectedCase && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <button onClick={() => setStep(1)} className="text-xs text-text-muted hover:text-text px-3 py-1.5 rounded-lg bg-surface-2 border border-border transition-colors">← Back</button>
            <div className="glass-card px-4 py-2 flex items-center gap-2">
              <FileText className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium">{selectedCase.title}</span>
              <span className="text-xs text-text-muted">{selectedCase.fir_number}</span>
            </div>
          </div>
          <div className="glass-card p-6 space-y-4">
            <h3 className="font-semibold flex items-center gap-2"><Scale className="w-4 h-4 text-primary" /> Select Document Type</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {DOC_TYPES.map(dt => (
                <button key={dt.id} onClick={() => selectDocType(dt)}
                  className="text-left p-5 rounded-xl border border-border/50 bg-surface/30 hover:bg-primary/5 hover:border-primary/30 transition-all group">
                  <div className="flex items-start gap-3">
                    <span className="text-3xl">{dt.icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-semibold text-sm group-hover:text-primary-light transition-colors">{dt.name}</h4>
                      </div>
                      <p className="text-xs text-text-secondary mb-2">{dt.desc}</p>
                      <span className="text-[10px] px-2 py-0.5 rounded-full border" style={{ color: dt.color, borderColor: dt.color + '40', backgroundColor: dt.color + '10' }}>{dt.badge}</span>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Step 3: Fill Details */}
      {step === 3 && selectedDocType && selectedCase && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <button onClick={() => setStep(2)} className="text-xs text-text-muted hover:text-text px-3 py-1.5 rounded-lg bg-surface-2 border border-border transition-colors">← Back</button>
            <div className="glass-card px-4 py-2 flex items-center gap-2">
              <span>{selectedDocType.icon}</span>
              <span className="text-sm font-medium">{selectedDocType.name}</span>
            </div>
          </div>
          <div className="glass-card p-6 space-y-4">
            <div>
              <h3 className="font-semibold mb-1">Document Details</h3>
              <p className="text-xs text-text-muted">Fill in the required fields. Leave blank to use auto-populated values from the case.</p>
            </div>
            {error && (
              <div className="flex items-center gap-2 p-3 rounded-xl bg-danger/10 border border-danger/20 text-sm text-danger">
                <AlertCircle className="w-4 h-4 flex-shrink-0" /> {error}
              </div>
            )}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {(FIELD_CONFIGS[selectedDocType.id] || []).map(field => (
                <div key={field.key} className={field.multiline ? 'sm:col-span-2' : ''}>
                  <label className="block text-xs font-medium text-text-secondary mb-1">{field.label}</label>
                  {field.multiline ? (
                    <textarea rows={3} className="input-field w-full resize-none" placeholder={field.placeholder}
                      value={formData[field.key] || ''} onChange={e => setFormData(p => ({ ...p, [field.key]: e.target.value }))} />
                  ) : (
                    <input type="text" className="input-field w-full" placeholder={field.placeholder}
                      value={formData[field.key] || ''} onChange={e => setFormData(p => ({ ...p, [field.key]: e.target.value }))} />
                  )}
                </div>
              ))}
            </div>
            <div className="flex gap-3 pt-2">
              <button onClick={generateDocument} disabled={generating} className="btn-primary flex items-center gap-2">
                {generating ? <Loader className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
                {generating ? 'Generating...' : 'Generate Document'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Step 4: Preview & Download */}
      {step === 4 && previewHtml && (
        <div className="space-y-4">
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div className="flex items-center gap-3">
              <button onClick={reset} className="text-xs text-text-muted hover:text-text px-3 py-1.5 rounded-lg bg-surface-2 border border-border transition-colors">← New Document</button>
              <div className="glass-card px-4 py-2 flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-success" />
                <span className="text-sm font-medium text-success">Document Generated</span>
              </div>
            </div>
            <div className="flex gap-2">
              <button onClick={printDocument} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-surface-2 border border-border text-sm hover:bg-surface-3 transition-all">
                <Printer className="w-4 h-4" /> Print
              </button>
              <button onClick={downloadDocument} className="btn-primary">
                <Download className="w-4 h-4" /> Download HTML
              </button>
            </div>
          </div>
          <div className="glass-card overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-surface-2">
              <Eye className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium">Document Preview</span>
              <span className="text-xs text-text-muted ml-auto">Official letterhead format</span>
            </div>
            <div className="bg-white rounded-b-2xl" style={{ minHeight: '600px' }}>
              <iframe
                srcDoc={previewHtml}
                style={{ width: '100%', minHeight: '700px', border: 'none', borderRadius: '0 0 1rem 1rem' }}
                title="Document Preview"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
