import { ArrowDownRight, ArrowRight, BookOpenCheck, BriefcaseBusiness, ChartNoAxesCombined, CirclePlay, Compass, Sparkles } from 'lucide-react'
import { Link } from 'react-router-dom'

const steps = [
  { icon: BriefcaseBusiness, number: '01', title: 'Find your direction', text: 'Explore a curated set of sample roles and learn what employers ask for.' },
  { icon: BookOpenCheck, number: '02', title: 'Build your confidence', text: 'Practise programming, aptitude, technical and HR interview questions.' },
  { icon: ChartNoAxesCombined, number: '03', title: 'Track your progress', text: 'Keep applications and quiz results together in your student dashboard.' },
]

export default function Home() {
  return <>
    <section className="hero wrap">
      <div className="hero-copy"><div className="eyebrow"><span className="eyebrow-line" /> YOUR NEXT CHAPTER STARTS HERE</div><h1>Prepare with purpose.<br /><em>Show them what</em><br />you can do.</h1><p className="hero-text">A calmer, clearer way to get ready for placements. Find roles to explore, sharpen your interview skills, and see your progress take shape.</p><div className="hero-actions"><Link className="button" to="/jobs">Explore opportunities <ArrowRight size={17} /></Link><Link className="text-link" to="/quiz"><CirclePlay size={17} /> Try a practice quiz</Link></div><div className="hero-note"><span className="avatars"><i>J</i><i>A</i><i>R</i></span><span>One focused step at a time</span></div></div>
      <div className="hero-visual"><div className="visual-orbit orbit-one"/><div className="visual-orbit orbit-two"/><div className="visual-card main-card"><div className="card-top"><span className="mini-label">YOUR WEEKLY FOCUS</span><span className="live-dot" /></div><div className="focus-icon"><Compass size={22} /></div><h3>Small steps.<br />Real momentum.</h3><p>Your preparation, gathered in one place.</p><div className="progress-label"><span>Week 01</span><span>Getting started</span></div><div className="progress-track"><span /></div></div><div className="floating-tag tag-quiz"><span className="tag-icon lilac"><Sparkles size={16} /></span><span><b>Practice</b><small>Keep your skills fresh</small></span></div><div className="floating-tag tag-roles"><span className="tag-icon green"><BriefcaseBusiness size={16} /></span><span><b>Explore roles</b><small>Find your next step</small></span><ArrowDownRight className="tag-arrow" size={17} /></div><span className="visual-caption">A little progress adds up.</span></div>
      <span className="hero-index">01 — 03</span>
    </section>
    <section className="trust-strip"><div className="wrap trust-inner"><span>MADE FOR THE MOMENT BEFORE YOUR FIRST BIG YES</span><div><i>Learn</i><b>·</b><i>Practise</i><b>·</b><i>Progress</i></div></div></section>
    <section className="section wrap"><div className="section-heading"><div><div className="eyebrow"><span className="eyebrow-line" /> YOUR PREPARATION, IN THREE PARTS</div><h2>Everything you need to<br /><em>feel ready.</em></h2></div><p>Go at your own pace. Start anywhere, and let each step make the next one easier.</p></div><div className="steps-grid">{steps.map(({ icon: Icon, number, title, text }) => <article className="step-card" key={number}><div className="step-card-top"><span className="step-icon"><Icon size={20} /></span><span>{number}</span></div><h3>{title}</h3><p>{text}</p><Link to={number === '01' ? '/jobs' : number === '02' ? '/quiz' : '/dashboard'} aria-label={`Explore ${title}`}><ArrowRight size={18} /></Link></article>)}</div></section>
    <section className="cta-wrap"><div className="cta-panel wrap"><span className="cta-spark">✳</span><div><div className="eyebrow eyebrow-light">READY WHEN YOU ARE</div><h2>Your next step is<br /><em>already within reach.</em></h2></div><Link className="button button-cream" to="/register">Create your free account <ArrowRight size={17} /></Link></div></section>
  </>
}
