// v2.1.0 - Hard refresh forced
import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import api from "../services/api";

export default function Modules() {
  const { isAuthenticated, user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [favourites, setFavourites] = useState([]);
  const [customModules, setCustomModules] = useState([]);
  const [customLoading, setCustomLoading] = useState(false);
  const [customError, setCustomError] = useState("");

  useEffect(() => {
    if (!authLoading && user) {
      const role = user.role?.toLowerCase();
      if (role === 'admin') {
        navigate('/admin');
      } else if (role === 'mentor') {
        navigate('/mentor');
      }
    }
  }, [user, authLoading, navigate]);

  if (authLoading && user) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  useEffect(() => {
    try {
      const raw = localStorage.getItem("favouriteModules");
      setFavourites(raw ? JSON.parse(raw) : []);
    } catch (e) {
      setFavourites([]);
    }
  }, []);

  useEffect(() => {
    if (!isAuthenticated || !user || user.role?.toLowerCase() !== 'student') return;

    let active = true;
    async function loadCustomModules() {
      setCustomLoading(true);
      setCustomError("");
      try {
        const { data } = await api.listCustomModules();
        if (!active) return;
        setCustomModules(Array.isArray(data) ? data : []);
      } catch (e) {
        if (!active) return;
        setCustomError(e?.response?.data?.detail || "Failed to load custom modules");
      } finally {
        if (active) setCustomLoading(false);
      }
    }

    loadCustomModules();
    return () => { active = false; };
  }, [isAuthenticated, user]);

  const levelOrder = { beginner: 1, intermediate: 2, expert: 3 };
  const groupedCustomModules = customModules.reduce((acc, mod) => {
    const name = (mod?.name || 'Custom Module').trim();
    const key = name.toLowerCase();
    if (!acc[key]) {
      acc[key] = { name, byLevel: {} };
    }

    const lvl = (mod?.level || 'beginner').toLowerCase();
    const existing = acc[key].byLevel[lvl];
    if (!existing) {
      acc[key].byLevel[lvl] = mod;
    } else {
      const existingTime = new Date(existing.created_at || 0).getTime();
      const incomingTime = new Date(mod.created_at || 0).getTime();
      if (incomingTime >= existingTime) {
        acc[key].byLevel[lvl] = mod;
      }
    }
    return acc;
  }, {});

  const customCards = Object.values(groupedCustomModules)
    .map((group) => ({
      ...group,
      levels: Object.values(group.byLevel).sort((a, b) => {
        const ax = levelOrder[(a.level || '').toLowerCase()] || 999;
        const bx = levelOrder[(b.level || '').toLowerCase()] || 999;
        return ax - bx;
      }),
    }))
    .sort((a, b) => a.name.localeCompare(b.name));

  const toggleFavourite = (slug) => {
    setFavourites((prev) => {
      const next = prev.includes(slug) ? prev.filter((s) => s !== slug) : [...prev, slug];
      try {
        localStorage.setItem("favouriteModules", JSON.stringify(next));
      } catch (e) {
        // ignore localStorage errors
      }
      return next;
    });
  };

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-extrabold text-slate-800 dark:text-slate-100">Modules</h1>
        <p className="text-slate-600 dark:text-slate-300 mt-3 max-w-2xl mx-auto">
          Choose a module to practice anytime. Earn 5 XP and +1 streak per correct answer. Wrong answers use the same rules as the daily quiz.
        </p>
      </div>

      {!isAuthenticated && (
        <div className="glass-card p-4 text-center max-w-2xl mx-auto mb-8">
          <p className="text-slate-700 dark:text-slate-200">
            Please log in to access module quizzes.
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
        <div className="module-card flex flex-col relative">
          <button
            aria-label="Toggle favourite Python"
            onClick={() => toggleFavourite('python')}
            className={`absolute right-4 top-4 w-9 h-9 inline-flex items-center justify-center rounded-full transition-shadow shadow-sm border ${favourites.includes('python') ? 'text-rose-500 bg-rose-50/30 border-rose-100/30' : 'text-slate-300 bg-slate-800/40 border-white/5 hover:text-rose-500 hover:bg-rose-50/8'}`}
            title={favourites.includes('python') ? 'Unfavourite' : 'Favourite'}
          >
            {/* Symmetric heart icon (Heroicons-style) with a 1px upward nudge for visual centering */}
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4" style={{ transform: 'translateY(-1px)' }}>
              <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L12 8.343l3.172-3.171a4 4 0 115.656 5.656L12 21.657 3.172 10.828a4 4 0 010-5.656z" clipRule="evenodd" />
            </svg>
          </button>
          <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Python</h2>
          <p className="text-slate-600 dark:text-slate-300 mt-2 flex-grow">Programming Skills Quiz: Beginner, Intermediate, and Expert difficulties.</p>
          <Link
            to={`/modules/python`}
            className={`btn-primary mt-6 ${!isAuthenticated ? 'pointer-events-none opacity-60' : ''}`}
            aria-disabled={!isAuthenticated}
          >
            Choose Difficulty
          </Link>
        </div>
        <div className="module-card flex flex-col relative">
          <button
            aria-label="Toggle favourite Java"
            onClick={() => toggleFavourite('java')}
            className={`absolute right-4 top-4 w-9 h-9 inline-flex items-center justify-center rounded-full transition-shadow shadow-sm border ${favourites.includes('java') ? 'text-rose-500 bg-rose-50/30 border-rose-100/30' : 'text-slate-300 bg-slate-800/40 border-white/5 hover:text-rose-500 hover:bg-rose-50/8'}`}
            title={favourites.includes('java') ? 'Unfavourite' : 'Favourite'}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4" style={{ transform: 'translateY(-1px)' }}>
              <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L12 8.343l3.172-3.171a4 4 0 115.656 5.656L12 21.657 3.172 10.828a4 4 0 010-5.656z" clipRule="evenodd" />
            </svg>
          </button>
          <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Java</h2>
          <p className="text-slate-600 dark:text-slate-300 mt-2 flex-grow">Programming Skills Quiz: Beginner, Intermediate, and Expert difficulties.</p>
          <Link
            to={`/modules/java`}
            className={`btn-primary mt-6 ${!isAuthenticated ? 'pointer-events-none opacity-60' : ''}`}
            aria-disabled={!isAuthenticated}
          >
            Choose Difficulty
          </Link>
        </div>
      </div>

      <div className="max-w-5xl mx-auto mt-12">
        <div className="mb-4">
          <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Custom Modules</h2>
          <p className="text-slate-600 dark:text-slate-300 mt-1">
            Mentor-created modules. If a module has multiple difficulty versions, each level appears separately.
          </p>
        </div>

        {customLoading && (
          <div className="glass-card p-4 text-slate-600 dark:text-slate-300">Loading custom modules...</div>
        )}

        {!customLoading && customError && (
          <div className="glass-card p-4 text-red-600 dark:text-red-400">{customError}</div>
        )}

        {!customLoading && !customError && customCards.length === 0 && (
          <div className="glass-card p-4 text-slate-600 dark:text-slate-300">No custom modules published yet.</div>
        )}

        {!customLoading && !customError && customCards.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {customCards.map((group) => (
              <div key={group.name} className="module-card">
                <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100">{group.name}</h3>
                <p className="text-slate-600 dark:text-slate-300 mt-2">
                  Available levels: {group.levels.map((m) => m.level).join(', ')}
                </p>
                <div className="flex flex-wrap gap-2 mt-4">
                  {group.levels.map((m) => (
                    <Link
                      key={`${m.id}-${m.level}`}
                      to={`/modules/custom/${m.id}`}
                      className="btn-primary"
                    >
                      {`${(m.level || 'beginner').charAt(0).toUpperCase()}${(m.level || 'beginner').slice(1)}`}
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
