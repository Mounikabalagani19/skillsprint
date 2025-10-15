import React, { useState } from "react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext.jsx";

const ChallengeCard = ({ challenge }) => {
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [error, setError] = useState(null);
  const { isAuthenticated } = useAuth();
  const [submitting, setSubmitting] = useState(false);
  const [completed, setCompleted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFeedback(null);
    setError(null);

    if (!isAuthenticated) {
      setError("You must be logged in to submit an answer.");
      return;
    }

    try {
      setSubmitting(true);
      const response = await api.submitAnswer(challenge.id, answer);
      setFeedback(response.data.message);
      // Mark as completed on success
      setCompleted(true);
    } catch (err) {
        if (err.response && err.response.data) {
          // Server may return validation errors as objects; stringify safely
          const data = err.response.data;
          let message = "Incorrect answer. Try again!";
          if (typeof data === 'string') {
            message = data;
          } else if (data.detail) {
            // detail can be a string or list/dict from FastAPI
            if (typeof data.detail === 'string') message = data.detail;
            else message = JSON.stringify(data.detail);
          } else {
            // fallback: stringify whole response body but limit length
            try {
              message = JSON.stringify(data);
              if (message.length > 500) message = message.slice(0, 500) + '...';
            } catch (e) {
              message = 'An unexpected error occurred. Please try again.';
            }
          }
          setError(message);
        } else {
          setError("An unexpected error occurred. Please try again.");
        }
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  // compute dayLabel and displayTitle so we don't show "Day N:" twice
  let dayLabel = null;
  let displayTitle = challenge.title || '';
  if (challenge) {
    if (challenge.day) {
      dayLabel = `Day ${challenge.day}`;
    } else if (challenge.title) {
      const m = challenge.title.match(/Day\s*(\d+)/i);
      if (m) {
        dayLabel = `Day ${m[1]}`;
        // strip the leading "Day N:" or "Day N -" from the title for display
        displayTitle = challenge.title.replace(/^Day\s*\d+\s*[:\-–—]?\s*/i, '');
      }
    }
  }

  return (
    <div className={`challenge-card ${completed ? 'ring-2 ring-green-400/60' : ''}`}>
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100">{displayTitle}</h3>
        </div>

        <div className="badge-stack ml-4 flex flex-col items-end">
          {(() => {
            let dayLabel = null;
            if (challenge) {
              if (challenge.day) {
                dayLabel = `Day ${challenge.day}`;
              } else if (challenge.title) {
                const m = challenge.title.match(/Day\s*(\d+)/i);
                if (m) dayLabel = `Day ${m[1]}`;
              }
            }
            return dayLabel ? (
              <span className="day-badge mb-2" aria-hidden>
                {dayLabel}
              </span>
            ) : null;
          })()}

          <span className="category-badge">
            {challenge.category}
          </span>
        </div>
      </div>
      <p className="text-slate-600 dark:text-slate-300 mb-6 flex-grow leading-relaxed">{challenge.question}</p>
      
      {isAuthenticated ? (
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Type your answer here"
            className="input-field"
            required
            disabled={completed || submitting}
          />
          <button
            type="submit"
            className={`btn-primary w-full ${completed ? 'opacity-70 cursor-not-allowed' : ''}`}
            disabled={completed || submitting}
          >
            {completed ? 'Completed ✓' : (submitting ? 'Submitting…' : 'Submit Answer')}
          </button>
        </form>
      ) : (
        <div className="space-y-3">
          <input
            type="text"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Login to answer"
            className="input-field"
            disabled
          />
          <a href="/login" className="btn-secondary w-full inline-flex justify-center">Log in to submit</a>
        </div>
      )}

      {/* Feedback Section */}
      {feedback && (
        <div className="mt-4 p-4 text-center bg-gradient-to-r from-green-100 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30 text-green-800 dark:text-green-300 rounded-xl border border-green-200 dark:border-green-700/30 backdrop-blur-sm">
          {feedback}
        </div>
      )}
      {error && (
        <div className="mt-4 p-4 text-center bg-gradient-to-r from-red-100 to-pink-100 dark:from-red-900/30 dark:to-pink-900/30 text-red-800 dark:text-red-300 rounded-xl border border-red-200 dark:border-red-700/30 backdrop-blur-sm">
          {error}
        </div>
      )}
    </div>
  );
};

export default ChallengeCard;

