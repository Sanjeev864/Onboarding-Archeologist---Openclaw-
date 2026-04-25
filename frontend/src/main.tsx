import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { AlertTriangle, Brain, GitBranch, Search, ShieldAlert, Sparkles, UserRoundSearch } from "lucide-react";
import { Analysis, OracleAnswer, analyze, askOracle } from "./lib/api";
import "./styles.css";

function App() {
  const [owner, setOwner] = useState("facebook");
  const [repo, setRepo] = useState("react");
  const [branch, setBranch] = useState("");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [question, setQuestion] = useState("Why were major architectural changes made?");
  const [answer, setAnswer] = useState<OracleAnswer | null>(null);

  const stats = useMemo(() => {
    if (!analysis) return null;
    const highRisk = analysis.ownership.filter((item) => item.risk === "high").length;
    return {
      decisions: analysis.decisions.length,
      ghost: analysis.ghost_code.length,
      owners: analysis.ownership.length,
      highRisk,
    };
  }, [analysis]);

  async function runAnalysis(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setAnswer(null);
    try {
      setAnalysis(await analyze(owner.trim(), repo.trim(), branch.trim()));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  }

  async function runQuestion(event: React.FormEvent) {
    event.preventDefault();
    if (!analysis) return;
    setError("");
    try {
      setAnswer(await askOracle(analysis.repository_id, question));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Oracle request failed");
    }
  }

  return (
    <main>
      <aside>
        <div className="brand">
          <Brain size={28} />
          <div>
            <h1>Onboarding Archaeologist</h1>
            <p>Evidence-backed codebase intelligence</p>
          </div>
        </div>

        <form onSubmit={runAnalysis} className="panel">
          <label>
            Owner
            <input value={owner} onChange={(event) => setOwner(event.target.value)} />
          </label>
          <label>
            Repository
            <input value={repo} onChange={(event) => setRepo(event.target.value)} />
          </label>
          <label>
            Branch
            <input placeholder="default branch" value={branch} onChange={(event) => setBranch(event.target.value)} />
          </label>
          <button disabled={loading || !owner || !repo}>
            <Search size={18} />
            {loading ? "Analyzing..." : "Start Analysis"}
          </button>
        </form>

        {error && <div className="error">{error}</div>}

        <section className="panel compact">
          <h2>Analysis Window</h2>
          <p>Reads the latest 200 commits and stores decision, ownership, and ghost-code signals locally.</p>
        </section>
      </aside>

      <section className="workspace">
        {analysis && stats ? (
          <>
            <header className="workspaceHeader">
              <div>
                <p className="eyebrow">Repository</p>
                <h2>{analysis.owner}/{analysis.repo}</h2>
              </div>
              <span>{new Date(analysis.analyzed_at).toLocaleString()}</span>
            </header>

            <div className="metrics">
              <Metric icon={<GitBranch />} label="Decision Signals" value={stats.decisions} />
              <Metric icon={<ShieldAlert />} label="Ghost Candidates" value={stats.ghost} />
              <Metric icon={<UserRoundSearch />} label="Ownership Paths" value={stats.owners} />
              <Metric icon={<AlertTriangle />} label="High Bus Risk" value={stats.highRisk} />
            </div>

            <div className="grid">
              <section className="surface wide">
                <h3>Decision Excavation</h3>
                <div className="list">
                  {analysis.decisions.map((item) => (
                    <article key={item.commit_sha}>
                      <div className="row">
                        <strong>{item.title}</strong>
                        <Confidence value={item.confidence} />
                      </div>
                      <p>{item.summary}</p>
                      <small>{item.evidence}</small>
                    </article>
                  ))}
                  {analysis.decisions.length === 0 && <Empty text="No explicit decision language found in the latest commits." />}
                </div>
              </section>

              <section className="surface">
                <h3>Knowledge Ownership</h3>
                <div className="list tight">
                  {analysis.ownership.slice(0, 12).map((item) => (
                    <article key={`${item.path}-${item.author}`}>
                      <div className="row">
                        <strong>{item.path}</strong>
                        <Risk risk={item.risk} />
                      </div>
                      <p>{item.author} owns {item.commits} recent commits</p>
                    </article>
                  ))}
                </div>
              </section>

              <section className="surface">
                <h3>Ghost Code</h3>
                <div className="list tight">
                  {analysis.ghost_code.slice(0, 12).map((item) => (
                    <article key={item.path}>
                      <div className="row">
                        <strong>{item.path}</strong>
                        <Confidence value={item.confidence} />
                      </div>
                      <p>{item.reason}. Last touched {item.last_touched_days} days ago.</p>
                    </article>
                  ))}
                  {analysis.ghost_code.length === 0 && <Empty text="No stale or legacy markers found in this analysis window." />}
                </div>
              </section>

              <section className="surface wide">
                <h3>Oracle</h3>
                <form onSubmit={runQuestion} className="oracle">
                  <input value={question} onChange={(event) => setQuestion(event.target.value)} />
                  <button>
                    <Sparkles size={18} />
                    Ask
                  </button>
                </form>
                {answer && (
                  <div className="answer">
                    <p>{answer.answer}</p>
                    <h4>Evidence</h4>
                    {answer.evidence.map((item) => <small key={item}>{item}</small>)}
                  </div>
                )}
              </section>
            </div>
          </>
        ) : (
          <section className="emptyState">
            <Brain size={56} />
            <h2>Analyze a GitHub repository to reconstruct its recent history.</h2>
            <p>Start with a public repository, then inspect the evidence the system extracts from commit history.</p>
          </section>
        )}
      </section>
    </main>
  );
}

function Metric({ icon, label, value }: { icon: React.ReactNode; label: string; value: number }) {
  return (
    <div className="metric">
      {icon}
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function Confidence({ value }: { value: number }) {
  return <span className="pill">{Math.round(value * 100)}%</span>;
}

function Risk({ risk }: { risk: "low" | "medium" | "high" }) {
  return <span className={`pill ${risk}`}>{risk}</span>;
}

function Empty({ text }: { text: string }) {
  return <p className="muted">{text}</p>;
}

createRoot(document.getElementById("root")!).render(<App />);
