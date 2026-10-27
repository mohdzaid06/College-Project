
import { useEffect, useState } from 'react'
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  CircleHelp,
  RotateCcw,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import {
  getDemoQuestions,
  submitDemoQuiz,
} from '../services/DemoStore.js'
import Notice from '../components/Notice'

const CATEGORIES = ['All topics', 'Programming', 'Aptitude', 'Technical', 'HR']

export default function Quiz({ user }) {
  const [category, setCategory] = useState('All topics')
  const [questions, setQuestions] = useState([])
  const [index, setIndex] = useState(0)
  const [answers, setAnswers] = useState({})
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  function load() {
    setLoading(true)
    setError('')
    setResult(null)
    setAnswers({})
    setIndex(0)

    try {
      setQuestions(getDemoQuestions(category))
    } catch (e) {
      setError(e.message || 'Could not load questions.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [category])

  function submit() {
    setError('')

    try {
      const savedResult = submitDemoQuiz(category, answers)
      setResult(savedResult)
    } catch (e) {
      setError(e.message || 'Could not submit the quiz.')
    }
  }

  const question = questions[index]

  return (
    <div className="wrap page-wrap quiz-page">
      <div className="page-intro">
        <div className="eyebrow">
          <span className="eyebrow-line" /> PRACTISE AT YOUR OWN PACE
        </div>
        <h1>
          Confidence comes
          <br />
          <em>with practice.</em>
        </h1>
        <p>A quick set of questions to warm up your interview thinking.</p>
      </div>

      <div className="quiz-toolbar">
        <div className="category-tabs" aria-label="Quiz category">
          {CATEGORIES.map((item) => (
            <button
              key={item}
              className={category === item ? 'active' : ''}
              onClick={() => setCategory(item)}
            >
              {item}
            </button>
          ))}
        </div>
        <span>{questions.length} questions</span>
      </div>

      <Notice error={error} />

      {!user && (
        <div className="auth-reminder">
          Try a quiz without an account.{' '}
          <Link to="/login?next=/quiz">Log in</Link> to save scores to your
          dashboard.
        </div>
      )}

      {loading ? (
        <div className="loading">Preparing your practice…</div>
      ) : result ? (
        <div className="quiz-result">
          <span className="result-check">
            <CheckCircle2 />
          </span>
          <div className="eyebrow">PRACTICE COMPLETE</div>
          <h2>
            {result.score} <span>/ {result.total}</span>
          </h2>
          <p>
            {result.score === result.total
              ? 'Excellent work. Keep that momentum going.'
              : 'Good effort. Every answer is a chance to learn.'}
          </p>

          <div className="feedback-list">
            {result.feedback.map((item, i) => (
              <div key={item.question_id}>
                <span>
                  {item.correct ? '✓' : '•'} Question {i + 1}
                </span>
                <p>{item.explanation}</p>
              </div>
            ))}
          </div>

          <button className="button" onClick={load}>
            Practice again <RotateCcw size={16} />
          </button>

          {user && (
            <Link className="text-link" to="/dashboard">
              See your dashboard <ArrowRight size={16} />
            </Link>
          )}
        </div>
      ) : question ? (
        <div className="question-card">
          <div className="question-progress">
            <span>
              QUESTION {String(index + 1).padStart(2, '0')}
              <i> / {String(questions.length).padStart(2, '0')}</i>
            </span>
            <div>
              <span
                style={{
                  width: `${((index + 1) / questions.length) * 100}%`,
                }}
              />
            </div>
          </div>

          <span className="question-category">
            <CircleHelp size={14} /> {question.category}
          </span>

          <h2>{question.prompt}</h2>

          <div className="answer-options">
            {question.options.map((option, i) => (
              <button
                key={option}
                className={
                  answers[question.id] === i
                    ? 'answer-option selected'
                    : 'answer-option'
                }
                onClick={() =>
                  setAnswers((previous) => ({
                    ...previous,
                    [question.id]: i,
                  }))
                }
              >
                <span>{String.fromCharCode(65 + i)}</span>
                {option}
              </button>
            ))}
          </div>

          <div className="question-actions">
            <button
              className="back-link"
              disabled={index === 0}
              onClick={() => setIndex((previous) => previous - 1)}
            >
              <ArrowLeft size={16} /> Previous
            </button>

            {index < questions.length - 1 ? (
              <button
                className="button"
                disabled={answers[question.id] === undefined}
                onClick={() => setIndex((previous) => previous + 1)}
              >
                Next question <ArrowRight size={16} />
              </button>
            ) : (
              <button
                className="button"
                disabled={Object.keys(answers).length !== questions.length}
                onClick={submit}
              >
                Submit and save score <ArrowRight size={16} />
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="empty-state">
          <h3>No questions in this category yet</h3>
          <button
            className="text-link"
            onClick={() => setCategory('All topics')}
          >
            View all topics
          </button>
        </div>
      )}
    </div>
  )
}
