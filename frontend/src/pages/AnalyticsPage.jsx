import { useState, useEffect } from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Filler } from 'chart.js';
import { Doughnut, Bar, Line } from 'react-chartjs-2';
import { casesAPI } from '../api';
import { BarChart3, PieChart, TrendingUp, Activity, Shield, Target } from 'lucide-react';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Filler);

const chartOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { labels: { color: '#94a3b8', font: { size: 11 } } } },
  scales: {
    x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(51,65,85,0.3)' } },
    y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(51,65,85,0.3)' } }
  }
};

export default function AnalyticsPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    casesAPI.getStats().then(r => setStats(r.data)).catch(() => setStats(null)).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex justify-center py-20"><div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" /></div>;
  if (!stats) return <div className="text-center py-20 text-text-muted">Failed to load analytics</div>;

  const priorityData = {
    labels: ['Critical', 'High', 'Medium', 'Low'],
    datasets: [{
      data: [stats.critical_cases, stats.high_priority, stats.medium_priority, stats.low_priority],
      backgroundColor: ['#dc2626', '#f97316', '#eab308', '#22c55e'],
      borderColor: ['#991b1b', '#c2410c', '#a16207', '#15803d'],
      borderWidth: 2
    }]
  };

  const statusData = {
    labels: Object.keys(stats.status_distribution).map(s => s.replace('_', ' ')),
    datasets: [{
      data: Object.values(stats.status_distribution),
      backgroundColor: ['rgba(99,102,241,0.7)', 'rgba(245,158,11,0.7)', 'rgba(16,185,129,0.7)', 'rgba(100,116,139,0.7)', 'rgba(6,182,212,0.7)'],
      borderWidth: 0
    }]
  };

  const categoryData = {
    labels: Object.keys(stats.categories).map(c => c.replace('_', ' ')),
    datasets: [{
      label: 'Cases',
      data: Object.values(stats.categories),
      backgroundColor: 'rgba(99,102,241,0.6)',
      borderColor: '#6366f1',
      borderWidth: 1,
      borderRadius: 8,
    }]
  };

  const trendData = {
    labels: stats.monthly_trend.map(t => t.month),
    datasets: [{
      label: 'Cases Filed',
      data: stats.monthly_trend.map(t => t.count),
      borderColor: '#06b6d4',
      backgroundColor: 'rgba(6,182,212,0.1)',
      fill: true,
      tension: 0.4,
      pointBackgroundColor: '#06b6d4',
    }]
  };

  const kpis = [
    { label: 'Resolution Rate', value: stats.total_firs ? ((stats.closed_cases / stats.total_firs) * 100).toFixed(1) + '%' : '0%', icon: Target, color: 'text-success' },
    { label: 'Active Cases', value: stats.pending_cases, icon: Activity, color: 'text-warning' },
    { label: 'Critical Alert', value: stats.critical_cases, icon: Shield, color: 'text-danger' },
    { label: 'Total Filed', value: stats.total_firs, icon: BarChart3, color: 'text-primary-light' },
  ];

  return (
    <div className="space-y-6 animate-fadeIn">
      <div>
        <h1 className="text-2xl font-bold">Analytics Dashboard</h1>
        <p className="text-text-secondary">Comprehensive crime statistics and insights</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((k, i) => (
          <div key={i} className="glass-card p-5 text-center" style={{ animationDelay: `${i * 100}ms` }}>
            <k.icon className={`w-8 h-8 mx-auto mb-2 ${k.color}`} />
            <p className="text-3xl font-bold">{k.value}</p>
            <p className="text-xs text-text-muted mt-1">{k.label}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <h3 className="font-semibold mb-4 flex items-center gap-2"><PieChart className="w-4 h-4 text-primary" /> Priority Distribution</h3>
          <div className="h-64"><Doughnut data={priorityData} options={{ ...chartOptions, scales: undefined, cutout: '60%' }} /></div>
        </div>
        <div className="glass-card p-6">
          <h3 className="font-semibold mb-4 flex items-center gap-2"><PieChart className="w-4 h-4 text-accent" /> Status Distribution</h3>
          <div className="h-64"><Doughnut data={statusData} options={{ ...chartOptions, scales: undefined, cutout: '60%' }} /></div>
        </div>
        <div className="glass-card p-6">
          <h3 className="font-semibold mb-4 flex items-center gap-2"><BarChart3 className="w-4 h-4 text-primary" /> Cases by Category</h3>
          <div className="h-64"><Bar data={categoryData} options={chartOptions} /></div>
        </div>
        <div className="glass-card p-6">
          <h3 className="font-semibold mb-4 flex items-center gap-2"><TrendingUp className="w-4 h-4 text-accent" /> Monthly Trend</h3>
          <div className="h-64"><Line data={trendData} options={chartOptions} /></div>
        </div>
      </div>
    </div>
  );
}
