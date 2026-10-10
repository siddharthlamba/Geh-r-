import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  MessageSquare, Search, Shield, Zap, CheckCircle2, ArrowRight, 
  Sparkles, Bot, AlertTriangle, Building2, Users, Clock, HelpCircle,
  Wifi, Wrench, Utensils, Droplets, ShieldAlert, BookOpen
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import SeverityBadge from '../components/SeverityBadge';

export default function LandingPage() {
  const [miniStep, setMiniStep] = useState(0);

  const miniDemoMessages = [
    { sender: 'student', text: "There is no Wi-Fi in Block C since yesterday." },
    { sender: 'ai', text: "Got it! Is the problem affecting everyone in Block C or only your device?" },
    { sender: 'student', text: "Everyone, third floor." },
    { sender: 'ai', text: "Understood! Classified as IT / Network (Medium Severity). Routed to IT Services.\n\nShould I submit this complaint?" },
    { sender: 'student', text: "Yes." },
    { sender: 'ai', text: "Complaint submitted successfully ✅\n\nComplaint ID: GH-2026-1042" }
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900 flex flex-col">
      
      {/* ----------------- HERO SECTION ----------------- */}
      <section className="relative overflow-hidden pt-12 pb-20 lg:pt-20 lg:pb-28 bg-gradient-to-b from-emerald-50/50 via-white to-gray-50 dark:from-slate-900 dark:via-slate-900 dark:to-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            
            {/* Left Content */}
            <div className="lg:col-span-7 space-y-6 text-center lg:text-left">
              
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-100/80 border border-emerald-200 text-emerald-800 text-xs font-semibold shadow-2xs dark:bg-slate-800 dark:border-slate-700 dark:text-emerald-400">
                <Sparkles className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                <span>Gehör • German for "A hearing, being heard"</span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-gray-900 dark:text-slate-200 tracking-tight leading-[1.15]">
                Report problems. <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-teal-500 dark:from-emerald-400 dark:to-teal-400">
                  Get heard. Get resolved.
                </span>
              </h1>

              <p className="text-lg text-gray-600 dark:text-slate-400 max-w-2xl leading-relaxed">
                An AI-powered complaint management system that transforms messy student complaints into structured, prioritized, and automatically routed tickets through a simple WhatsApp conversation.
              </p>

              {/* CTAs */}
              <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-2">
                <Link
                  to="/report"
                  className="w-full sm:w-auto px-7 py-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white dark:bg-emerald-600 dark:text-white dark:hover:bg-emerald-700 dark:shadow-md font-bold text-base shadow-lg shadow-emerald-600/25 flex items-center justify-center gap-2.5 transition-all hover:-translate-y-0.5"
                >
                  <MessageSquare className="w-5 h-5" />
                  <span>Report an Issue</span>
                  <ArrowRight className="w-4 h-4 ml-1" />
                </Link>

                <Link
                  to="/track"
                  className="w-full sm:w-auto px-7 py-3.5 rounded-xl bg-white hover:bg-gray-50 text-gray-800 font-semibold text-base border border-gray-300 shadow-sm dark:bg-slate-800 dark:text-slate-200 dark:border-slate-700 dark:hover:bg-slate-700 dark:shadow-sm flex items-center justify-center gap-2.5 transition-all"
                >
                  <Search className="w-5 h-5 text-gray-500 dark:text-slate-400" />
                  <span>Track Complaint</span>
                </Link>

                <Link
                  to="/admin"
                  className="w-full sm:w-auto px-5 py-3.5 rounded-xl bg-purple-50 hover:bg-purple-100 text-purple-700 font-semibold text-sm border border-purple-200 dark:bg-slate-800 dark:text-indigo-300 dark:border-slate-700 dark:hover:bg-slate-700 dark:shadow-sm flex items-center justify-center gap-2 transition-all"
                >
                  <Shield className="w-4 h-4 text-purple-600 dark:text-indigo-400" />
                  <span>Admin Portal</span>
                </Link>
              </div>

              {/* Quick Trust Badges */}
              <div className="pt-4 flex flex-wrap items-center justify-center lg:justify-start gap-6 text-xs text-gray-500 dark:text-slate-400 font-medium">
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                  <span>No forms required</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                  <span>Automatic severity calculation</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                  <span>Real-time tracking ID</span>
                </div>
              </div>

            </div>

            {/* Right: Live Interactive Miniature WhatsApp Widget */}
            <div className="lg:col-span-5 flex justify-center">
              <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl border border-gray-200 dark:bg-slate-800 dark:border-slate-700 dark:shadow-xl overflow-hidden transform transition-all hover:scale-[1.01]">
                
                {/* Mini WhatsApp Header */}
                <div className="bg-[#008069] px-4 py-3 flex items-center justify-between text-white shadow-sm">
                  <div className="flex items-center gap-2.5">
                    <div className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold leading-tight">Gehor AI Desk</h4>
                      <p className="text-[11px] text-emerald-100 flex items-center gap-1">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-300"></span>
                        online • 24/7 campus triage
                      </p>
                    </div>
                  </div>
                  <span className="text-[10px] bg-emerald-800/60 px-2 py-0.5 rounded-full font-mono">
                    WhatsApp Mock
                  </span>
                </div>

                {/* Mini Chat Feed */}
                <div className="p-4 space-y-3 bg-[#efeae2] h-80 overflow-y-auto wa-chat-pattern text-xs">
                  {miniDemoMessages.slice(0, miniStep + 2).map((m, idx) => (
                    <div
                      key={idx}
                      className={`flex ${m.sender === 'student' ? 'justify-end' : 'justify-start'} animate-in fade-in duration-300`}
                    >
                      <div
                        className={`max-w-[85%] rounded-xl p-2.5 shadow-2xs whitespace-pre-line leading-relaxed ${
                          m.sender === 'student'
                            ? 'bg-[#d9fdd3] text-gray-900 rounded-tr-none'
                            : 'bg-white text-gray-900 rounded-tl-none border border-gray-100'
                        }`}
                      >
                        {m.text}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Mini Step Controls */}
                <div className="p-3 bg-gray-50 border-t border-gray-200 flex items-center justify-between text-xs">
                  <span className="text-gray-500 font-medium">
                    Simulate Turn ({Math.min(miniStep + 1, miniDemoMessages.length / 2)} of 3)
                  </span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setMiniStep(prev => Math.min(prev + 2, miniDemoMessages.length - 2))}
                      disabled={miniStep >= miniDemoMessages.length - 2}
                      className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-40 text-white rounded-lg font-semibold transition-colors"
                    >
                      Next Response
                    </button>
                    <button
                      onClick={() => setMiniStep(0)}
                      className="px-2.5 py-1.5 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg font-medium transition-colors"
                    >
                      Restart
                    </button>
                  </div>
                </div>

              </div>
            </div>

          </div>
        </div>
      </section>

      {/* ----------------- 7-STEP HACKATHON LIFECYCLE ----------------- */}
      <section className="py-16 bg-white border-y border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <h2 className="text-xs font-bold text-emerald-700 uppercase tracking-widest">
              END-TO-END AUTOMATION PIPELINE
            </h2>
            <p className="mt-2 text-3xl font-extrabold text-gray-900">
              From natural voice to resolution in 7 steps
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-7 gap-3 text-center">
            {[
              { step: '1', title: 'Student', sub: 'Speaks naturally on WhatsApp' },
              { step: '2', title: 'AI Intent', sub: 'Detects problem & extracts slots' },
              { step: '3', title: 'Classify', sub: 'Categorizes into 12 campus depts' },
              { step: '4', title: 'Severity', sub: 'Calculates risk & SLA rules' },
              { step: '5', title: 'Confirm', sub: 'Human-in-the-loop validation' },
              { step: '6', title: 'Ticket ID', sub: 'Generates GH-2026-XXXX ID' },
              { step: '7', title: 'Resolved', sub: 'Live tracking & closing feedback' },
            ].map((st, i) => (
              <div key={i} className="p-4 rounded-xl bg-gray-50 border border-gray-200 relative group hover:border-emerald-400 transition-all">
                <span className="w-7 h-7 mx-auto rounded-full bg-emerald-600 text-white text-xs font-bold flex items-center justify-center mb-2 shadow-sm">
                  {st.step}
                </span>
                <h4 className="text-sm font-bold text-gray-900">{st.title}</h4>
                <p className="text-[11px] text-gray-500 mt-1">{st.sub}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ----------------- LIVE STATS SECTION ----------------- */}
      <section className="py-12 bg-emerald-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <p className="text-4xl font-extrabold text-emerald-300 font-mono">1,248+</p>
              <p className="text-xs text-emerald-200 mt-1 uppercase font-semibold">Complaints Processed</p>
            </div>
            <div>
              <p className="text-4xl font-extrabold text-emerald-300 font-mono">94.2%</p>
              <p className="text-xs text-emerald-200 mt-1 uppercase font-semibold">Routing Accuracy</p>
            </div>
            <div>
              <p className="text-4xl font-extrabold text-emerald-300 font-mono">&lt; 90s</p>
              <p className="text-xs text-emerald-200 mt-1 uppercase font-semibold">Average Filing Time</p>
            </div>
            <div>
              <p className="text-4xl font-extrabold text-emerald-300 font-mono">100%</p>
              <p className="text-xs text-emerald-200 mt-1 uppercase font-semibold">Audited Status History</p>
            </div>
          </div>
        </div>
      </section>

      {/* ----------------- COMPLAINT CATEGORIES SHOWCASE ----------------- */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <h2 className="text-xs font-bold text-emerald-700 uppercase tracking-widest">
              CAMPUS COVERAGE
            </h2>
            <p className="mt-2 text-3xl font-extrabold text-gray-900">
              One conversational desk for every institutional concern
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            {[
              { icon: Wifi, title: 'IT & Wi-Fi', desc: 'SSID, routers, portals', color: 'text-blue-600 bg-blue-50' },
              { icon: Droplets, title: 'Plumbing', desc: 'Leaks, pipes, tanks', color: 'text-cyan-600 bg-cyan-50' },
              { icon: Zap, title: 'Electrical', desc: 'Sparks, power cuts, AC', color: 'text-amber-600 bg-amber-50' },
              { icon: Utensils, title: 'Hostel Mess', desc: 'Hygiene, meal quality', color: 'text-orange-600 bg-orange-50' },
              { icon: ShieldAlert, title: 'Security', desc: 'Hazards, locks, gates', color: 'text-red-600 bg-red-50' },
              { icon: BookOpen, title: 'Academic', desc: 'Classrooms, schedules', color: 'text-purple-600 bg-purple-50' },
            ].map((cat, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-white border border-gray-200 text-center hover:shadow-md transition-shadow">
                <div className={`w-10 h-10 mx-auto rounded-lg flex items-center justify-center mb-3 ${cat.color}`}>
                  <cat.icon className="w-5 h-5" />
                </div>
                <h4 className="text-sm font-bold text-gray-900">{cat.title}</h4>
                <p className="text-[11px] text-gray-500 mt-0.5">{cat.desc}</p>
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* ----------------- FOOTER ----------------- */}
      <footer className="mt-auto bg-gray-900 text-gray-400 py-10 border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="w-8 h-8 rounded-lg bg-emerald-600 text-white font-bold flex items-center justify-center text-sm">
              G
            </span>
            <div>
              <span className="text-white font-bold text-sm">Gehör</span>
              <p className="text-[11px] text-gray-500">AI Complaint Management Platform • Built for Hackathon</p>
            </div>
          </div>
          <p className="text-xs text-gray-500">
            Simulated WhatsApp experience • Zero friction campus redressal
          </p>
        </div>
      </footer>

    </div>
  );
}
