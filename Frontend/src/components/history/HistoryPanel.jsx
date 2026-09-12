import { useEffect, useMemo, useState } from "react";

import { clearHistory, deleteHistoryItem, getHistory, getHistoryItem } from "../../services/geometryApi";

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

function groupFor(value) {
  const date = new Date(value);
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);
  if (date.toDateString() === today.toDateString()) return "Today";
  if (date.toDateString() === yesterday.toDateString()) return "Yesterday";
  return "Older";
}

export function HistoryPanel({ onRestore }) {
  const [items, setItems] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadHistory(nextQuery = query) {
    setLoading(true);
    setError("");
    try {
      setItems(await getHistory(nextQuery));
    } catch (requestError) {
      setError(requestError.message || "History could not be loaded.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadHistory("");
  }, []);

  const grouped = useMemo(() => {
    return items.reduce((groups, item) => {
      const group = groupFor(item.created_at);
      groups[group] = groups[group] || [];
      groups[group].push(item);
      return groups;
    }, {});
  }, [items]);

  async function handleOpen(item) {
    setError("");
    try {
      const detail = await getHistoryItem(item.id);
      onRestore(detail.response);
    } catch (requestError) {
      setError(requestError.message || "That saved solution could not be opened.");
    }
  }

  async function handleDelete(item) {
    setError("");
    try {
      await deleteHistoryItem(item.id);
      setItems((current) => current.filter((candidate) => candidate.id !== item.id));
    } catch (requestError) {
      setError(requestError.message || "That history item could not be deleted.");
    }
  }

  async function handleClear() {
    if (!items.length || !window.confirm("Clear all solved-problem history?")) return;
    setError("");
    try {
      await clearHistory();
      setItems([]);
    } catch (requestError) {
      setError(requestError.message || "History could not be cleared.");
    }
  }

  return (
    <section className="panel-page" aria-labelledby="history-title">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Saved work</p>
          <h1 id="history-title">History</h1>
        </div>
        <button className="secondary-button" type="button" onClick={handleClear} disabled={!items.length}>
          Clear
        </button>
      </div>

      <form className="search-row" onSubmit={(event) => { event.preventDefault(); loadHistory(query); }}>
        <label className="sr-only" htmlFor="history-search">Search history</label>
        <input id="history-search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search solved problems" />
        <button type="submit">Search</button>
      </form>

      {loading && <p className="panel-state">Loading history...</p>}
      {error && <p className="panel-error" role="alert">{error}</p>}
      {!loading && !error && items.length === 0 && (
        <div className="empty-state">
          <h2>No solved problems yet.</h2>
          <p>Your completed geometry problems will appear here.</p>
        </div>
      )}

      {!loading && items.length > 0 && (
        <div className="history-groups">
          {["Today", "Yesterday", "Older"].filter((group) => grouped[group]?.length).map((group) => (
            <section key={group} className="history-group" aria-label={group}>
              <h2>{group}</h2>
              <div className="history-list">
                {grouped[group].map((item) => (
                  <article className="history-item" key={item.id}>
                    <button type="button" className="history-open" onClick={() => handleOpen(item)}>
                      <span>{item.question}</span>
                      <small>{item.operation_label || item.operation} / {item.dimension || "2d"} / {formatDate(item.created_at)}</small>
                    </button>
                    <button className="icon-button" type="button" aria-label={`Delete history item ${item.id}`} onClick={() => handleDelete(item)}>
                      Delete
                    </button>
                  </article>
                ))}
              </div>
            </section>
          ))}
        </div>
      )}
    </section>
  );
}
