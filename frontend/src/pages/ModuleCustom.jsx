import React, { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

export default function ModuleCustom() {
  const { moduleId } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState({ loading: true, error: "" });
  const [moduleData, setModuleData] = useState(null);
  const [index, setIndex] = useState(0);
  const [input, setInput] = useState("");
  const [message, setMessage] = useState("");
  const [wasCorrect, setWasCorrect] = useState(null);

  useEffect(() => {
    let active = true;
    async function load() {
      setStatus({ loading: true, error: "" });
      try {
        const { data } = await api.getCustomModuleItems(moduleId);
        if (!active) return;
        setModuleData(data);
        setIndex(0);
        setInput("");
        setMessage("");
        setWasCorrect(null);
        setStatus({ loading: false, error: "" });
      } catch (e) {
        if (!active) return;
        setStatus({
          loading: false,
          error: e?.response?.data?.detail || "Failed to load custom module",
        });
      }
    }
    load();
    return () => {
      active = false;
    };
  }, [moduleId]);

  const questions = useMemo(() => moduleData?.questions || [], [moduleData]);
  const current = questions[index] || null;

  const submit = async () => {
    if (!current) return;
    try {
      const res = await api.submitCustomModuleAnswer(moduleId, { id: current.id, answer: input });
      const ok = !!res?.data?.success;
      setWasCorrect(ok);
      setMessage(res?.data?.message || (ok ? "Correct" : "Incorrect"));
      if (ok) {
        setModuleData((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            questions: (prev.questions || []).map((q) =>
              q.id === current.id ? { ...q, completed: true } : q
            ),
          };
        });
      }
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.response?.data?.message || "Submission failed";
      setWasCorrect(false);
      setMessage(msg);
    }
  };

  const next = () => {
    if (index >= questions.length - 1) {
      navigate("/modules");
      return;
    }
    setIndex((v) => v + 1);
    setInput("");
    setMessage("");
    setWasCorrect(null);
  };

  const prev = () => {
    setIndex((v) => Math.max(0, v - 1));
    setInput("");
    setMessage("");
    setWasCorrect(null);
  };

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl md:text-4xl font-extrabold text-slate-800 dark:text-slate-100">
          {moduleData?.name || "Custom Module"}
        </h1>
        <Link to="/modules" className="btn-secondary">Back to Modules</Link>
      </div>

      {moduleData && (
        <div className="mb-6 text-sm text-slate-500 dark:text-slate-400">
          <span className="mr-4">Level: {moduleData.level}</span>
          <span>Questions: {questions.length}</span>
        </div>
      )}

      {!status.loading && !status.error && questions.length > 0 && (
        <div className="max-w-3xl mx-auto mb-6 flex flex-wrap gap-2 justify-center">
          {questions.map((q, i) => {
            const isActive = i === index;
            const isDone = !!q.completed;
            return (
              <button
                key={q.id}
                onClick={() => { setIndex(i); setInput(""); setMessage(""); setWasCorrect(null); }}
                className={`px-3 py-1 rounded-full text-sm transition-all duration-300 focus:outline-none
                  ${isActive ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg scale-105' : 'bg-white/70 dark:bg-slate-800/70 text-slate-700 dark:text-slate-200 border border-slate-200/50 dark:border-slate-700/50 hover:scale-105'}
                  ${isDone ? 'ring-2 ring-green-400/70 dark:ring-green-500/50' : 'ring-0'}`}
                title={isDone ? 'Completed' : 'Not completed'}
              >
                {i + 1}
              </button>
            );
          })}
        </div>
      )}

      {status.loading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-10 w-10 border-b-2 border-purple-600"></div>
          <p className="text-slate-500 dark:text-slate-400 mt-3">Loading...</p>
        </div>
      )}

      {!status.loading && status.error && (
        <div className="glass-card p-4 text-red-600 dark:text-red-400">{status.error}</div>
      )}

      {!status.loading && !status.error && current && (
        <div className="max-w-2xl mx-auto module-card">
          <div className="text-sm text-slate-500 dark:text-slate-400">Question {index + 1} of {questions.length}</div>
          <div className="mt-3 text-lg text-slate-800 dark:text-slate-100">{current.question}</div>

          {(current.type === "mcq" || current.type === "true_false") && Array.isArray(current.options) && current.options.length > 0 && (
            <div className="mt-4 space-y-2">
              {current.options.map((opt, i) => (
                <button
                  key={`${i}-${opt}`}
                  onClick={() => setInput(opt)}
                  className={`w-full text-left px-3 py-2 rounded-lg border transition-colors ${
                    input === opt
                      ? "border-purple-500 bg-purple-50 dark:bg-purple-900/20"
                      : "border-slate-300 dark:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-800"
                  }`}
                >
                  {opt}
                </button>
              ))}
            </div>
          )}

          {(current.type === "fill_blank" || !Array.isArray(current.options) || current.options.length === 0) && (
            <div className="mt-4">
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-200">Your Answer</label>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className="mt-1 w-full rounded-md border border-slate-300 dark:border-slate-600 bg-white/70 dark:bg-slate-800/70 p-2 focus:outline-none focus:ring-2 focus:ring-purple-600"
                placeholder="Type your answer"
              />
            </div>
          )}

          <div className="mt-4 flex items-center gap-3">
            <button onClick={submit} className="btn-primary" disabled={!input.trim()}>Submit</button>
            {message && (
              <div className={`text-sm ${wasCorrect === true ? "text-green-600 dark:text-green-400" : wasCorrect === false ? "text-red-600 dark:text-red-400" : "text-slate-700 dark:text-slate-200"}`}>
                {message}
              </div>
            )}
          </div>

          {current.explanation && (
            <details className="mt-4">
              <summary className="cursor-pointer text-slate-600 dark:text-slate-300">Show explanation</summary>
              <div className="mt-2 text-slate-700 dark:text-slate-200">{current.explanation}</div>
            </details>
          )}

          <div className="mt-6 flex items-center justify-between">
            <button className="btn-secondary" onClick={prev} disabled={index === 0}>Previous</button>
            <button className="btn-primary" onClick={next}>{index < questions.length - 1 ? "Next" : "Finish"}</button>
          </div>
        </div>
      )}

      {!status.loading && !status.error && !current && (
        <div className="glass-card p-6 text-center max-w-xl mx-auto">
          <div className="text-lg">No questions in this module.</div>
          <Link to="/modules" className="btn-primary mt-4 inline-block">Back to modules</Link>
        </div>
      )}
    </div>
  );
}
