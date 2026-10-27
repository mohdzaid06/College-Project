
const STORAGE_KEYS = {
  user: 'placify_demo_user',
  applications: 'placify_demo_applications',
  results: 'placify_demo_results',
}

// Fictional jobs for the college demonstration.
export const DEMO_JOBS = [
  {
    id: 1,
    title: 'Frontend Developer Intern',
    company: 'Sample Company A',
    location: 'Bengaluru / Remote',
    job_type: 'Internship',
    description: 'Practice building responsive interfaces with a product team.',
    skills: ['HTML', 'CSS', 'JavaScript', 'React'],
    instructions: 'Fictional sample listing for demonstration only.',
    is_sample: true,
  },
  {
    id: 2,
    title: 'Python Developer Trainee',
    company: 'Sample Company B',
    location: 'Pune',
    job_type: 'Full-time',
    description: 'Explore beginner Python and backend development tasks.',
    skills: ['Python', 'Flask', 'SQL', 'Git'],
    instructions: 'Fictional sample listing for demonstration only.',
    is_sample: true,
  },
  {
    id: 3,
    title: 'Data Analyst Intern',
    company: 'Sample Company C',
    location: 'Remote',
    job_type: 'Internship',
    description: 'Practice analyzing data and presenting insights.',
    skills: ['Excel', 'SQL', 'Python', 'Communication'],
    instructions: 'Fictional sample listing for demonstration only.',
    is_sample: true,
  },
]

export const DEMO_QUESTIONS = [
  {
    id: 1,
    category: 'Programming',
    prompt: 'Which Python keyword defines a function?',
    options: ['func', 'def', 'function', 'method'],
    correct_answer: 1,
    explanation: 'Python uses def to define a function.',
  },
  {
    id: 2,
    category: 'Technical',
    prompt: 'Which SQL command retrieves records?',
    options: ['GET', 'OPEN', 'SELECT', 'FETCH TABLE'],
    correct_answer: 2,
    explanation: 'SELECT retrieves data from a database table.',
  },
  {
    id: 3,
    category: 'Aptitude',
    prompt: 'A team completes 12 tasks in 3 days. How many tasks at the same rate in 5 days?',
    options: ['15', '18', '20', '24'],
    correct_answer: 2,
    explanation: 'The rate is 4 tasks a day, so 5 days gives 20 tasks.',
  },
  {
    id: 4,
    category: 'HR',
    prompt: 'What makes a strong behavioral interview answer?',
    options: [
      'Give a specific example and explain the outcome',
      'Avoid answering directly',
      'List unrelated skills',
      'Give no details',
    ],
    correct_answer: 0,
    explanation: 'A specific example and outcome make your answer clear.',
  },
]

function read(key, fallback) {
  try {
    const value = localStorage.getItem(key)
    return value ? JSON.parse(value) : fallback
  } catch {
    return fallback
  }
}

function write(key, value) {
  localStorage.setItem(key, JSON.stringify(value))
}

export function getDemoUser() {
  return read(STORAGE_KEYS.user, null)
}

// Demo-only login: no real password or secure authentication.
export function loginDemo({ name, email }) {
  const cleanEmail = email.trim().toLowerCase()
  if (!cleanEmail) throw new Error('Please enter an email address.')

  const user = {
    id: cleanEmail,
    name: name?.trim() || cleanEmail.split('@')[0],
    email: cleanEmail,
    role: 'student',
  }

  write(STORAGE_KEYS.user, user)
  return user
}

export function logoutDemo() {
  localStorage.removeItem(STORAGE_KEYS.user)
}

export function getDemoJobs({ search = '', type = '', location = '' } = {}) {
  return DEMO_JOBS.filter((job) => {
    const text = `${job.title} ${job.company}`.toLowerCase()
    return (
      text.includes(search.toLowerCase()) &&
      (!type || job.job_type === type) &&
      job.location.toLowerCase().includes(location.toLowerCase())
    )
  })
}

export function getDemoJob(id) {
  return DEMO_JOBS.find((job) => job.id === Number(id)) || null
}

function forCurrentUser(key) {
  const user = getDemoUser()
  if (!user) return []
  const all = read(key, {})
  return all[user.id] || []
}

function saveForCurrentUser(key, value) {
  const user = getDemoUser()
  if (!user) throw new Error('Please start the demo session first.')
  const all = read(key, {})
  all[user.id] = value
  write(key, all)
}

export function getApplications() {
  return forCurrentUser(STORAGE_KEYS.applications)
}

export function trackDemoJob(jobId) {
  const job = getDemoJob(jobId)
  if (!job) throw new Error('Job not found.')

  const applications = getApplications()
  if (applications.some((item) => item.job_id === job.id)) {
    return applications
  }

  const next = [
    ...applications,
    {
      ...job,
      job_id: job.id,
      status: 'Saved',
      created_at: new Date().toISOString(),
    },
  ]
  saveForCurrentUser(STORAGE_KEYS.applications, next)
  return next
}

export function updateApplicationStatus(id, status) {
  const next = getApplications().map((item) =>
    item.job_id === Number(id) ? { ...item, status } : item
  )
  saveForCurrentUser(STORAGE_KEYS.applications, next)
  return next
}

export function getDemoQuestions(category = 'All topics') {
  return category === 'All topics'
    ? DEMO_QUESTIONS
    : DEMO_QUESTIONS.filter((question) => question.category === category)
}

export function getQuizResults() {
  return forCurrentUser(STORAGE_KEYS.results)
}

export function submitDemoQuiz(category, answers) {
  const questions = getDemoQuestions(category)
  const feedback = questions.map((question) => {
    const correct = answers[question.id] === question.correct_answer
    return {
      question_id: question.id,
      correct,
      explanation: question.explanation,
    }
  })

  const result = {
    id: Date.now(),
    category,
    score: feedback.filter((item) => item.correct).length,
    total: questions.length,
    feedback,
    created_at: new Date().toISOString(),
  }

  saveForCurrentUser(STORAGE_KEYS.results, [
    result,
    ...getQuizResults(),
  ])

  return result
}
