
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  ArrowRight,
  BriefcaseBusiness,
  MapPin,
  Search,
} from 'lucide-react'
import Notice from '../components/Notice'
import {
  getDemoJobs,
  getDemoJob,
  trackDemoJob,
} from '../services/DemoStore.js'

function JobCard({ job, onTrack, user }) {
  return (
    <article className="job-card">
      <div className="company-row">
        <div>
          <h3>{job.title}</h3>
          <p>{job.company}</p>
        </div>
        <span className="job-type">{job.job_type}</span>
      </div>

      <p>{job.description}</p>

      <div className="job-meta">
        <span><MapPin size={16} /> {job.location}</span>
        <span><BriefcaseBusiness size={16} /> {job.job_type}</span>
      </div>

      <div className="job-skills">
        {job.skills?.map((skill) => (
          <span key={skill}>{skill}</span>
        ))}
      </div>

      <div className="job-actions">
        <Link className="button button-secondary" to={`/jobs/${job.id}`}>
          View details <ArrowRight size={16} />
        </Link>
        {user && (
          <button
            className="button"
            onClick={() => onTrack(job)}
          >
            Save job
          </button>
        )}
      </div>
    </article>
  )
}

export default function Jobs({ user }) {
  const { id } = useParams()
  const [jobs, setJobs] = useState([])
  const [search, setSearch] = useState('')
  const [type, setType] = useState('')
  const [location, setLocation] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (id) {
      const job = getDemoJob(id)
      setJobs(job ? [job] : [])
    } else {
      setJobs(getDemoJobs({ search, type, location }))
    }
  }, [id, search, type, location])

  function handleTrack(job) {
    try {
      trackDemoJob(job.id)
      setError('')
      setMessage('Job saved to your demo dashboard.')
    } catch (err) {
      setMessage('')
      setError(err.message || 'Could not save this job.')
    }
  }

  return (
    <div className="wrap page-wrap">
      <div className="page-intro">
        <div className="eyebrow">PLACEMENT OPPORTUNITIES</div>
        <h1>{id ? 'Job details' : 'Explore jobs'}</h1>
        <p>Explore sample opportunities and save jobs to your demo dashboard.</p>
      </div>

      {message && <Notice message={message} />}
      {error && <p role="alert">{error}</p>}

      {!id && (
        <div className="job-filters">
          <label>
            <Search size={16} />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search jobs or companies"
            />
          </label>

          <select value={type} onChange={(event) => setType(event.target.value)}>
            <option value="">All job types</option>
            <option value="Internship">Internship</option>
            <option value="Full-time">Full-time</option>
          </select>

          <input
            value={location}
            onChange={(event) => setLocation(event.target.value)}
            placeholder="Filter by location"
          />
        </div>
      )}

      {id && (
        <Link to="/jobs" className="back-link">
          <ArrowLeft size={16} /> Back to all jobs
        </Link>
      )}

      {jobs.length === 0 ? (
        <div className="empty-state">
          <h2>No jobs found</h2>
          <p>Try changing your search or filters.</p>
        </div>
      ) : (
        <div className="jobs-grid">
          {jobs.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              user={user}
              onTrack={handleTrack}
            />
          ))}
        </div>
      )}

      <p className="demo-note">
        These are fictional sample listings for college demonstration purposes.
      </p>
    </div>
  )
}
