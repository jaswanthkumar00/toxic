import { useCallback, useEffect, useState } from "react";
import type { ReactNode } from "react";
import Editor from "@monaco-editor/react";
import {
  ArrowDownRight, ArrowLeft, ArrowRight, ArrowUpRight, BadgeCheck, Bell, BookOpen,
  Braces, Check, ChevronDown, ChevronRight, CircleHelp, Clock3, Code2, Command,
  Compass, Database, ExternalLink, FileCode2, GitBranch, LayoutDashboard,
  Lightbulb, ListFilter, LoaderCircle, LockKeyhole, LogOut, Play, Plus,
  Search, Send, Settings2, ShieldCheck, Sparkles, Terminal, X, Zap,
} from "lucide-react";
import type { Exercise, Progress, SubmissionResult, Track, User } from "../../shared/src";
import { api } from "./api";

type AuthMode = "login" | "register";
type RunState = { kind: "idle" } | { kind: "loading" } | { kind: "result"; value: SubmissionResult };

const initialProgress: Progress = {
  completed_count: 0, completed_exercise_ids: [], total_exercises: 0, completion_percent: 0, total_submissions: 0,
  skills: [], recommended_exercise_id: null, recent_submissions: [],
};

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [checkingSession, setCheckingSession] = useState(true);
  const [authMode, setAuthMode] = useState<AuthMode>("login");
  const [tracks, setTracks] = useState<Track[]>([]);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [progress, setProgress] = useState<Progress>(initialProgress);
  const [activeExercise, setActiveExercise] = useState<Exercise | null>(null);
  const [toast, setToast] = useState("");
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(async () => {
    const [trackData, exerciseData, progressData] = await Promise.all([
      api.tracks(), api.exercises(), api.progress(),
    ]);
    setTracks(trackData);
    setExercises(exerciseData);
    setProgress(progressData);
  }, []);

  useEffect(() => {
    api.me()
      .then((current) => { setUser(current); return refresh(); })
      .catch((error: unknown) => {
        if (error instanceof Error && !["Please sign in.", "Session is no longer valid."].includes(error.message)) {
          setToast(error.message);
        }
        setUser(null);
      })
      .finally(() => setCheckingSession(false));
  }, [refresh]);

  useEffect(() => {
    if (!toast) return;
    const timer = window.setTimeout(() => setToast(""), 3500);
    return () => window.clearTimeout(timer);
  }, [toast]);

  async function authenticate(values: { name: string; email: string; password: string }) {
    setLoading(true);
    try {
      const authenticated = authMode === "register"
        ? await api.register(values.name, values.email, values.password)
        : await api.login(values.email, values.password);
      setUser(authenticated);
      await refresh();
    } catch (error) {
      setToast(error instanceof Error ? error.message : "Could not sign in.");
    } finally {
      setLoading(false);
    }
  }

  async function signOut() {
    try {
      await api.logout();
      setUser(null);
      setActiveExercise(null);
      setProgress(initialProgress);
    } catch (error) {
      setToast(error instanceof Error ? error.message : "Could not sign out.");
    }
  }

  async function openExercise(exercise: Exercise) {
    setActiveExercise(exercise);
  }

  function openChallenge(predicate: (exercise: Exercise) => boolean) {
    const challenge = exercises.find(predicate);
    if (challenge) setActiveExercise(challenge);
    else setToast("No challenge is available yet.");
  }

  if (checkingSession) return <div className="loading-screen"><div className="brand-mark"><Braces size={19} /></div><LoaderCircle className="spin" size={22} /></div>;
  if (!user) return <AuthScreen mode={authMode} setMode={setAuthMode} onSubmit={authenticate} loading={loading} toast={toast} />;

  return (
    <div className="app-shell">
      <Sidebar
        user={user}
        tracks={tracks}
        signOut={signOut}
        openHome={() => setActiveExercise(null)}
        openChallenge={openChallenge}
        openProgress={() => {
          setActiveExercise(null);
          window.setTimeout(() => document.getElementById("progress-section")?.scrollIntoView({ behavior: "smooth" }), 0);
        }}
        notify={setToast}
      />
      <main className="main-column">
        <Topbar user={user} signOut={signOut} />
        {activeExercise
          ? <Workspace exercise={activeExercise} goBack={() => setActiveExercise(null)} onComplete={async () => { await refresh(); }} notify={setToast} />
          : <Dashboard user={user} tracks={tracks} exercises={exercises} progress={progress} openExercise={openExercise} />}
      </main>
      {toast && <div className="toast"><CircleHelp size={16} />{toast}<button onClick={() => setToast("")} aria-label="Dismiss"><X size={15} /></button></div>}
    </div>
  );
}

function AuthScreen({ mode, setMode, onSubmit, loading, toast }: {
  mode: AuthMode; setMode: (mode: AuthMode) => void;
  onSubmit: (values: { name: string; email: string; password: string }) => void;
  loading: boolean; toast: string;
}) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  return (
    <div className="auth-screen">
      <div className="auth-aside">
        <a className="brand auth-brand" href="#"><Brand /></a>
        <div className="auth-copy">
          <div className="eyebrow"><span className="live-dot" />THE ENGINEERING PLAYGROUND</div>
          <h1>Build skills<br />that <span>ship.</span></h1>
          <p>Real-world challenges. Practical feedback. A clearer path from learning to your first engineering role.</p>
          <div className="proof-row"><span><b>Practical, not performative.</b> Built around the work teams do.</span></div>
        </div>
        <div className="aside-bottom"><span>Designed for the work, not just the interview.</span><span>01 — 03</span></div>
        <div className="auth-graphic"><div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="orbit orbit-three" /><div className="orbit-core"><Braces size={28} /></div><span className="orb-label orb-one">learn</span><span className="orb-label orb-two">build</span><span className="orb-label orb-three">ship</span></div>
      </div>
      <div className="auth-panel">
        <div className="auth-topline"><span>ALREADY PART OF THE COMMUNITY?</span><button className="text-button" onClick={() => setMode(mode === "login" ? "register" : "login")}>{mode === "login" ? "Create an account" : "Sign in"} <ArrowUpRight size={15} /></button></div>
        <div className="auth-form-wrap">
          <div className="form-icon"><LockKeyhole size={20} /></div>
          <div className="eyebrow muted">{mode === "login" ? "WELCOME BACK" : "YOUR NEXT CHAPTER"}</div>
          <h2>{mode === "login" ? "Pick up where you left off." : "Make something of your skills."}</h2>
          <p className="form-intro">{mode === "login" ? "Your practice space is ready when you are." : "Join a community that learns by building."}</p>
          <form onSubmit={(event) => { event.preventDefault(); onSubmit({ name, email, password }); }}>
            {mode === "register" && <label>Full name<input required minLength={2} autoComplete="name" placeholder="Jordan Lee" value={name} onChange={(event) => setName(event.target.value)} /></label>}
            <label>Email address<input required type="email" autoComplete="email" placeholder="you@example.com" value={email} onChange={(event) => setEmail(event.target.value)} /></label>
            <label>Password<input required minLength={mode === "register" ? 10 : 1} type="password" autoComplete={mode === "login" ? "current-password" : "new-password"} placeholder={mode === "login" ? "Enter your password" : "At least 10 characters"} value={password} onChange={(event) => setPassword(event.target.value)} /></label>
            {toast && <div className="form-error">{toast}</div>}
            <button className="button button-primary auth-submit" disabled={loading}>{loading ? <LoaderCircle className="spin" size={17} /> : null}{mode === "login" ? "Sign in to SkillForge" : "Create your account"}<ArrowRight size={17} /></button>
          </form>
          <div className="auth-legal"><ShieldCheck size={14} />Your work stays yours. Always.</div>
          <div className="switch-mode">{mode === "login" ? "New around here?" : "Already have an account?"} <button onClick={() => setMode(mode === "login" ? "register" : "login")}>{mode === "login" ? "Join SkillForge" : "Sign in"}</button></div>
        </div>
        <div className="auth-footer"><span>© 2026 SKILLFORGE</span><span>LEARNING, BUILT FOR THE REAL WORLD</span></div>
      </div>
    </div>
  );
}

function Brand() {
  return <><span className="brand-mark"><Braces size={18} strokeWidth={2.5} /></span><span>skillforge<span className="brand-period">.</span></span></>;
}

function Sidebar({ user, tracks, signOut, openHome, openChallenge, openProgress, notify }: {
  user: User; tracks: Track[]; signOut: () => void;
  openHome: () => void; openChallenge: (predicate: (exercise: Exercise) => boolean) => void;
  openProgress: () => void; notify: (message: string) => void;
}) {
  return (
    <aside className="sidebar">
      <a className="brand" href="#" aria-label="SkillForge home"><Brand /></a>
      <div className="side-label">WORKSPACE</div>
      <button className="side-link active" onClick={openHome}><LayoutDashboard size={17} /><span>Overview</span><span className="side-shortcut">⌘ 1</span></button>
      <button className="side-link" onClick={() => openChallenge(() => true)}><Compass size={17} /><span>Explore challenges</span><span className="side-count">{tracks.reduce((sum, track) => sum + track.exercise_count, 0)}</span></button>
      <button className="side-link" onClick={() => openChallenge((exercise) => exercise.language === "javascript")}><GitBranch size={17} /><span>Project sandbox</span><span className="side-new">NEW</span></button>
      <button className="side-link" onClick={openProgress}><BadgeCheck size={17} /><span>My progress</span></button>
      <div className="side-divider" />
      <div className="side-label">YOUR LEARNING PATH</div>
      {tracks.map((track) => <button className="path-link" key={track.id} onClick={() => openChallenge((exercise) => exercise.track_id === track.id)}><span className={`path-icon ${track.icon}`}><TrackIcon icon={track.icon} /></span><span>{track.title}</span><ChevronRight size={14} /></button>)}
      <div className="sidebar-grow" />
      <div className="side-mentor"><div className="mentor-icon"><Sparkles size={16} /></div><div><b>Need a nudge?</b><span>Focused challenge hints.</span></div><ArrowUpRight size={15} /></div>
      <button className="side-link side-settings" onClick={() => notify("Account preferences are not configured in this release.")}><Settings2 size={17} /><span>Preferences</span></button>
      <button className="profile-row" onClick={signOut}><span className="profile-avatar">{initials(user.name)}</span><span className="profile-copy"><b>{user.name}</b><small>{user.role === "instructor" ? "Instructor" : "Learning path"}</small></span><LogOut size={15} /></button>
    </aside>
  );
}

function TrackIcon({ icon }: { icon: string }) {
  if (icon === "database") return <Database size={15} />;
  if (icon === "layout") return <FileCode2 size={15} />;
  return <Code2 size={15} />;
}

function Topbar({ user, signOut }: { user: User; signOut: () => void }) {
  return (
    <header className="topbar">
      <div className="breadcrumb"><span>Workspace</span><ChevronRight size={14} /><b>Overview</b></div>
      <div className="topbar-tools"><div className="top-search"><Search size={15} /><span>Search anything...</span><kbd>⌘ K</kbd></div><button className="icon-button" aria-label="Notifications"><Bell size={17} /><i /></button><span className="top-separator" /><button className="top-user" onClick={signOut}><span className="profile-avatar">{initials(user.name)}</span><ChevronDown size={14} /></button></div>
    </header>
  );
}

function Dashboard({ user, tracks, exercises, progress, openExercise }: {
  user: User; tracks: Track[]; exercises: Exercise[]; progress: Progress; openExercise: (exercise: Exercise) => void;
}) {
  const nextChallenge = exercises.find((exercise) => exercise.id === progress.recommended_exercise_id) || exercises[0];
  const firstName = user.name.split(" ")[0];
  const dateLabel = new Intl.DateTimeFormat("en", {
    weekday: "long",
    month: "long",
    day: "numeric",
  }).format(new Date()).toUpperCase();
  return (
    <div className="dashboard page-enter">
      <div className="welcome-row"><div><div className="eyebrow muted">{dateLabel} <span className="eyebrow-dot">·</span> YOUR WORKSPACE</div><h1>Good to have you, {firstName}<span className="wave">✳</span></h1><p>Small wins turn into real momentum. Let’s make one today.</p></div><button className="button button-outline"><Command size={15} />Quick actions <kbd>⌘ K</kbd></button></div>
      <section className="hero-card">
        <div className="hero-content"><div className="hero-kicker"><span className="hero-kicker-icon"><Sparkles size={13} /></span>YOUR NEXT MILESTONE</div><h2>Think like an engineer.<br /><em>Build like one, too.</em></h2><p>Practice the decisions and habits that make great teams work.</p><button className="button button-lime" onClick={() => nextChallenge && openExercise(nextChallenge)}>Continue learning <ArrowRight size={16} /></button><div className="hero-caption"><span className="caption-line" />Your journey, one challenge at a time</div></div>
        <div className="hero-art" aria-hidden="true"><div className="art-rings"><div /><div /><div /></div><div className="art-code"><div className="art-code-head"><span /><span /><span /><b>practical-skills.ts</b></div><div className="code-row"><i>01</i><span><b>const</b> progress = <strong>learn</strong>();</span></div><div className="code-row"><i>02</i><span><b>while</b> (curious) {'{'}</span></div><div className="code-row indented"><i>03</i><span><b>build</b>(somethingReal);</span></div><div className="code-row"><i>04</i><span>{'}'} <label>✦</label></span></div><div className="code-row"><i>05</i><span><b>ship</b>(); <label>// today</label></span></div><div className="art-cursor" /></div><div className="float-tag tag-top"><span>✳</span> REAL-WORLD READY</div><div className="float-tag tag-bottom"><div className="float-check"><Check size={12} /></div>Progress, not perfection</div></div>
      </section>
      <section className="metrics-grid">
        <MetricCard label="CHALLENGES COMPLETED" value={`${progress.completed_count.toString().padStart(2, "0")}`} suffix={`/ ${progress.total_exercises.toString().padStart(2, "0")}`} icon={<BadgeCheck size={17} />} trend={`${progress.completion_percent}% of your path`} color="violet" />
        <MetricCard label="SUBMISSIONS" value={`${progress.total_submissions.toString().padStart(2, "0")}`} suffix="" icon={<Code2 size={17} />} trend="Practice attempts recorded" color="orange" />
        <MetricCard label="SKILL SCORE" value={progress.total_submissions && progress.skills.length ? `${Math.round(progress.skills.reduce((sum, skill) => sum + skill.score, 0) / progress.skills.length)}` : "--"} suffix="/ 100" icon={<Zap size={17} />} trend="Based on your submissions" color="lime" />
        <MetricCard label="LATEST SCORE" value={progress.recent_submissions.length ? `${progress.recent_submissions[0].score}` : "--"} suffix="/ 100" icon={<Clock3 size={17} />} trend="From your latest assessment" color="blue" />
      </section>
      <div className="content-grid">
        <section className="panel path-panel">
          <div className="section-head"><div><div className="eyebrow muted">PICK UP WHERE YOU LEFT OFF</div><h3>Your learning path</h3></div><button className="quiet-link">View all <ArrowRight size={14} /></button></div>
          <div className="track-list">{tracks.map((track, index) => {
            const trackExercises = exercises.filter((exercise) => exercise.track_id === track.id);
            const completed = trackExercises.filter((exercise) => progress.completed_exercise_ids.includes(exercise.id)).length;
            return <div className="track-card" key={track.id}><div className={`track-symbol ${track.icon}`}><TrackIcon icon={track.icon} /></div><div className="track-info"><div className="track-title-row"><h4>{track.title}</h4><span className="level-pill">{track.level}</span></div><p>{track.description}</p><div className="track-progress-row"><div className="mini-progress"><span style={{ width: `${trackExercises.length ? completed / trackExercises.length * 100 : 0}%` }} /></div><span>{completed}/{track.exercise_count} challenges</span></div></div><button className="round-arrow" aria-label={`Open ${track.title}`} onClick={() => trackExercises[0] && openExercise(trackExercises[0])}><ArrowUpRight size={17} /></button><span className="track-index">0{index + 1}</span></div>;
          })}</div>
        </section>
        <section className="panel recommended-panel">
          <div className="section-head"><div><div className="eyebrow muted">HAND-PICKED FOR YOU</div><h3>A good next step</h3></div><span className="spark-badge"><Sparkles size={14} /></span></div>
          {nextChallenge ? <><div className="recommend-art"><div className="rec-squares"><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /></div><span className="recommend-icon"><Code2 size={22} /></span><span className="rec-tag">CHALLENGE 0{nextChallenge.id}</span><span className="rec-orbit" /></div><div className="recommend-meta"><span>{nextChallenge.difficulty.toUpperCase()}</span><i /> <span>{nextChallenge.estimated_minutes} MIN</span><i /> <span>{nextChallenge.skill.toUpperCase()}</span></div><h4>{nextChallenge.title}</h4><p>{nextChallenge.problem_statement}</p><button className="button button-dark full-button" onClick={() => openExercise(nextChallenge)}>Take this challenge <ArrowRight size={15} /></button><div className="recommend-note"><Lightbulb size={14} />A focused 20 minutes can move you forward.</div></> : <div className="empty-state">Your next challenge is being prepared.</div>}
        </section>
      </div>
      <section className="bottom-grid" id="progress-section">
        <div className="panel skill-panel"><div className="section-head"><div><div className="eyebrow muted">YOUR GROWING TOOLKIT</div><h3>Skills in practice</h3></div><button className="icon-button small"><ListFilter size={16} /></button></div>{progress.skills.length ? progress.skills.slice(0, 4).map((skill, index) => <div className="skill-row" key={skill.name}><span className={`skill-number skill-${index}`}>0{index + 1}</span><span className="skill-name">{skill.name}</span><div className="skill-bar"><span style={{ width: `${skill.score}%` }} /></div><b>{skill.score}</b><ArrowUpRight size={14} /></div>) : <div className="skills-empty"><span className="empty-icon"><Sparkles size={16} /></span><span>Complete your first challenge to see your skills take shape.</span><ArrowRight size={14} /></div>}</div>
        <div className="panel activity-panel"><div className="section-head"><div><div className="eyebrow muted">RECENT MOMENTUM</div><h3>Your latest work</h3></div><button className="quiet-link">History <ArrowRight size={14} /></button></div>{progress.recent_submissions.length ? <div className="activity-list">{progress.recent_submissions.slice(0, 3).map((submission) => {
          const completed = submission.status === "passed";
          return <div className="activity-row" key={submission.id}><span className={`activity-state ${completed ? "success" : ""}`}>{completed ? <Check size={13} /> : <Code2 size={13} />}</span><span className="activity-copy"><b>{submission.exercise_title}</b><small>{completed ? "Challenge completed" : "Practice submitted"}</small></span><span className="activity-score">{submission.score}%</span></div>;
        })}</div> : <div className="activity-empty"><div className="empty-check"><Plus size={17} /></div><div><b>Make this space yours.</b><span>Your first submission is the start of something.</span></div><button className="text-arrow" onClick={() => nextChallenge && openExercise(nextChallenge)}>Start <ArrowRight size={14} /></button></div>}</div>
      </section>
      <footer className="dashboard-footer"><span>BUILT FOR THE WAY GREAT ENGINEERS GROW.</span><span>LESS THEORY. MORE DOING. <span className="footer-star">✳</span></span></footer>
    </div>
  );
}

function MetricCard({ label, value, suffix, icon, trend, color }: { label: string; value: string; suffix: string; icon: ReactNode; trend: string; color: string }) {
  return <div className="metric-card"><div className={`metric-icon ${color}`}>{icon}</div><div className="metric-label">{label}</div><div className="metric-value">{value}<span>{suffix}</span></div><div className="metric-trend"><span className={`trend-dot ${color}`} />{trend}</div></div>;
}

function Workspace({ exercise, goBack, onComplete, notify }: {
  exercise: Exercise; goBack: () => void; onComplete: () => Promise<void>; notify: (message: string) => void;
}) {
  const storageKey = `skillforge-draft-${exercise.id}`;
  const [code, setCode] = useState(() => localStorage.getItem(storageKey) || exercise.starter_code);
  const [runState, setRunState] = useState<RunState>({ kind: "idle" });
  const [hint, setHint] = useState("");
  const [hintLoading, setHintLoading] = useState(false);
  const [tab, setTab] = useState<"problem" | "tests">("problem");
  const [terminalOpen, setTerminalOpen] = useState(true);
  const [completedTasks, setCompletedTasks] = useState<number[]>([]);
  const [commitMessage, setCommitMessage] = useState("fix: handle challenge edge cases");
  const [commitCreated, setCommitCreated] = useState(false);
  const result = runState.kind === "result" ? runState.value : null;

  useEffect(() => {
    setCode(localStorage.getItem(storageKey) || exercise.starter_code);
    setRunState({ kind: "idle" });
    setHint("");
    setCompletedTasks([]);
    setCommitCreated(false);
  }, [exercise.id, exercise.starter_code, storageKey]);

  const updateCode = (value: string | undefined) => {
    const next = value ?? "";
    setCode(next);
    localStorage.setItem(storageKey, next);
  };

  async function run(action: "run" | "submit") {
    setRunState({ kind: "loading" });
    try {
      const value = await api.submit(exercise.id, code, action);
      setRunState({ kind: "result", value });
      if (action === "submit") await onComplete();
    } catch (error) {
      setRunState({ kind: "idle" });
      notify(error instanceof Error ? error.message : "Could not assess this submission.");
    }
  }

  async function requestHint() {
    setHintLoading(true);
    try {
      const result = await api.hint(exercise.id, code);
      setHint(result.hint);
    } catch (error) {
      notify(error instanceof Error ? error.message : "Could not load a hint.");
    } finally {
      setHintLoading(false);
    }
  }

  function simulateCommit() {
    const message = commitMessage.trim();
    if (!message) {
      notify("Add a commit message before creating the mock commit.");
      return;
    }
    setCommitCreated(true);
    notify(`Mock commit created: ${message}`);
  }

  return <div className="workspace page-enter">
    <div className="workspace-toolbar"><button className="back-link" onClick={goBack}><ArrowLeft size={16} /> Dashboard</button><div className="workspace-crumb"><ChevronRight size={14} /><span>{exercise.track_title}</span><ChevronRight size={14} /><b>{exercise.title}</b></div><div className="workspace-toolbar-right"><span className="saved-indicator"><span />Draft saved</span><button className="icon-button small"><CircleHelp size={17} /></button></div></div>
    <div className="workspace-title"><div><div className="eyebrow muted">{exercise.skill.toUpperCase()} <span className="eyebrow-dot">·</span> {exercise.difficulty.toUpperCase()}</div><h1>{exercise.title}</h1><p>{exercise.estimated_minutes} min <span>·</span> Practical challenge</p></div><div className="workspace-title-actions"><button className="button button-outline" onClick={requestHint} disabled={hintLoading}>{hintLoading ? <LoaderCircle className="spin" size={15} /> : <Lightbulb size={15} />} Get a hint</button><button className="button button-primary" onClick={() => run("submit")} disabled={runState.kind === "loading"}><Send size={14} /> Submit solution</button></div></div>
    <section className="step-strip"><div className="step-strip-head"><div className="eyebrow muted">PROJECT PLAN</div><span>{completedTasks.length} / {exercise.tasks.length} STEPS COMPLETE</span></div><div className="step-track">{exercise.tasks.map((task, index) => {
      const completed = completedTasks.includes(index);
      return <button className={`step-item ${completed ? "done" : ""}`} key={task} aria-pressed={completed} onClick={() => setCompletedTasks((current) => completed ? current.filter((step) => step !== index) : [...current, index])}><span className="step-number">{completed ? <Check size={13} /> : `0${index + 1}`}</span><span>{task}</span></button>;
    })}</div></section>
    <div className="workspace-grid">
      <aside className="problem-panel">
        <div className="problem-tabs"><button className={tab === "problem" ? "selected" : ""} onClick={() => setTab("problem")}><BookOpen size={15} />Task</button><button className={tab === "tests" ? "selected" : ""} onClick={() => setTab("tests")}><BadgeCheck size={15} />Test cases <span>{exercise.test_cases.length}</span></button></div>
        {tab === "problem" ? <><div className="problem-body"><div className="problem-kicker">THE BRIEF <span>01 / 03</span></div><p>{exercise.problem_statement}</p><div className="brief-note"><div><Sparkles size={14} /></div><span><b>Think like the team.</b>Consider edge cases and maintainability—not only the happy path.</span></div><div className="problem-kicker task-kicker">WHAT GOOD LOOKS LIKE</div><ul className="acceptance-list"><li><Check size={14} />Meets the requirements above</li><li><Check size={14} />Handles the cases in the tests</li><li><Check size={14} />Keeps the implementation readable</li></ul>{hint && <div className="hint-box"><div><Lightbulb size={15} /><b>Your mentor’s hint</b><button onClick={() => setHint("")} aria-label="Close hint"><X size={14} /></button></div><p>{hint}</p></div>}</div><button className="hint-footer" onClick={requestHint} disabled={hintLoading}><span><span className="hint-bulb"><Lightbulb size={15} /></span><span><b>Hit a wall?</b><small>Get a thoughtful nudge.</small></span></span><ArrowRight size={16} /></button></> : <div className="problem-body test-case-list">{exercise.test_cases.map((test, index) => <div className="test-case" key={test.name}><span className="test-number">0{index + 1}</span><div><b>{test.name}</b><code>Input: {JSON.stringify(test.input)}</code><code>Expected: {JSON.stringify(test.expected)}</code></div></div>)}</div>}
      </aside>
      <section className="editor-panel">
        <div className="editor-head">
          <div className="editor-file"><span className="file-icon"><FileCode2 size={15} /></span><span>solution.{exercise.language === "python" ? "py" : exercise.language === "sql" ? "sql" : "js"}</span><span className="file-dirty">●</span></div>
          <div className="editor-head-right"><span className="editor-language">{exercise.language}</span><button className="icon-button small" aria-label="Editor settings"><Settings2 size={15} /></button></div>
        </div>
        <div className="monaco-container">
          <Editor height="100%" language={exercise.language === "python" ? "python" : exercise.language === "sql" ? "sql" : "javascript"} theme="vs-dark" value={code} onChange={updateCode} options={{ minimap: { enabled: false }, fontSize: 13, lineHeight: 23, fontFamily: "'Cascadia Code', 'Fira Code', Consolas, monospace", padding: { top: 20 }, scrollBeyondLastLine: false, automaticLayout: true, wordWrap: "on", renderLineHighlight: "line", lineNumbers: "on", glyphMargin: false, folding: true, tabSize: 2 }} />
        </div>
        <div className="editor-foot">
          <div><span className="status-ok"><Code2 size={12} /> Ready for assessment</span><span>Ln {code.split("\n").length}, Col 1</span></div>
          <span>UTF-8 <i>·</i> {exercise.language === "python" ? "Python 3.12" : exercise.language === "sql" ? "PostgreSQL" : "JavaScript ES2022"}</span>
        </div>
        <div className={`console-panel ${terminalOpen ? "open" : ""}`}>
          <div className="console-title">
            <button className="console-toggle" onClick={() => setTerminalOpen(!terminalOpen)} aria-expanded={terminalOpen}>
              <span><Terminal size={14} />OUTPUT CONSOLE <ChevronDown size={14} /></span>
              <span>{result ? `${result.passed_count}/${result.total_count} checks` : "Ready to run"}</span>
            </button>
            <button className="console-close" onClick={() => setTerminalOpen(false)} aria-label="Hide output"><X size={14} /></button>
          </div>
          {terminalOpen && <div className="console-output">
            {runState.kind === "loading"
              ? <div className="console-muted"><LoaderCircle className="spin" size={15} />Checking your work...</div>
              : result
                ? <>
                  <div className={`console-summary ${result.status === "passed" ? "positive" : ""}`}>
                    <span className="console-state-icon">{result.status === "passed" ? <Check size={13} /> : <ArrowDownRight size={13} />}</span>
                    <b>{result.output}</b><span className="console-time">{result.execution_time_ms} ms</span>
                  </div>
                  <div className="console-checks">{result.test_results.map((test) => <span key={test.name} className={test.passed ? "check-pass" : "check-fail"}>{test.passed ? <Check size={12} /> : <X size={12} />}{test.name}</span>)}</div>
                  <div className="mock-notice"><CircleHelp size={13} />Assessment is a static mock; submitted code is not executed in a sandbox.</div>
                </>
                : <div className="console-muted"><span className="prompt-symbol">›</span>Run your code to see assessment feedback.</div>}
          </div>}
        </div>
        <div className="editor-actions">
          <span><GitBranch size={14} />main <span className="branch-dot">·</span> <span className="mock-commit">Sandbox branch simulation <ArrowUpRight size={12} /></span></span>
          <div>
            <button className="button button-run" onClick={() => run("run")} disabled={runState.kind === "loading"}><Play size={13} fill="currentColor" /> Run checks</button>
            <button className="button button-submit" onClick={() => run("submit")} disabled={runState.kind === "loading"}>{runState.kind === "loading" ? <LoaderCircle className="spin" size={15} /> : <Send size={13} />} Submit <ArrowRight size={14} /></button>
          </div>
        </div>
      </section>
    </div>
    {result && <section className="result-metrics"><div><span>RUBRIC SCORE</span><b>{result.score}%</b></div><div><span>CHECKS PASSED</span><b>{result.passed_count} / {result.total_count}</b></div><div><span>CODE QUALITY (MOCK)</span><b>{result.code_quality.score} / 100</b></div><div><span>ASSESSMENT TIME</span><b>{result.execution_time_ms} ms</b></div>{result.hint && <p><Lightbulb size={13} />Next focus: {result.hint}</p>}</section>}
    <section className="mock-git-panel"><div className="mock-git-icon"><GitBranch size={16} /></div><div className="mock-git-copy"><b>Practice the commit, too.</b><span>Write a clear message and simulate the handoff.</span></div><input aria-label="Mock commit message" value={commitMessage} onChange={(event) => { setCommitMessage(event.target.value); setCommitCreated(false); }} /><button className="button button-outline" onClick={simulateCommit}>{commitCreated ? <Check size={14} /> : <GitBranch size={14} />}{commitCreated ? "Mock commit saved" : "Create mock commit"}</button><span className="mock-git-note"><CircleHelp size={13} />No repository is changed</span></section>
    <div className="workspace-footnote"><span><ShieldCheck size={14} />Your work is saved privately to this account.</span><span><ExternalLink size={13} />Sandbox and Git actions are simulations.</span></div>
  </div>;
}

function initials(name: string) {
  return name.split(/\s+/).slice(0, 2).map((part) => part[0]?.toUpperCase() || "").join("");
}

export default App;
