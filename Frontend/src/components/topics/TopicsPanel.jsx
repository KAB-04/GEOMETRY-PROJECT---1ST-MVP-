import { useEffect, useMemo, useState } from "react";

import { getTopics } from "../../services/geometryApi";

const STATUS_LABELS = {
  available: "Available",
  partial: "Partial",
  experimental: "Experimental",
  coming_later: "Coming later",
};

export function TopicsPanel({ onUseExample }) {
  const [topics, setTopics] = useState([]);
  const [activeTopicId, setActiveTopicId] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadTopics() {
      try {
        const nextTopics = await getTopics();
        setTopics(nextTopics);
        setActiveTopicId(nextTopics[0]?.id || "");
      } catch (requestError) {
        setError(requestError.message || "Topics could not be loaded.");
      } finally {
        setLoading(false);
      }
    }
    loadTopics();
  }, []);

  const grouped = useMemo(() => {
    return topics.reduce((groups, topic) => {
      groups[topic.category] = groups[topic.category] || [];
      groups[topic.category].push(topic);
      return groups;
    }, {});
  }, [topics]);

  const activeTopic = topics.find((topic) => topic.id === activeTopicId);

  return (
    <section className="panel-page topics-page" aria-labelledby="topics-title">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Engine map</p>
          <h1 id="topics-title">Topics</h1>
        </div>
      </div>

      {loading && <p className="panel-state">Loading topics...</p>}
      {error && <p className="panel-error" role="alert">{error}</p>}

      {!loading && !error && (
        <div className="topics-layout">
          <div className="topic-list" aria-label="Topic list">
            {Object.entries(grouped).map(([category, entries]) => (
              <section key={category}>
                <h2>{category}</h2>
                {entries.map((topic) => (
                  <button
                    key={topic.id}
                    type="button"
                    className={`topic-pill ${topic.id === activeTopicId ? "active" : ""}`}
                    onClick={() => setActiveTopicId(topic.id)}
                  >
                    <span>{topic.name}</span>
                    <small>{STATUS_LABELS[topic.status] || topic.status}</small>
                  </button>
                ))}
              </section>
            ))}
          </div>

          {activeTopic && (
            <article className="topic-detail">
              <div className="topic-title-row">
                <div>
                  <span className="dimension-chip">{activeTopic.dimension}</span>
                  <h2>{activeTopic.name}</h2>
                </div>
                <span className={`status-badge status-${activeTopic.status}`}>{STATUS_LABELS[activeTopic.status] || activeTopic.status}</span>
              </div>
              <p>{activeTopic.description}</p>

              <div className="topic-section">
                <h3>Supported</h3>
                {activeTopic.supported_operations.length ? (
                  <ul>
                    {activeTopic.supported_operations.map((operation) => (
                      <li key={operation.operation}>{operation.label}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="muted-copy">Not exposed through the chatbot MVP yet.</p>
                )}
              </div>

              {activeTopic.examples.length > 0 && (
                <div className="topic-section">
                  <h3>Try</h3>
                  <div className="example-list compact">
                    {activeTopic.examples.map((example) => (
                      <button key={example} type="button" onClick={() => onUseExample(example)}>
                        {example}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </article>
          )}
        </div>
      )}
    </section>
  );
}
