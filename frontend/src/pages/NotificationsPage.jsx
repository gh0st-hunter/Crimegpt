import { useState, useEffect } from 'react';
import { notificationsAPI } from '../api';
import { Bell, CheckCheck, Clock, FileText, AlertTriangle, Info } from 'lucide-react';

const typeIcons = {
  fir_status: FileText, investigation_deadline: Clock,
  evidence_submission: AlertTriangle, court_date: Info,
  reminder: Bell, system: Info
};

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    notificationsAPI.list().then(r => setNotifications(r.data)).catch(() => setNotifications([])).finally(() => setLoading(false));
  }, []);

  const markRead = async (id) => {
    await notificationsAPI.markRead(id);
    setNotifications(p => p.map(n => n.id === id ? { ...n, is_read: true } : n));
  };

  const markAllRead = async () => {
    await notificationsAPI.markAllRead();
    setNotifications(p => p.map(n => ({ ...n, is_read: true })));
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Notifications</h1>
          <p className="text-text-secondary">{notifications.filter(n => !n.is_read).length} unread</p>
        </div>
        {notifications.some(n => !n.is_read) && (
          <button onClick={markAllRead} className="btn-secondary"><CheckCheck className="w-4 h-4" /> Mark All Read</button>
        )}
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" /></div>
      ) : notifications.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <Bell className="w-16 h-16 mx-auto mb-4 text-text-muted opacity-30" />
          <h3 className="text-xl font-semibold mb-2">All Caught Up!</h3>
          <p className="text-text-secondary">No notifications to display</p>
        </div>
      ) : (
        <div className="space-y-3">
          {notifications.map((n, i) => {
            const Icon = typeIcons[n.notification_type] || Bell;
            return (
              <div key={n.id} onClick={() => !n.is_read && markRead(n.id)}
                className={`glass-card p-4 flex gap-4 cursor-pointer transition-all ${!n.is_read ? 'border-l-2 border-l-primary bg-primary/5' : 'opacity-75'}`}
                style={{ animationDelay: `${i * 50}ms` }}>
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${!n.is_read ? 'bg-primary/15 text-primary-light' : 'bg-surface-3 text-text-muted'}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div className="flex-1">
                  <h4 className="text-sm font-medium">{n.title}</h4>
                  <p className="text-xs text-text-secondary mt-0.5">{n.message}</p>
                  <p className="text-xs text-text-muted mt-2">{new Date(n.created_at).toLocaleString()}</p>
                </div>
                {!n.is_read && <div className="w-2.5 h-2.5 rounded-full bg-primary flex-shrink-0 mt-2" />}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
