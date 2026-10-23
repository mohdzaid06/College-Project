export default function Notice({ error, success }) {
  if (!error && !success) return null
  return <div className={`notice ${error ? 'notice-error' : 'notice-success'}`} role="status">{error || success}</div>
}
