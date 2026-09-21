import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { Shield, Mail, Lock, User, Phone, ArrowRight, AlertCircle, Badge } from 'lucide-react';

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '', full_name: '', phone: '', role: 'victim', badge_number: '', station: '', rank: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault(); setError(''); setLoading(true);
    try {
      await register(form);
      navigate('/');
    } catch (err) { setError(err.response?.data?.detail || 'Registration failed'); }
    finally { setLoading(false); }
  };

  const update = (k, v) => setForm(p => ({ ...p, [k]: v }));

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface p-4">
      <div className="w-full max-w-lg animate-fadeIn">
        <div className="text-center mb-8">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-primary to-accent flex items-center justify-center animate-pulse-glow">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold gradient-text">Join CrimeGPT</h1>
          <p className="text-text-secondary mt-2">Create your account</p>
        </div>

        <div className="glass-card p-8">
          {error && <div className="mb-4 p-3 rounded-xl bg-danger/10 border border-danger/20 flex items-center gap-2 text-danger text-sm"><AlertCircle className="w-4 h-4" /> {error}</div>}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Role Toggle */}
            <div className="flex gap-2 p-1 bg-surface rounded-xl">
              {['victim', 'officer'].map(r => (
                <button key={r} type="button" onClick={() => update('role', r)}
                  className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-all ${form.role === r ? 'bg-primary text-white' : 'text-text-secondary hover:text-text'}`}>
                  {r === 'victim' ? '👤 Victim/Citizen' : '🛡️ Police Officer'}
                </button>
              ))}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <label className="text-sm font-medium text-text-secondary mb-1 block">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                  <input value={form.full_name} onChange={e => update('full_name', e.target.value)} placeholder="Enter full name" className="input-field pl-10" required />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-text-secondary mb-1 block">Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                  <input type="email" value={form.email} onChange={e => update('email', e.target.value)} placeholder="Email" className="input-field pl-10" required />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium text-text-secondary mb-1 block">Phone</label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                  <input value={form.phone} onChange={e => update('phone', e.target.value)} placeholder="Phone" className="input-field pl-10" />
                </div>
              </div>
              <div className="col-span-2">
                <label className="text-sm font-medium text-text-secondary mb-1 block">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
                  <input type="password" value={form.password} onChange={e => update('password', e.target.value)} placeholder="Min 6 characters" className="input-field pl-10" required minLength={6} />
                </div>
              </div>

              {form.role === 'officer' && (
                <>
                  <div>
                    <label className="text-sm font-medium text-text-secondary mb-1 block">Badge Number</label>
                    <input value={form.badge_number} onChange={e => update('badge_number', e.target.value)} placeholder="Badge #" className="input-field" />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-text-secondary mb-1 block">Rank</label>
                    <input value={form.rank} onChange={e => update('rank', e.target.value)} placeholder="Rank" className="input-field" />
                  </div>
                  <div className="col-span-2">
                    <label className="text-sm font-medium text-text-secondary mb-1 block">Station</label>
                    <input value={form.station} onChange={e => update('station', e.target.value)} placeholder="Police Station" className="input-field" />
                  </div>
                </>
              )}
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full justify-center mt-2">
              {loading ? <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" /> : <>Create Account <ArrowRight className="w-4 h-4" /></>}
            </button>
          </form>

          <p className="mt-4 text-center text-text-secondary text-sm">
            Already have an account? <Link to="/login" className="text-primary-light hover:underline font-medium">Sign In</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
