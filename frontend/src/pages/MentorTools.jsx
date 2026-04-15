import React, { useState, useEffect, useCallback } from 'react';
import {
  FileUp, UploadCloud, BookOpen, CheckCircle, AlertCircle,
  Trash2, Edit2, Save, X, RefreshCw, ChevronDown, ChevronUp,
  Plus, PenLine, Calendar,
} from 'lucide-react';
import api from '../services/api';

// ── Constants ─────────────────────────────────────────────────────────────────
const TYPE_META = {
  mcq:        { label: 'MCQ',           color: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300' },
  true_false: { label: 'True / False',  color: 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300' },
  fill_blank: { label: 'Fill in Blank', color: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300' },
};
const CATEGORIES = ['Coding', 'General Knowledge', 'Math', 'Frontend'];

// ── QuestionCard ──────────────────────────────────────────────────────────────
function QuestionCard({ q, index, onEdit, onDelete }) {
  const [expanded, setExpanded] = useState(true);
  const [editing,  setEditing]  = useState(false);
  const [draft,    setDraft]    = useState({ ...q });
  const meta = TYPE_META[q.type] || TYPE_META.mcq;
  const save = () => { onEdit(index, draft); setEditing(false); };

  return (
    <div className="border border-slate-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 mb-3 overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 bg-slate-50 dark:bg-slate-800/80">
        <div className="flex items-center gap-2">
          <span className="text-slate-400 font-mono text-sm w-6">#{index + 1}</span>
          <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${meta.color}`}>{meta.label}</span>
        </div>
        <div className="flex items-center gap-1">
          {!editing && (
            <button onClick={() => setEditing(true)} className="p-1.5 rounded hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-500">
              <Edit2 size={15} />
            </button>
          )}
          <button onClick={() => onDelete(index)} className="p-1.5 rounded hover:bg-red-100 dark:hover:bg-red-900/30 text-red-400">
            <Trash2 size={15} />
          </button>
          <button onClick={() => setExpanded(p => !p)} className="p-1.5 rounded hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-500 ml-1">
            {expanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
          </button>
        </div>
      </div>
      {expanded && (
        <div className="px-4 py-3 space-y-2 text-sm">
          {editing ? (
            <textarea className="input-field w-full text-sm resize-none" rows={2}
              value={draft.question} onChange={e => setDraft(p => ({ ...p, question: e.target.value }))} />
          ) : (
            <p className="font-medium text-slate-800 dark:text-slate-100">{q.question}</p>
          )}
          {q.options.length > 0 && (
            <ul className="space-y-1 mt-1">
              {(editing ? draft.options : q.options).map((opt, i) => (
                <li key={i} className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border ${
                  opt === (editing ? draft.answer : q.answer)
                    ? 'border-green-400 bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 font-semibold'
                    : 'border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400'}`}>
                  <span className="font-mono text-xs w-4">{String.fromCharCode(65 + i)}.</span>
                  {editing ? (
                    <input className="flex-1 bg-transparent outline-none text-sm" value={opt}
                      onChange={e => { const o = [...draft.options]; o[i] = e.target.value; setDraft(p => ({ ...p, options: o })); }} />
                  ) : <span className="flex-1">{opt}</span>}
                  {opt === (editing ? draft.answer : q.answer) && <CheckCircle size={13} className="shrink-0" />}
                </li>
              ))}
            </ul>
          )}
          {q.type === 'fill_blank' && (
            <p className="text-green-600 dark:text-green-400 text-xs">
              Answer:{' '}
              {editing
                ? <input className="input-field text-xs py-0.5 px-2 ml-1" value={draft.answer}
                    onChange={e => setDraft(p => ({ ...p, answer: e.target.value }))} />
                : <strong>{q.answer}</strong>}
            </p>
          )}
          {editing && q.type === 'mcq' && (
            <div>
              <label className="text-xs text-slate-500 mb-1 block">Correct answer:</label>
              <select className="input-field text-xs py-1" value={draft.answer}
                onChange={e => setDraft(p => ({ ...p, answer: e.target.value }))}>
                {draft.options.map((o, i) => <option key={i} value={o}>{o}</option>)}
              </select>
            </div>
          )}
          <p className="text-xs text-slate-400 italic border-t border-slate-100 dark:border-slate-700 pt-2 mt-1">{q.explanation}</p>
          {editing && (
            <div className="flex gap-2 pt-1">
              <button onClick={save} className="flex items-center gap-1 px-3 py-1.5 bg-green-600 text-white rounded-lg text-xs hover:bg-green-700">
                <Save size={12} /> Save
              </button>
              <button onClick={() => { setDraft({ ...q }); setEditing(false); }}
                className="flex items-center gap-1 px-3 py-1.5 border border-slate-300 rounded-lg text-xs text-slate-600 hover:bg-slate-100 dark:border-slate-600 dark:text-slate-400">
                <X size={12} /> Cancel
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── ManualQuestionForm ────────────────────────────────────────────────────────
function ManualQuestionForm({ onAdd }) {
  const [type,        setType]        = useState('mcq');
  const [question,    setQuestion]    = useState('');
  const [options,     setOptions]     = useState(['', '', '', '']);
  const [answer,      setAnswer]      = useState('');
  const [explanation, setExplanation] = useState('');

  const reset = () => {
    setQuestion(''); setOptions(['', '', '', '']); setAnswer(''); setExplanation('');
  };

  const handleAdd = () => {
    if (!question.trim() || !answer.trim()) return;
    const opts = type === 'mcq'        ? options.filter(o => o.trim())
               : type === 'true_false' ? ['True', 'False']
               : [];
    onAdd({ type, question: question.trim(), options: opts, answer: answer.trim(), explanation: explanation.trim() });
    reset();
  };

  return (
    <div className="border border-slate-200 dark:border-slate-700 rounded-xl p-5 bg-slate-50 dark:bg-slate-800/50 space-y-4">
      {/* Type selector */}
      <div className="flex gap-2">
        {Object.entries(TYPE_META).map(([t, m]) => (
          <button key={t} onClick={() => { setType(t); setAnswer(''); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              type === t
                ? 'bg-blue-600 text-white'
                : 'border border-slate-300 dark:border-slate-600 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700'}`}>
            {m.label}
          </button>
        ))}
      </div>

      {/* Question */}
      <div>
        <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">Question</label>
        <textarea className="input-field w-full text-sm resize-none" rows={2} value={question}
          onChange={e => setQuestion(e.target.value)} placeholder="Enter question text…" />
      </div>

      {/* MCQ options */}
      {type === 'mcq' && (
        <div className="space-y-2">
          <label className="block text-xs font-medium text-slate-600 dark:text-slate-400">Options (A–D)</label>
          {options.map((opt, i) => (
            <div key={i} className="flex items-center gap-2">
              <span className="text-xs text-slate-400 font-mono w-5">{String.fromCharCode(65 + i)}.</span>
              <input className="input-field flex-1 text-sm" value={opt}
                onChange={e => { const o = [...options]; o[i] = e.target.value; setOptions(o); }}
                placeholder={`Option ${String.fromCharCode(65 + i)}`} />
            </div>
          ))}
          <div>
            <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">Correct Answer</label>
            <select className="input-field text-sm" value={answer} onChange={e => setAnswer(e.target.value)}>
              <option value="">Select correct option…</option>
              {options.filter(o => o.trim()).map((o, i) => <option key={i} value={o}>{o}</option>)}
            </select>
          </div>
        </div>
      )}

      {/* True/False answer */}
      {type === 'true_false' && (
        <div>
          <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">Correct Answer</label>
          <select className="input-field text-sm" value={answer} onChange={e => setAnswer(e.target.value)}>
            <option value="">Select…</option>
            <option value="True">True</option>
            <option value="False">False</option>
          </select>
        </div>
      )}

      {/* Fill in blank answer */}
      {type === 'fill_blank' && (
        <div>
          <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">Answer</label>
          <input className="input-field w-full text-sm" value={answer}
            onChange={e => setAnswer(e.target.value)} placeholder="Correct answer…" />
        </div>
      )}

      {/* Explanation */}
      <div>
        <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">Explanation (optional)</label>
        <input className="input-field w-full text-sm" value={explanation}
          onChange={e => setExplanation(e.target.value)} placeholder="Brief explanation of the answer…" />
      </div>

      <button onClick={handleAdd} disabled={!question.trim() || !answer.trim()}
        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
        <Plus size={15} /> Add Question
      </button>
    </div>
  );
}

// ── ChallengesTable ───────────────────────────────────────────────────────────
function ChallengesTable({ challenges, onUpdated, onDeleted }) {
  const [editingId,  setEditingId]  = useState(null);
  const [editDraft,  setEditDraft]  = useState({});
  const [saving,     setSaving]     = useState(false);
  const [toggling,   setToggling]   = useState(null);

  const startEdit = (c) => {
    setEditingId(c.id);
    setEditDraft({ title: c.title, question: c.question, category: c.category, answer: c.answer });
  };

  const saveEdit = async () => {
    setSaving(true);
    try {
      await api.updateChallenge(editingId, editDraft);
      onUpdated(editingId, editDraft);
      setEditingId(null);
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
    } finally { setSaving(false); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this challenge? This cannot be undone.')) return;
    try {
      await api.deleteChallenge(id);
      onDeleted(id);
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
    }
  };

  const handleToggle = async (c) => {
    setToggling(c.id);
    try {
      const { data } = await api.toggleChallengeActive(c.id);
      onUpdated(c.id, { is_active: data.is_active });
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
    } finally {
      setToggling(null);
    }
  };

  // Group by day
  const groups = {};
  for (const c of challenges) {
    const d = c.day ?? 0;
    if (!groups[d]) groups[d] = [];
    groups[d].push(c);
  }
  const sortedDays = Object.keys(groups).map(Number).sort((a, b) => a - b);

  if (challenges.length === 0) {
    return (
      <div className="text-center py-16 text-slate-400 dark:text-slate-500">
        <Calendar size={40} className="mx-auto mb-3 opacity-40" />
        <p>No challenges found. Add one using the form above.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {sortedDays.map(day => (
        <div key={day}>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300 shrink-0">
              Day {day}
            </span>
            <div className="flex-1 h-px bg-slate-200 dark:bg-slate-700" />
            <span className="text-xs text-slate-400 shrink-0">{groups[day].length} challenge{groups[day].length !== 1 ? 's' : ''}</span>
          </div>

          <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-700">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 dark:bg-slate-800/60">
                <tr>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide w-20">Active</th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide w-32">Category</th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">Title</th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">Question</th>
                  <th className="px-4 py-2.5 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide w-36">Answer</th>
                  <th className="px-4 py-2.5 text-right text-xs font-semibold text-slate-500 uppercase tracking-wide w-24">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-700/60">
                {groups[day].map(c => (
                  editingId === c.id ? (
                    <tr key={c.id} className="bg-blue-50/60 dark:bg-blue-900/10 opacity-100">
                     <td className="px-3 py-2"></td>
                      <td className="px-3 py-2">
                        <select className="input-field text-xs py-1 w-full"
                          value={editDraft.category}
                          onChange={e => setEditDraft(p => ({ ...p, category: e.target.value }))}>
                          {CATEGORIES.map(cat => <option key={cat}>{cat}</option>)}
                        </select>
                      </td>
                      <td className="px-3 py-2">
                        <input className="input-field text-xs py-1 w-full min-w-[160px]" value={editDraft.title}
                          onChange={e => setEditDraft(p => ({ ...p, title: e.target.value }))} />
                      </td>
                      <td className="px-3 py-2">
                        <textarea className="input-field text-xs py-1 w-full min-w-[200px] resize-none" rows={2}
                          value={editDraft.question}
                          onChange={e => setEditDraft(p => ({ ...p, question: e.target.value }))} />
                      </td>
                      <td className="px-3 py-2">
                        <input className="input-field text-xs py-1 w-full" value={editDraft.answer}
                          onChange={e => setEditDraft(p => ({ ...p, answer: e.target.value }))} />
                      </td>
                      <td className="px-3 py-2 text-right">
                        <div className="flex justify-end gap-1">
                          <button onClick={saveEdit} disabled={saving} title="Save"
                            className="p-1.5 rounded bg-green-600 text-white hover:bg-green-700">
                            {saving ? <RefreshCw size={13} className="animate-spin" /> : <Save size={13} />}
                          </button>
                          <button onClick={() => setEditingId(null)} title="Cancel"
                            className="p-1.5 rounded border border-slate-300 dark:border-slate-600 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700">
                            <X size={13} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ) : (
                    <tr key={c.id} className={`hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors ${!c.is_active ? 'opacity-50' : ''}`}>
                      <td className="px-4 py-2.5">
                        <button
                          onClick={() => handleToggle(c)}
                          disabled={toggling === c.id}
                          title={c.is_active ? 'Disable for students' : 'Enable for students'}
                          className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none ${
                            c.is_active ? 'bg-green-500' : 'bg-slate-300 dark:bg-slate-600'
                          } ${toggling === c.id ? 'opacity-50 cursor-wait' : 'cursor-pointer'}`}>
                          <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform ${
                            c.is_active ? 'translate-x-4' : 'translate-x-1'
                          }`} />
                        </button>
                      </td>
                      <td className="px-4 py-2.5">
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                          c.category === 'Coding'            ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300'
                        : c.category === 'Math'             ? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300'
                        : c.category === 'Frontend'         ? 'bg-pink-100 text-pink-700 dark:bg-pink-900/40 dark:text-pink-300'
                        : 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300'}`}>
                          {c.category}
                        </span>
                      </td>
                      <td className="px-4 py-2.5 text-slate-700 dark:text-slate-300 text-xs font-medium">{c.title}</td>
                      <td className="px-4 py-2.5 text-slate-500 dark:text-slate-400 text-xs max-w-xs">
                        <span className="line-clamp-2" title={c.question}>{c.question}</span>
                      </td>
                      <td className="px-4 py-2.5 text-green-700 dark:text-green-400 text-xs font-semibold">{c.answer}</td>
                      <td className="px-4 py-2.5 text-right">
                        <div className="flex justify-end gap-1">
                          <button onClick={() => startEdit(c)} title="Edit"
                            className="p-1.5 rounded hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-500">
                            <Edit2 size={14} />
                          </button>
                          <button onClick={() => handleDelete(c.id)} title="Delete"
                            className="p-1.5 rounded hover:bg-red-100 dark:hover:bg-red-900/30 text-red-400">
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
}

// ── Main Component ─────────────────────────────────────────────────────────────
const MentorTools = () => {
  // top-level tab
  const [activeTab, setActiveTab] = useState('generate'); // 'generate' | 'challenges'

  // Generate module sub-tab
  const [genTab, setGenTab] = useState('pdf'); // 'pdf' | 'manual'

  // ── PDF module state ──
  const [pdfFile,      setPdfFile]      = useState(null);
  const [moduleName,   setModuleName]   = useState('');
  const [moduleLevel,  setModuleLevel]  = useState('beginner');
  const [numQuestions, setNumQuestions] = useState(15);
  const [uploading,    setUploading]    = useState(false);
  const [uploadError,  setUploadError]  = useState('');
  const [questions,    setQuestions]    = useState(null);
  const [saving,       setSaving]       = useState(false);
  const [saveResult,   setSaveResult]   = useState(null);

  // ── Manual module state ──
  const [manualName,        setManualName]        = useState('');
  const [manualLevel,       setManualLevel]       = useState('beginner');
  const [manualQuestions,   setManualQuestions]   = useState([]);
  const [manualSaving,      setManualSaving]      = useState(false);
  const [manualSaveResult,  setManualSaveResult]  = useState(null);

  // ── Challenges state ──
  const [challenges,        setChallenges]        = useState([]);
  const [challengesLoading, setChallengesLoading] = useState(false);
  const [challengesError,   setChallengesError]   = useState('');
  const [addForm,   setAddForm]   = useState({ title: '', question: '', category: 'Coding', answer: '' });
  const [addSaving, setAddSaving] = useState(false);
  const [addResult, setAddResult] = useState(null);

  // Load all challenges when tab becomes active
  const loadChallenges = useCallback(async () => {
    setChallengesLoading(true);
    setChallengesError('');
    try {
      const { data } = await api.getAllChallengesAdmin();
      setChallenges(data);
    } catch (err) {
      setChallengesError(err.response?.data?.detail || err.message);
    } finally {
      setChallengesLoading(false);
    }
  }, []);

  useEffect(() => {
    if (activeTab === 'challenges') loadChallenges();
  }, [activeTab, loadChallenges]);

  // ── PDF generate ──
  const handlePdfGenerate = async (e) => {
    e.preventDefault();
    if (!pdfFile) return;
    setUploadError(''); setUploading(true); setQuestions(null); setSaveResult(null);
    const fd = new FormData();
    fd.append('file', pdfFile);
    fd.append('level', moduleLevel);
    fd.append('module_name', moduleName || 'Custom Module');
    fd.append('num_questions', numQuestions);
    try {
      const { data } = await api.uploadPdfModule(fd);
      setQuestions(data.questions);
    } catch (err) {
      setUploadError(err.response?.data?.detail || err.message);
    } finally { setUploading(false); }
  };

  const handlePdfEdit   = (idx, updated) => setQuestions(qs => qs.map((q, i) => i === idx ? { ...q, ...updated } : q));
  const handlePdfDelete = (idx) => setQuestions(qs => qs.filter((_, i) => i !== idx));

  const handleSavePdf = async () => {
    if (!questions?.length) return;
    setSaving(true); setSaveResult(null);
    try {
      const { data } = await api.saveCustomModule({ module_name: moduleName || 'Custom Module', level: moduleLevel, subject: moduleName || 'Custom', questions });
      setSaveResult({ success: true, message: `Module "${data.name}" saved with ${data.questions_saved} questions!` });
      setPdfFile(null); setModuleName(''); setQuestions(null);
    } catch (err) {
      setSaveResult({ success: false, message: err.response?.data?.detail || err.message });
    } finally { setSaving(false); }
  };

  // ── Manual module ──
  const handleAddManualQ    = (q)           => setManualQuestions(qs => [...qs, q]);
  const handleEditManual    = (idx, updated) => setManualQuestions(qs => qs.map((q, i) => i === idx ? { ...q, ...updated } : q));
  const handleDeleteManual  = (idx)         => setManualQuestions(qs => qs.filter((_, i) => i !== idx));

  const handleSaveManual = async () => {
    if (!manualQuestions.length) return;
    setManualSaving(true); setManualSaveResult(null);
    try {
      const { data } = await api.saveCustomModule({ module_name: manualName || 'Custom Module', level: manualLevel, subject: manualName || 'Custom', questions: manualQuestions });
      setManualSaveResult({ success: true, message: `Module "${data.name}" saved with ${data.questions_saved} questions!` });
      setManualName(''); setManualQuestions([]);
    } catch (err) {
      setManualSaveResult({ success: false, message: err.response?.data?.detail || err.message });
    } finally { setManualSaving(false); }
  };

  // ── Add challenge ──
  const handleAddChallenge = async (e) => {
    e.preventDefault();
    if (!addForm.title.trim() || !addForm.question.trim() || !addForm.answer.trim()) return;
    setAddSaving(true); setAddResult(null);
    try {
      await api.createChallengeManual(addForm);
      setAddResult({ success: true, message: 'Challenge added successfully!' });
      setAddForm({ title: '', question: '', category: 'Coding', answer: '' });
      loadChallenges();
    } catch (err) {
      setAddResult({ success: false, message: err.response?.data?.detail || err.message });
    } finally { setAddSaving(false); }
  };

  const handleChallengeUpdated = (id, draft) =>
    setChallenges(cs => cs.map(c => c.id === id ? { ...c, ...draft } : c));
  const handleChallengeDeleted = (id) =>
    setChallenges(cs => cs.filter(c => c.id !== id));

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="container mx-auto px-4 py-12 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-slate-800 dark:text-slate-100">Mentor Tools</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">
          Generate quiz modules and manage daily challenges for your students.
        </p>
      </div>

      {/* ── Main tab bar ── */}
      <div className="flex gap-1 mb-8 p-1 bg-slate-100 dark:bg-slate-800 rounded-xl w-fit">
        {[
          { key: 'generate',   icon: <FileUp size={16} />,   label: 'Generate Module'    },
          { key: 'challenges', icon: <BookOpen size={16} />, label: 'Manage Challenges'  },
        ].map(({ key, icon, label }) => (
          <button key={key} onClick={() => setActiveTab(key)}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all ${
              activeTab === key
                ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'}`}>
            {icon}{label}
          </button>
        ))}
      </div>

      {/* ════════════ GENERATE MODULE TAB ════════════ */}
      {activeTab === 'generate' && (
        <div className="glass-card p-8">
          {/* Sub-tab bar */}
          <div className="flex gap-1 mb-7 p-1 bg-slate-100 dark:bg-slate-800 rounded-lg w-fit">
            {[
              { key: 'pdf',    label: 'Via PDF',         icon: <UploadCloud size={15} /> },
              { key: 'manual', label: 'Enter Manually',  icon: <PenLine size={15} />     },
            ].map(({ key, label, icon }) => (
              <button key={key} onClick={() => setGenTab(key)}
                className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                  genTab === key
                    ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm'
                    : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'}`}>
                {icon}{label}
              </button>
            ))}
          </div>

          {/* ── Via PDF ── */}
          {genTab === 'pdf' && (
            <div>
              <div className="flex items-center mb-6">
                <FileUp className="text-blue-600 mr-3" size={26} />
                <div>
                  <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100">Generate Module from PDF</h2>
                  <p className="text-slate-500 dark:text-slate-400 text-sm mt-0.5">
                    Upload an educational PDF chapter — NLP will auto-create MCQ, True/False and Fill-in-blank questions.
                  </p>
                </div>
              </div>

              {!questions ? (
                <form onSubmit={handlePdfGenerate} className="space-y-5">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Module Name</label>
                      <input type="text" value={moduleName} onChange={e => setModuleName(e.target.value)}
                        placeholder="e.g., Python Basics – Chapter 3" className="input-field w-full" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Difficulty Level</label>
                      <select value={moduleLevel} onChange={e => setModuleLevel(e.target.value)} className="input-field w-full">
                        <option value="beginner">Beginner</option>
                        <option value="intermediate">Intermediate</option>
                        <option value="expert">Expert</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                      Number of Questions: <span className="text-blue-600 font-bold">{numQuestions}</span>
                    </label>
                    <input type="range" min={5} max={30} value={numQuestions}
                      onChange={e => setNumQuestions(Number(e.target.value))} className="w-full accent-blue-600" />
                    <div className="flex justify-between text-xs text-slate-400 mt-0.5"><span>5</span><span>30</span></div>
                  </div>

                  <div className="border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-xl p-8 text-center
                    bg-slate-50/50 dark:bg-slate-900/50 hover:border-blue-400 dark:hover:border-blue-600 transition-colors">
                    <input type="file" accept=".pdf" id="pdf-upload" className="hidden"
                      onChange={e => setPdfFile(e.target.files[0])} />
                    <label htmlFor="pdf-upload" className="cursor-pointer">
                      <UploadCloud className="mx-auto mb-3 text-slate-400" size={44} />
                      <p className="text-base font-medium text-slate-700 dark:text-slate-300">
                        {pdfFile ? pdfFile.name : 'Click to choose a PDF file'}
                      </p>
                      <p className="text-xs text-slate-400 mt-1">Text-based PDFs work best. Scanned images won't extract text.</p>
                    </label>
                  </div>

                  {uploadError && (
                    <div className="flex items-start gap-2 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm">
                      <AlertCircle size={16} className="mt-0.5 shrink-0" />{uploadError}
                    </div>
                  )}

                  <button type="submit" disabled={uploading || !pdfFile} className="btn-primary w-full flex items-center justify-center gap-2">
                    {uploading ? <><RefreshCw size={16} className="animate-spin" /> Analysing PDF…</> : <><FileUp size={16} /> Generate Questions</>}
                  </button>
                </form>
              ) : (
                <div>
                  <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
                    <div>
                      <span className="font-semibold text-slate-700 dark:text-slate-200">{questions.length} questions generated</span>
                      <span className="ml-2 text-sm text-slate-400">– edit or remove any before saving</span>
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => { setQuestions(null); setUploadError(''); }}
                        className="flex items-center gap-1 px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700">
                        <RefreshCw size={14} /> Start Over
                      </button>
                      <button onClick={handleSavePdf} disabled={saving || questions.length === 0}
                        className="btn-primary flex items-center gap-2 px-5 py-2 text-sm">
                        {saving ? <><RefreshCw size={14} className="animate-spin" /> Saving…</> : <><Save size={14} /> Save Module</>}
                      </button>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {Object.entries(TYPE_META).map(([key, m]) => (
                      <span key={key} className={`text-xs px-2 py-0.5 rounded-full font-medium ${m.color}`}>
                        {m.label}: {questions.filter(q => q.type === key).length}
                      </span>
                    ))}
                  </div>
                  <div className="max-h-[60vh] overflow-y-auto pr-1">
                    {questions.map((q, i) => (
                      <QuestionCard key={i} q={q} index={i} onEdit={handlePdfEdit} onDelete={handlePdfDelete} />
                    ))}
                  </div>
                  {saveResult && (
                    <div className={`flex items-center gap-2 p-3 mt-4 rounded-lg text-sm ${
                      saveResult.success ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400' : 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400'}`}>
                      {saveResult.success ? <CheckCircle size={16} /> : <AlertCircle size={16} />}{saveResult.message}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* ── Enter Manually ── */}
          {genTab === 'manual' && (
            <div>
              <div className="flex items-center mb-6">
                <PenLine className="text-blue-600 mr-3" size={26} />
                <div>
                  <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100">Build Module Manually</h2>
                  <p className="text-slate-500 dark:text-slate-400 text-sm mt-0.5">
                    Compose each question by hand — choose the type, fill in the details, then save as a module.
                  </p>
                </div>
              </div>

              {/* Module meta */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Module Name</label>
                  <input type="text" value={manualName} onChange={e => setManualName(e.target.value)}
                    placeholder="e.g., Data Structures Quiz" className="input-field w-full" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Difficulty Level</label>
                  <select value={manualLevel} onChange={e => setManualLevel(e.target.value)} className="input-field w-full">
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="expert">Expert</option>
                  </select>
                </div>
              </div>

              {/* Add question form */}
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Add a Question</h3>
                <ManualQuestionForm onAdd={handleAddManualQ} />
              </div>

              {/* Preview */}
              {manualQuestions.length > 0 && (
                <div>
                  <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                    <div>
                      <span className="font-semibold text-slate-700 dark:text-slate-200">{manualQuestions.length} question{manualQuestions.length !== 1 ? 's' : ''} added</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(TYPE_META).map(([key, m]) => (
                        <span key={key} className={`text-xs px-2 py-0.5 rounded-full font-medium ${m.color}`}>
                          {m.label}: {manualQuestions.filter(q => q.type === key).length}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="max-h-[50vh] overflow-y-auto pr-1 mb-4">
                    {manualQuestions.map((q, i) => (
                      <QuestionCard key={i} q={q} index={i} onEdit={handleEditManual} onDelete={handleDeleteManual} />
                    ))}
                  </div>
                  <button onClick={handleSaveManual} disabled={manualSaving}
                    className="btn-primary flex items-center gap-2 px-5 py-2 text-sm">
                    {manualSaving ? <><RefreshCw size={14} className="animate-spin" /> Saving…</> : <><Save size={14} /> Save Module</>}
                  </button>
                  {manualSaveResult && (
                    <div className={`flex items-center gap-2 p-3 mt-4 rounded-lg text-sm ${
                      manualSaveResult.success ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400' : 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400'}`}>
                      {manualSaveResult.success ? <CheckCircle size={16} /> : <AlertCircle size={16} />}{manualSaveResult.message}
                    </div>
                  )}
                </div>
              )}

              {manualQuestions.length === 0 && (
                <div className="text-center py-10 text-slate-400 dark:text-slate-500 border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-xl">
                  <PenLine size={36} className="mx-auto mb-3 opacity-30" />
                  <p className="text-sm">Fill the form above and click <strong>Add Question</strong> to start building your module.</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ════════════ MANAGE CHALLENGES TAB ════════════ */}
      {activeTab === 'challenges' && (
        <div className="space-y-8">

          {/* ── Add Challenge form ── */}
          <div className="glass-card p-8">
            <div className="flex items-center mb-6">
              <Plus className="text-purple-600 mr-3" size={26} />
              <div>
                <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100">Add Challenge</h2>
                <p className="text-slate-500 dark:text-slate-400 text-sm mt-0.5">
                  Manually enter a new daily challenge. Title format: <code className="text-xs bg-slate-100 dark:bg-slate-700 px-1 rounded">Day N: Short Title</code>
                </p>
              </div>
            </div>

            <form onSubmit={handleAddChallenge} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Title</label>
                  <input type="text" value={addForm.title}
                    onChange={e => setAddForm(p => ({ ...p, title: e.target.value }))}
                    placeholder="Day 3: Reverse String" className="input-field w-full" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Category</label>
                  <select value={addForm.category}
                    onChange={e => setAddForm(p => ({ ...p, category: e.target.value }))}
                    className="input-field w-full">
                    {CATEGORIES.map(c => <option key={c}>{c}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Question</label>
                <textarea rows={2} value={addForm.question}
                  onChange={e => setAddForm(p => ({ ...p, question: e.target.value }))}
                  placeholder="What is the output of print('hello'[::-1])?"
                  className="input-field w-full resize-none" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Answer</label>
                <input type="text" value={addForm.answer}
                  onChange={e => setAddForm(p => ({ ...p, answer: e.target.value }))}
                  placeholder="olleh" className="input-field w-full" />
              </div>

              {addResult && (
                <div className={`flex items-center gap-2 p-3 rounded-lg text-sm ${
                  addResult.success ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400' : 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400'}`}>
                  {addResult.success ? <CheckCircle size={16} /> : <AlertCircle size={16} />}{addResult.message}
                </div>
              )}

              <button type="submit" disabled={addSaving || !addForm.title.trim() || !addForm.question.trim() || !addForm.answer.trim()}
                className="btn-primary flex items-center gap-2 px-5 py-2 text-sm bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800">
                {addSaving ? <><RefreshCw size={14} className="animate-spin" /> Saving…</> : <><Plus size={15} /> Add Challenge</>}
              </button>
            </form>
          </div>

          {/* ── Challenges table ── */}
          <div className="glass-card p-8">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center">
                <Calendar className="text-blue-600 mr-3" size={26} />
                <div>
                  <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100">All Day Challenges</h2>
                  <p className="text-slate-500 dark:text-slate-400 text-sm mt-0.5">
                    {challenges.length} challenge{challenges.length !== 1 ? 's' : ''} across all days — click <Edit2 size={12} className="inline" /> to edit any row.
                  </p>
                  <p className="text-slate-400 dark:text-slate-500 text-xs mt-1">
                    Toggle the <span className="font-semibold text-green-600 dark:text-green-400">Active</span> switch to control which challenges students can see. Dimmed rows are hidden from students.
                  </p>
                </div>
              </div>
              <button onClick={loadChallenges} disabled={challengesLoading}
                className="flex items-center gap-2 px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                <RefreshCw size={14} className={challengesLoading ? 'animate-spin' : ''} /> Refresh
              </button>
            </div>

            {challengesError && (
              <div className="flex items-start gap-2 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm mb-4">
                <AlertCircle size={16} className="mt-0.5 shrink-0" />{challengesError}
              </div>
            )}

            {challengesLoading ? (
              <div className="flex items-center justify-center py-16 text-slate-400">
                <RefreshCw size={24} className="animate-spin mr-3" /> Loading challenges…
              </div>
            ) : (
              <ChallengesTable
                challenges={challenges}
                onUpdated={handleChallengeUpdated}
                onDeleted={handleChallengeDeleted}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default MentorTools;
