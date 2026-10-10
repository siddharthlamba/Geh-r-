import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Save, Building2, BookOpen, CheckCircle2, Shield, Plus } from 'lucide-react';
import { getRoutingRules, updateRoutingRule, getDepartments, getFaqDocs } from '../api';

export default function AdminSettings() {
  const [rules, setRules] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [faqDocs, setFaqDocs] = useState([]);
  const [editingRule, setEditingRule] = useState(null);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const loadSettings = async () => {
    setIsLoading(true);
    try {
      const [r, d, f] = await Promise.all([
        getRoutingRules(),
        getDepartments(),
        getFaqDocs()
      ]);
      setRules(r);
      setDepartments(d);
      setFaqDocs(f);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const handleUpdateDept = async (category, newDept) => {
    try {
      await updateRoutingRule({
        category,
        department_name: newDept,
        priority_level: 'NORMAL',
        notes: 'Updated via Admin portal'
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 2000);
      loadSettings();
    } catch (err) {
      alert("Failed to update rule: " + err.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex items-center gap-3 pb-4 border-b border-gray-200">
          <Link
            to="/admin"
            className="p-2 bg-white hover:bg-gray-100 rounded-xl border border-gray-200 text-gray-600 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">
              Routing Engine & Department Configuration
            </h1>
            <p className="text-xs text-gray-500">
              Configure Category-to-Department auto-routing tables, SLA targets, and RAG knowledge base
            </p>
          </div>
        </div>

        {savedSuccess && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs font-semibold flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Routing rule updated successfully! New complaints will route according to this change.</span>
          </div>
        )}

        {/* ----------------- ROUTING TABLE ----------------- */}
        <div className="bg-white rounded-2xl shadow-2xs border border-gray-200 overflow-hidden">
          <div className="p-5 border-b border-gray-200">
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider">
              Category-to-Department Routing Matrix
            </h3>
            <p className="text-xs text-gray-500 mt-0.5">
              When Gehor AI classifies an issue into a category, it automatically routes cases to the assigned department.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-gray-50/80 border-b border-gray-200 text-gray-500 uppercase font-semibold text-[11px] tracking-wider">
                  <th className="py-3 px-4">Complaint Category</th>
                  <th className="py-3 px-4">Target Department</th>
                  <th className="py-3 px-4">Priority Level</th>
                  <th className="py-3 px-4 text-right">Quick Change</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {rules.map((rule) => (
                  <tr key={rule.category} className="hover:bg-gray-50/50">
                    <td className="py-3.5 px-4 font-bold text-gray-800">
                      {rule.category}
                    </td>
                    <td className="py-3.5 px-4 text-gray-900 font-medium">
                      <span className="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200">
                        {rule.department_name}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-gray-500">
                      {rule.priority_level}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <select
                        value={rule.department_name}
                        onChange={(e) => handleUpdateDept(rule.category, e.target.value)}
                        className="text-xs bg-gray-50 border border-gray-300 rounded-lg p-1.5 focus:ring-2 focus:ring-emerald-500"
                      >
                        {departments.map((d) => (
                          <option key={d.name} value={d.name}>{d.name}</option>
                        ))}
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* ----------------- ACTIVE DEPARTMENTS DIRECTORY ----------------- */}
        <div className="bg-white rounded-2xl shadow-2xs border border-gray-200 p-6 space-y-4">
          <div className="flex items-center gap-2">
            <Building2 className="w-5 h-5 text-emerald-600" />
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider">
              Institutional Department SLAs & Contacts
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {departments.map((d) => (
              <div key={d.name} className="p-4 rounded-xl bg-gray-50 border border-gray-200 space-y-2">
                <div className="flex items-baseline justify-between">
                  <h4 className="text-sm font-bold text-gray-900">{d.name}</h4>
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                    SLA: {d.sla_hours}h
                  </span>
                </div>
                <p className="text-xs text-gray-600">{d.description}</p>
                <div className="flex items-center justify-between text-[11px] text-gray-500 pt-1">
                  <span>Head: {d.head_name}</span>
                  <span className="font-mono text-emerald-700">{d.contact_email}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ----------------- KNOWLEDGE BASE / FAQ ----------------- */}
        <div className="bg-white rounded-2xl shadow-2xs border border-gray-200 p-6 space-y-4">
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-purple-600" />
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider">
              Campus Knowledge Base Documents (FAQ Engine)
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {faqDocs.map((doc) => (
              <div key={doc.id} className="p-4 rounded-xl bg-purple-50/50 border border-purple-200 space-y-2">
                <h4 className="text-sm font-bold text-purple-950">{doc.title}</h4>
                <span className="text-[10px] font-semibold text-purple-700 bg-purple-100 px-2 py-0.5 rounded-full inline-block">
                  {doc.category}
                </span>
                <p className="text-xs text-gray-700 whitespace-pre-line leading-relaxed">
                  {doc.content}
                </p>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
