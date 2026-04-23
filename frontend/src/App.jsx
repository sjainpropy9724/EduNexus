import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import html2pdf from 'html2pdf.js';
import {
  Activity, BookOpen, AlertTriangle, Download, RefreshCw,
  Server, TrendingUp, Bell, Database, GitBranch, Zap, BarChart2
} from 'lucide-react';
import SyllabusUploader from './components/SyllabusUploader';
import GraphVisualizer from './components/GraphVisualizer';

const API = 'http://127.0.0.1:8001/api/v1';

// ── Reusable Metric Card ──────────────────────────────────────────────────────
const MetricCard = ({ icon, label, value, sub, color = 'text-blue-600' }) => (
  <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
    <div className={`flex items-center gap-2 mb-2 ${color}`}>
      {icon}
      <span className="text-sm font-semibold text-gray-500">{label}</span>
    </div>
    <p className="text-3xl font-bold text-gray-900">{value}</p>
    {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
  </div>
);

// ── Main App ──────────────────────────────────────────────────────────────────
export default function App() {
  const [reportData,   setReportData]   = useState(null);
  const [graphStats,   setGraphStats]   = useState(null);
  const [velocity,     setVelocity]     = useState([]);
  const [auditEvents,  setAuditEvents]  = useState([]);
  const [loading,      setLoading]      = useState(false);
  const [statsLoading, setStatsLoading] = useState(true);
  const [error,        setError]        = useState(null);
  const [activeTab,    setActiveTab]    = useState('dashboard');

  // Load graph stats + velocity + audit events on mount
  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchVelocityAndEvents, 15000); // poll every 15s
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    setStatsLoading(true);
    try {
      const [statsRes, velRes, eventsRes] = await Promise.all([
        axios.get(`${API}/graph/stats`),
        axios.get(`${API}/analytics/velocity?limit=8`),
        axios.get(`${API}/audit/events?limit=5`)
      ]);
      setGraphStats(statsRes.data);
      setVelocity(velRes.data.leaderboard || []);
      setAuditEvents(eventsRes.data.events || []);
    } catch (e) {
      console.error('Dashboard data fetch failed:', e);
    } finally {
      setStatsLoading(false);
    }
  };

  const fetchVelocityAndEvents = async () => {
    try {
      const [velRes, eventsRes] = await Promise.all([
        axios.get(`${API}/analytics/velocity?limit=8`),
        axios.get(`${API}/audit/events?limit=5`)
      ]);
      setVelocity(velRes.data.leaderboard || []);
      setAuditEvents(eventsRes.data.events || []);
    } catch (e) { /* silent */ }
  };

  const runAudit = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(
        `${API}/audit/research_report?generate_text_report=true`
      );
      setReportData(response.data);
      setActiveTab('report');
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Audit failed');
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = () => {
    const element = document.getElementById('printable-report');
    if (!element) return;
    html2pdf().set({
      margin:      0.5,
      filename:    'Edu-Nexus-Curriculum-Amendment-Report.pdf',
      image:       { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF:       { unit: 'in', format: 'letter', orientation: 'portrait' }
    }).from(element).save();
  };

  const nc = graphStats?.node_counts || {};
  const ec = graphStats?.edge_counts || {};

  return (
    <div className="min-h-screen bg-gray-50 font-sans">

      {/* ── Top Nav ── */}
      <header className="bg-white border-b border-gray-200 px-8 py-4 flex justify-between items-center sticky top-0 z-20 shadow-sm">
        <div className="flex items-center gap-3">
          <Server className="text-blue-600" size={28} />
          <div>
            <h1 className="text-xl font-bold text-gray-900">Edu-Nexus V2</h1>
            <p className="text-xs text-gray-400">Autonomous Graph-RAG Curriculum Governance</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {/* Tab switcher */}
          {['dashboard', 'graph', 'report'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium capitalize transition-all
                ${activeTab === tab
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-500 hover:bg-gray-100'}`}
            >
              {tab}
            </button>
          ))}
          <button
            onClick={runAudit}
            disabled={loading}
            className="ml-2 bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2 text-sm font-semibold transition-all disabled:opacity-50"
          >
            {loading
              ? <><RefreshCw className="animate-spin" size={16}/> Running Audit...</>
              : <><Activity size={16}/> Run Audit</>}
          </button>
        </div>
      </header>

      <main className="px-8 py-6 max-w-screen-xl mx-auto">

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 mb-6 rounded">
            <p className="font-bold">Error</p><p>{error}</p>
          </div>
        )}

        {/* ════════════════════════════════ DASHBOARD TAB ══════════════════════ */}
        {activeTab === 'dashboard' && (
          <div className="space-y-8">

            {/* Row 1: Graph Scale Stats */}
            <section>
              <h2 className="text-lg font-bold text-gray-700 mb-3 flex items-center gap-2">
                <Database size={18} className="text-blue-500"/> Knowledge Graph Scale
              </h2>
              {statsLoading ? (
                <div className="text-gray-400 text-sm">Loading stats...</div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <MetricCard icon={<BookOpen size={16}/>}    label="Courses Indexed"     value={nc.Course  || 0} color="text-purple-600"/>
                  <MetricCard icon={<GitBranch size={16}/>}   label="Skills in Graph"     value={(nc.Skill  || 0).toLocaleString()} color="text-blue-600"/>
                  <MetricCard icon={<BarChart2 size={16}/>}   label="Job Postings"        value={(nc.Job    || 0).toLocaleString()} color="text-green-600"/>
                  <MetricCard icon={<Zap size={16}/>}         label="Graph Relationships" value={Object.values(ec).reduce((a,b)=>a+b,0).toLocaleString()} color="text-orange-500"/>
                </div>
              )}
            </section>

            {/* Row 2: CAS + PIS */}
            <section>
              <h2 className="text-lg font-bold text-gray-700 mb-3 flex items-center gap-2">
                <Activity size={18} className="text-blue-500"/> Curriculum Health Scores
                <span className="text-xs font-normal text-gray-400 ml-2">
                  (Run audit to update)
                </span>
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {reportData ? (
                  <>
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertTriangle className="text-orange-500" size={20}/>
                        <span className="font-semibold text-gray-600">Curriculum Alignment Score (CAS)</span>
                      </div>
                      <p className="text-5xl font-bold text-gray-900">
                        {reportData.raw_data.metrics.curriculum_alignment_score_percent}%
                      </p>
                      <div className="mt-3 bg-gray-100 rounded-full h-2">
                        <div
                          className="bg-orange-400 h-2 rounded-full"
                          style={{width: `${reportData.raw_data.metrics.curriculum_alignment_score_percent}%`}}
                        />
                      </div>
                      <p className="text-xs text-gray-400 mt-2">
                        {reportData.raw_data.metrics.stats.covered_demand_points?.toLocaleString()} of{' '}
                        {reportData.raw_data.metrics.stats.total_market_demand_points?.toLocaleString()} market demand points covered
                      </p>
                    </div>

                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                      <div className="flex items-center gap-2 mb-2">
                        <BookOpen className="text-green-500" size={20}/>
                        <span className="font-semibold text-gray-600">Pedagogical Integrity Score (PIS)</span>
                      </div>
                      <p className="text-5xl font-bold text-gray-900">
                        {reportData.raw_data.metrics.pedagogical_integrity_score_percent}%
                      </p>
                      <div className="mt-3 bg-gray-100 rounded-full h-2">
                        <div
                          className="bg-green-400 h-2 rounded-full"
                          style={{width: `${reportData.raw_data.metrics.pedagogical_integrity_score_percent}%`}}
                        />
                      </div>
                      <p className="text-xs text-gray-400 mt-2">
                        {reportData.raw_data.metrics.stats.broken_chains} broken prerequisite chains out of{' '}
                        {reportData.raw_data.metrics.stats.total_prerequisite_chains} total
                      </p>
                    </div>
                  </>
                ) : (
                  <div className="col-span-2 bg-white p-8 rounded-xl border border-dashed border-gray-300 text-center text-gray-400">
                    Click <strong>Run Audit</strong> to calculate CAS and PIS scores
                  </div>
                )}
              </div>
            </section>

            {/* Row 3: Velocity + Audit Events side by side */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

              {/* Velocity Leaderboard */}
              <section className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
                <h2 className="text-base font-bold text-gray-700 mb-4 flex items-center gap-2">
                  <TrendingUp size={18} className="text-rose-500"/>
                  Rising Skills — Market Velocity
                  <span className="ml-auto text-xs text-gray-400 font-normal">Auto-refreshes 15s</span>
                </h2>
                {velocity.length > 0 ? (
                  <div className="space-y-2">
                    {velocity.map((s, i) => (
                      <div key={i} className="flex items-center gap-3">
                        <span className="text-xs text-gray-400 w-4">{i+1}</span>
                        <div className="flex-1">
                          <div className="flex justify-between text-sm mb-0.5">
                            <span className="font-medium text-gray-800">{s.skill}</span>
                            <span className="text-rose-600 font-bold">+{s.velocity}%</span>
                          </div>
                          <div className="bg-gray-100 rounded-full h-1.5">
                            <div
                              className="bg-rose-400 h-1.5 rounded-full"
                              style={{width: `${Math.min(s.velocity * 10, 100)}%`}}
                            />
                          </div>
                        </div>
                        <span className="text-xs text-gray-400">{s.demand?.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-400 text-sm text-center py-4">
                    No velocity data yet. Run simulate_market.py to generate signals.
                  </p>
                )}
              </section>

              {/* Audit Events */}
              <section className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
                <h2 className="text-base font-bold text-gray-700 mb-4 flex items-center gap-2">
                  <Bell size={18} className="text-amber-500"/>
                  Proactive Audit Events
                  <span className="ml-auto text-xs text-gray-400 font-normal">Celery watchdog</span>
                </h2>
                {auditEvents.length > 0 ? (
                  <div className="space-y-3">
                    {auditEvents.map((e, i) => (
                      <div key={i} className="border border-amber-100 bg-amber-50 rounded-lg p-3">
                        <div className="flex justify-between items-start">
                          <span className="text-xs font-bold text-amber-700 uppercase">
                            Threshold Breach
                          </span>
                          <span className="text-xs text-gray-400">
                            {e.triggered_at?.slice(0, 19).replace('T', ' ')}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700 mt-1">
                          <strong>{e.skills_count}</strong> skill(s) exceeded velocity threshold.
                          Top: <strong>{e.top_skill}</strong> (+{e.top_velocity?.toFixed(1)}%)
                        </p>
                        {e.skill_names && (
                          <div className="flex flex-wrap gap-1 mt-1">
                            {e.skill_names.slice(0,4).map((s,j) => (
                              <span key={j} className="text-xs bg-amber-200 text-amber-800 px-2 py-0.5 rounded-full">
                                {s}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-400 text-sm text-center py-4">
                    No autonomous events triggered yet.
                    Start Celery + simulate_market.py to see live alerts.
                  </p>
                )}
              </section>
            </div>

            {/* Row 4: Top Curriculum Gaps */}
            {reportData?.raw_data?.actionable_interventions?.length > 0 && (
              <section className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
                <h2 className="text-base font-bold text-gray-700 mb-4 flex items-center gap-2">
                  <AlertTriangle size={18} className="text-red-500"/>
                  Top Curriculum Gaps — Actionable Interventions
                </h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-xs text-gray-400 border-b">
                        <th className="pb-2 pr-4">Missing Skill</th>
                        <th className="pb-2 pr-4">Market Demand</th>
                        <th className="pb-2 pr-4">Inject Into Course</th>
                        <th className="pb-2">Affinity Score</th>
                      </tr>
                    </thead>
                    <tbody>
                      {reportData.raw_data.actionable_interventions.map((item, i) => (
                        <tr key={i} className="border-b border-gray-50 hover:bg-gray-50">
                          <td className="py-2 pr-4 font-medium text-gray-800">
                            {item.missing_skill}
                          </td>
                          <td className="py-2 pr-4">
                            <span className="bg-red-100 text-red-700 px-2 py-0.5 rounded text-xs font-bold">
                              {item.market_demand?.toLocaleString()}
                            </span>
                          </td>
                          <td className="py-2 pr-4 text-gray-600">
                            {item.suggested_courses?.[0]?.recommended_course || '—'}
                          </td>
                          <td className="py-2 text-gray-500">
                            {item.suggested_courses?.[0]?.affinity_score ?? '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            )}

            {/* Syllabus Uploader */}
            <section>
              <h2 className="text-lg font-bold text-gray-700 mb-3 flex items-center gap-2">
                <BookOpen size={18} className="text-blue-500"/> Ingest New Syllabus
              </h2>
              <SyllabusUploader />
            </section>

          </div>
        )}

        {/* ════════════════════════════════ GRAPH TAB ══════════════════════════ */}
        {activeTab === 'graph' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-bold text-gray-700 flex items-center gap-2">
                <GitBranch size={18} className="text-blue-500"/>
                Knowledge Graph — Courses & Skills Network
              </h2>
              <p className="text-sm text-gray-400">
                Blue = Course &nbsp;|&nbsp; Teal = Skill
              </p>
            </div>
            {graphStats && (
              <div className="flex gap-4 text-sm text-gray-500">
                <span>Showing up to 250 nodes</span>
                <span>•</span>
                <span>{(nc.Skill || 0).toLocaleString()} total skills in graph</span>
                <span>•</span>
                <span>{nc.Course || 0} courses</span>
              </div>
            )}
            <GraphVisualizer />
          </div>
        )}

        {/* ════════════════════════════════ REPORT TAB ═════════════════════════ */}
        {activeTab === 'report' && (
          <div>
            {reportData?.ai_written_report ? (
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 relative">
                <div className="flex justify-between items-center border-b pb-4 mb-6">
                  <h2 className="text-xl font-bold text-gray-800">
                    Curriculum Amendment Report
                  </h2>
                  <button
                    onClick={downloadPDF}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2 text-sm font-semibold"
                  >
                    <Download size={16}/> Download PDF
                  </button>
                </div>
                <div id="printable-report" className="prose max-w-none text-gray-700">
                  <ReactMarkdown>{reportData.ai_written_report}</ReactMarkdown>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-xl border border-dashed border-gray-300 p-16 text-center text-gray-400">
                <Activity size={40} className="mx-auto mb-4 opacity-30"/>
                <p className="text-lg font-medium">No report generated yet</p>
                <p className="text-sm mt-1">Click <strong>Run Audit</strong> to generate the board report</p>
              </div>
            )}
          </div>
        )}

      </main>
    </div>
  );
}
