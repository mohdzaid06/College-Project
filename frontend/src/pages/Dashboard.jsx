
import { useEffect, useState } from 'react'
import {
  ArrowRight,
  BookOpenCheck,
  BriefcaseBusiness,
  ChartNoAxesCombined,
  Clock3,
  MapPin,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import {
  getApplications,
  getQuizResults,
  updateApplicationStatus,
} from '../services/DemoStore.js'
import Notice from '../components/Notice'

const STATUSES = ['Saved', 'Applied', 'Interview', 'Offered', 'Rejected']

export default function Dashboard({ user }) {
  const [applications, setApplications] = useState([])
  const [results, setResults] = useState([])
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  function load() {
    try {
      setApplications(getApplications())
      setResults(getQuizResults())
      setError('')
    } catch (e) {
      setError(e.message || 'Could not load your dashboard.')
    }
  }

  useEffect(() => {
    load()
  }, [])

  function update(id, status) {
    setBusy(true)
    try {
      updateApplicationStatus(id, status)
      load()
    } catch (e) {
      setError(e.message || 'Could not update application status.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="wrap page-wrap">
      <div className="dashboard-welcome">
        <div>
          <div className="eyebrow">
            <span className="eyebrow-line" /> YOUR PERSONAL SPACE
          </div>
          <h1>
            Good to see you,
            <br />
            <em>{user.name.split(' ')[0]}.</em>
          </h1>
          <p>Every practice session and application is progress worth keeping.</p>
        </div>
        <Link className="button" to="/quiz">
          Start a practice quiz <ArrowRight size={17} />
        </Link>
      </div>

      <Notice error={error} />

      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-icon blue"><BriefcaseBusiness /></span>
          <span className="stat-label">TRACKED ROLES</span>
          <b>{applications.length}</b>
          <small>opportunities in your list</small>
        </div>

        <div className="stat-card">
          <span className="stat-icon lilac"><BookOpenCheck /></span>
          <span className="stat-label">PRACTICE SESSIONS</span>
          <b>{results.length}</b>
          <small>quiz attempts completed</small>
        </div>

        <div className="stat-card">
          <span className="stat-icon green"><ChartNoAxesCombined /></span>
          <span className="stat-label">LATEST SCORE</span>
          <b>{results[0] ? `${results[0].score}/${results[0].total}` : '—'}</b>
          <small>{results[0] ? results[0].category : 'ready when you are'}</small>
        </div>
      </div>

      <div className="dashboard-columns">
        <section className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <span className="panel-kicker">YOUR OPPORTUNITIES</span>
              <h2>Application tracker</h2>
            </div>
            <Link to="/jobs">
              Explore roles <ArrowRight size={15} />
            </Link>
          </div>

          {applications.length ? (
            <div className="application-list">
              {applications.map((app) => (
                <article
                  className="application-row"
                  key={app.job_id ?? app.id}
                >
                  <span className="company-mark small-mark">
                    {app.company?.charAt(0) || 'J'}
                  </span>
                  <div className="application-info">
                    <b>{app.title}</b>
                    <span>
                      {app.company} · <MapPin size={12} /> {app.location}
                    </span>
                  </div>
                  <select
                    disabled={busy}
                    aria-label={`Status for ${app.title}`}
                    value={app.status}
                    onChange={(e) =>
                      update(app.job_id ?? app.id, e.target.value)
                    }
                  >
                    {STATUSES.map((status) => (
                      <option key={status}>{status}</option>
                    ))}
                  </select>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-inline">
              <BriefcaseBusiness />
              <div>
                <b>Your tracker is ready</b>
                <p>Add a role you want to follow and keep its status up to date.</p>
              </div>
              <Link to="/jobs">
                Browse roles <ArrowRight size={14} />
              </Link>
            </div>
          )}
        </section>

        <section className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <span className="panel-kicker">KEEP BUILDING</span>
              <h2>Practice history</h2>
            </div>
            <Link to="/quiz">
              Take a quiz <ArrowRight size={15} />
            </Link>
          </div>

          {results.length ? (
            <div className="result-list">
              {results.slice(0, 5).map((result) => (
                <div className="result-row" key={result.id}>
                  <span className="result-icon">
                    <BookOpenCheck size={17} />
                  </span>
                  <div>
                    <b>{result.category} practice</b>
                    <small>
                      <Clock3 size={12} />{' '}
                      {new Date(result.created_at).toLocaleDateString()}
                    </small>
                  </div>
                  <strong>{result.score}/{result.total}</strong>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-inline">
              <BookOpenCheck />
              <div>
                <b>Your first result is waiting</b>
                <p>Try a short quiz and your score will appear here.</p>
              </div>
              <Link to="/quiz">
                Start now <ArrowRight size={14} />
              </Link>
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
