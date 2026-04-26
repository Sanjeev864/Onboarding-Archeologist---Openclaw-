import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  AlertTriangle,
  Archive,
  Brain,
  ChevronRight,
  CircleHelp,
  Clock3,
  FileWarning,
  GitBranch,
  Layers3,
  Map,
  Network,
  Search,
  ShieldAlert,
  Sparkles,
  UserRoundSearch,
  Wrench,
} from "lucide-react";
import { Analysis, BusFactorAlert, Decision, GhostCode, OracleAnswer, Owner, ScarTissue, analyze, askOracle } from "./lib/api";
import "./styles.css";

type View = "overview" | "intelligence" | "onboarding" | "oracle";

function App() {
  const [owner, setOwner] = useState("facebook");
  const [repo, setRepo] = useState("react");
  const [branch, setBranch] = useState("");
  const [view, setView] = useState<View>("overview");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [question, setQuestion] = useState("Why were major architectural changes made?");
  const [answer, setAnswer] = useState<OracleAnswer | null>(null);

  const stats = useMemo(() => {
    if (!analysis) return null;
    const busRisk = analysis.bus_factor_alerts.filter((item) => item.risk_level !== "medium").length;
    const ownershipRisk = analysis.ownership.filter((item) => item.risk === "high").length;
    return {
      decisions: analysis.decisions.length,
      ghost: analysis.ghost_code.length,
      owners: analysis.ownership.length,
      risk: busRisk + ownershipRisk,
      scar: analysis.scar_tissue.length,
      days: analysis.onboarding_paths.length,
      coverage: Number(analysis.coverage_summary.coverage_percentage ?? 0),
      commits: Number(analysis.coverage_summary.total_commits_analyzed ?? 0),
    };
  }, [analysis]);

  async function runAnalysis(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setAnswer(null);
    try {
      const result = await analyze(owner.trim(), repo.trim(), branch.trim());
      setAnalysis(result);
      setView("overview");
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
    <main className="appShell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brandMark"><Brain size={20} /></div>
          <div>
            <h1>Onboarding Archaeologist</h1>
            <p>Codebase intelligence</p>
          </div>
        </div>

        <form onSubmit={runAnalysis} className="analysisForm">
          <div className="formHeader">
            <span>Repository</span>
            <GitBranch size={16} />
          </div>
          <label>
            Owner
            <input value={owner} onChange={(event) => setOwner(event.target.value)} spellCheck={false} />
          </label>
          <label>
            Repository
            <input value={repo} onChange={(event) => setRepo(event.target.value)} spellCheck={false} />
          </label>
          <label>
            Branch
            <input placeholder="default branch" value={branch} onChange={(event) => setBranch(event.target.value)} spellCheck={false} />
          </label>
          <button className="primaryButton" disabled={loading || !owner || !repo}>
            <Search size={17} />
            {loading ? "Analyzing" : "Run analysis"}
          </button>
        </form>

        <nav className="sideNav" aria-label="Workspace">
          <NavButton active={view === "overview"} icon={<Layers3 />} label="Overview" onClick={() => setView("overview")} />
          <NavButton active={view === "intelligence"} icon={<Network />} label="Intelligence" onClick={() => setView("intelligence")} />
          <NavButton active={view === "onboarding"} icon={<Map />} label="Onboarding" onClick={() => setView("onboarding")} />
          <NavButton active={view === "oracle"} icon={<Sparkles />} label="Oracle" onClick={() => setView("oracle")} />
        </nav>

        <section className="sidebarNote">
          <span>Coverage window</span>
          <strong>{stats ? `${stats.commits} commits` : "Not analyzed"}</strong>
          <p>Runs local evidence extraction with optional LLM enrichment when configured.</p>
        </section>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Repository Intelligence</p>
            <h2>{analysis ? `${analysis.owner}/${analysis.repo}` : "No repository selected"}</h2>
          </div>
          <div className="topbarActions">
            {analysis && <StatusPill label={`${stats?.coverage ?? 0}% coverage`} tone="good" />}
            {analysis && <StatusPill label={new Date(analysis.analyzed_at).toLocaleString()} tone="neutral" />}
          </div>
        </header>

        {error && <div className="errorBanner"><AlertTriangle size={18} />{error}</div>}

        {analysis && stats ? (
          <>
            <div className="metricGrid">
              <Metric icon={<GitBranch />} label="Decisions" value={stats.decisions} caption="ranked signals" />
              <Metric icon={<FileWarning />} label="Ghost code" value={stats.ghost} caption="review candidates" />
              <Metric icon={<UserRoundSearch />} label="Owners" value={stats.owners} caption="knowledge paths" />
              <Metric icon={<AlertTriangle />} label="Risk alerts" value={stats.risk} caption="bus factor" tone={stats.risk > 0 ? "warn" : "good"} />
              <Metric icon={<Wrench />} label="Scar tissue" value={stats.scar} caption="defensive patterns" />
              <Metric icon={<Map />} label="Journey" value={stats.days} caption="learning days" />
            </div>

            <div className="viewTabs" role="tablist">
              <Tab active={view === "overview"} label="Overview" onClick={() => setView("overview")} />
              <Tab active={view === "intelligence"} label="Evidence" onClick={() => setView("intelligence")} />
              <Tab active={view === "onboarding"} label="Onboarding" onClick={() => setView("onboarding")} />
              <Tab active={view === "oracle"} label="Oracle" onClick={() => setView("oracle")} />
            </div>

            {view === "overview" && <Overview analysis={analysis} />}
            {view === "intelligence" && <Intelligence analysis={analysis} />}
            {view === "onboarding" && <Onboarding analysis={analysis} />}
            {view === "oracle" && (
              <OraclePanel
                question={question}
                setQuestion={setQuestion}
                answer={answer}
                runQuestion={runQuestion}
              />
            )}
          </>
        ) : (
          <EmptyWorkspace loading={loading} />
        )}
      </section>
    </main>
  );
}

function Overview({ analysis }: { analysis: Analysis }) {
  const topDecision = analysis.decisions[0];
  const topRisk = analysis.bus_factor_alerts[0];
  const topGhost = analysis.ghost_code[0];

  return (
    <div className="overviewGrid">
      <section className="panel span2">
        <PanelHeader icon={<Brain />} title="Executive Summary" meta="Latest analysis" />
        <div className="summaryList">
          <SummaryItem icon={<GitBranch />} label="Primary decision signal" value={topDecision?.title ?? "No high-confidence decision signal found"} />
          <SummaryItem icon={<ShieldAlert />} label="Highest knowledge risk" value={topRisk ? `${topRisk.critical_person} across ${topRisk.areas_affected.slice(0, 2).join(", ")}` : "No bus-factor alert found"} />
          <SummaryItem icon={<Archive />} label="Top removal-review candidate" value={topGhost ? `${topGhost.path} - ${topGhost.reason}` : "No ghost-code candidate found"} />
        </div>
      </section>

      <section className="panel">
        <PanelHeader icon={<AlertTriangle />} title="Risk Queue" meta={`${analysis.bus_factor_alerts.length} alerts`} />
        <RiskList alerts={analysis.bus_factor_alerts} />
      </section>

      <section className="panel span2">
        <PanelHeader icon={<GitBranch />} title="Decision Timeline" meta={`${analysis.decisions.length} signals`} />
        <DecisionTable decisions={analysis.decisions.slice(0, 6)} />
      </section>

      <section className="panel">
        <PanelHeader icon={<UserRoundSearch />} title="Ownership Concentration" meta={`${analysis.ownership.length} paths`} />
        <OwnershipList ownership={analysis.ownership.slice(0, 7)} />
      </section>
    </div>
  );
}

function Intelligence({ analysis }: { analysis: Analysis }) {
  return (
    <div className="evidenceGrid">
      <section className="panel span2">
        <PanelHeader icon={<GitBranch />} title="Decision Excavation" meta="Commit evidence" />
        <DecisionTable decisions={analysis.decisions} />
      </section>
      <section className="panel">
        <PanelHeader icon={<Wrench />} title="Scar Tissue" meta="Defensive patterns" />
        <ScarList scarTissue={analysis.scar_tissue} />
      </section>
      <section className="panel">
        <PanelHeader icon={<FileWarning />} title="Ghost Code" meta="Review candidates" />
        <GhostList ghostCode={analysis.ghost_code} />
      </section>
      <section className="panel span2">
        <PanelHeader icon={<UserRoundSearch />} title="Knowledge Ownership" meta="Recent history" />
        <OwnershipTable ownership={analysis.ownership} />
      </section>
    </div>
  );
}

function Onboarding({ analysis }: { analysis: Analysis }) {
  return (
    <section className="panel">
      <PanelHeader icon={<Map />} title="Five Day Onboarding Path" meta="Generated from repository evidence" />
      <div className="journey">
        {analysis.onboarding_paths.map((item) => (
          <article className="journeyCard" key={item.day_number}>
            <span className="dayBadge">Day {item.day_number}</span>
            <h3>{item.focus_area}</h3>
            <p>{item.key_concepts.join(", ") || "Repository orientation"}</p>
            <div className="journeyMeta">
              <Clock3 size={15} />
              <span>{item.estimated_hours}h</span>
            </div>
            <div className="locationList">
              {item.code_locations.slice(0, 4).map((location) => <code key={location}>{location}</code>)}
              {item.code_locations.length === 0 && <span className="muted">No focused paths yet</span>}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function OraclePanel({
  question,
  setQuestion,
  answer,
  runQuestion,
}: {
  question: string;
  setQuestion: (value: string) => void;
  answer: OracleAnswer | null;
  runQuestion: (event: React.FormEvent) => void;
}) {
  return (
    <section className="panel oraclePanel">
      <PanelHeader icon={<Sparkles />} title="Evidence Oracle" meta="Answers cite stored findings" />
      <form onSubmit={runQuestion} className="oracleForm">
        <input value={question} onChange={(event) => setQuestion(event.target.value)} />
        <button className="primaryButton">
          <Sparkles size={17} />
          Ask
        </button>
      </form>
      {answer ? (
        <div className="answerLayout">
          <div className="answerText">
            <span className="sectionLabel">Answer</span>
            <p>{answer.answer}</p>
          </div>
          <div className="evidenceRail">
            <span className="sectionLabel">Evidence</span>
            {answer.evidence.length > 0 ? answer.evidence.map((item) => <blockquote key={item}>{item}</blockquote>) : <p className="muted">No evidence returned.</p>}
          </div>
        </div>
      ) : (
        <div className="oracleEmpty">
          <CircleHelp size={24} />
          <p>Ask about decisions, ownership, defensive code, risk, or ghost-code candidates.</p>
        </div>
      )}
    </section>
  );
}

function DecisionTable({ decisions }: { decisions: Decision[] }) {
  if (decisions.length === 0) return <EmptyText text="No explicit decision language found in the latest commits." />;
  return (
    <div className="dataTable">
      {decisions.map((item) => (
        <article className="tableRow" key={item.commit_sha}>
          <div>
            <strong>{item.title}</strong>
            <p>{item.summary}</p>
            <small>{item.evidence}</small>
          </div>
          <Confidence value={item.confidence} />
        </article>
      ))}
    </div>
  );
}

function OwnershipTable({ ownership }: { ownership: Owner[] }) {
  if (ownership.length === 0) return <EmptyText text="No ownership signals found in source paths." />;
  return (
    <div className="ownershipTable">
      {ownership.slice(0, 14).map((item) => (
        <article className="ownerRow" key={`${item.path}-${item.author}`}>
          <code>{item.path}</code>
          <span>{item.author}</span>
          <span>{item.commits} commits</span>
          <Risk risk={item.risk} />
        </article>
      ))}
    </div>
  );
}

function OwnershipList({ ownership }: { ownership: Owner[] }) {
  if (ownership.length === 0) return <EmptyText text="No ownership signals yet." />;
  return (
    <div className="compactList">
      {ownership.map((item) => (
        <article key={`${item.path}-${item.author}`}>
          <div>
            <strong>{item.path}</strong>
            <small>{item.author} - {item.commits} commits</small>
          </div>
          <Risk risk={item.risk} />
        </article>
      ))}
    </div>
  );
}

function RiskList({ alerts }: { alerts: BusFactorAlert[] }) {
  if (alerts.length === 0) return <EmptyText text="No bus-factor alerts found." />;
  return (
    <div className="compactList">
      {alerts.slice(0, 6).map((item) => (
        <article key={`${item.critical_person}-${item.risk_level}`}>
          <div>
            <strong>{item.critical_person}</strong>
            <small>{item.concentration_percentage}% concentration</small>
          </div>
          <StatusPill label={item.risk_level} tone={item.risk_level === "critical" ? "bad" : "warn"} />
        </article>
      ))}
    </div>
  );
}

function ScarList({ scarTissue }: { scarTissue: ScarTissue[] }) {
  if (scarTissue.length === 0) return <EmptyText text="No defensive patterns found in this analysis window." />;
  return (
    <div className="compactList">
      {scarTissue.slice(0, 10).map((item) => (
        <article key={`${item.file_path}-${item.pattern_type}-${item.line_numbers.join("-")}`}>
          <div>
            <strong>{item.file_path}</strong>
            <small>{item.pattern_type.replace(/_/g, " ")} near line {item.line_numbers.join(", ")}</small>
          </div>
          <Confidence value={item.confidence} />
        </article>
      ))}
    </div>
  );
}

function GhostList({ ghostCode }: { ghostCode: GhostCode[] }) {
  if (ghostCode.length === 0) return <EmptyText text="No stale or legacy markers found in this analysis window." />;
  return (
    <div className="compactList">
      {ghostCode.slice(0, 10).map((item) => (
        <article key={item.path}>
          <div>
            <strong>{item.path}</strong>
            <small>{item.reason} - last touched {item.last_touched_days} days ago</small>
          </div>
          <Confidence value={item.confidence} />
        </article>
      ))}
    </div>
  );
}

function Metric({ icon, label, value, caption, tone = "neutral" }: { icon: React.ReactNode; label: string; value: number; caption: string; tone?: "neutral" | "warn" | "good" }) {
  return (
    <div className={`metric ${tone}`}>
      <div className="metricIcon">{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{caption}</small>
    </div>
  );
}

function PanelHeader({ icon, title, meta }: { icon: React.ReactNode; title: string; meta: string }) {
  return (
    <div className="panelHeader">
      <div>
        <span className="panelIcon">{icon}</span>
        <h3>{title}</h3>
      </div>
      <small>{meta}</small>
    </div>
  );
}

function SummaryItem({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <article className="summaryItem">
      <span>{icon}</span>
      <div>
        <small>{label}</small>
        <strong>{value}</strong>
      </div>
      <ChevronRight size={16} />
    </article>
  );
}

function NavButton({ active, icon, label, onClick }: { active: boolean; icon: React.ReactNode; label: string; onClick: () => void }) {
  return (
    <button className={`navButton ${active ? "active" : ""}`} onClick={onClick} type="button">
      {icon}
      <span>{label}</span>
    </button>
  );
}

function Tab({ active, label, onClick }: { active: boolean; label: string; onClick: () => void }) {
  return <button className={`tab ${active ? "active" : ""}`} onClick={onClick} type="button">{label}</button>;
}

function Confidence({ value }: { value: number }) {
  return <span className="confidence">{Math.round(value * 100)}%</span>;
}

function Risk({ risk }: { risk: "low" | "medium" | "high" }) {
  return <span className={`status ${risk}`}>{risk}</span>;
}

function StatusPill({ label, tone }: { label: string; tone: "neutral" | "good" | "warn" | "bad" }) {
  return <span className={`status ${tone}`}>{label}</span>;
}

function EmptyText({ text }: { text: string }) {
  return <p className="emptyText">{text}</p>;
}

function EmptyWorkspace({ loading }: { loading: boolean }) {
  return (
    <section className="emptyState">
      <div className="emptyIcon"><Brain size={34} /></div>
      <h2>{loading ? "Analyzing repository" : "Run an analysis to populate the workspace"}</h2>
      <p>{loading ? "Mining commits, code paths, ownership, and defensive patterns." : "Use the repository form to generate an evidence-backed onboarding map."}</p>
    </section>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
