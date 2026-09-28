import React from "react";

const assetUrl = (fileName) => `${import.meta.env.BASE_URL}images/${fileName}`;

const cards = [
  {
    slug: "about",
    eyebrow: "Profile",
    title: "About Me",
    subtitle: "Human Performance • Tactical Readiness • EHS",
    image: null,
    details: [
      "Master’s-level education in Exercise Science",
      "Applied focus in mental performance, injury prevention, and biomechanics",
      "Experience translating performance science into tactical and high-stakes environments",
      "EHS and ergonomics focus centered on safer, more sustainable human performance"
    ],
    whyItMatters:
      "I connect performance science with the realities of demanding work: movement quality, readiness, recovery, safety, and decision-making."
  },
  {
    slug: "mental-performance",
    eyebrow: "Cognitive Performance",
    title: "Mental Performance",
    subtitle: "Focus, Resilience & Performance Under Pressure",
    image: "mental-performance.gif",
    mediaClass: "object-cover object-center",
    details: [
      "Performance psychology and pre-performance routines",
      "Cognitive drills performed under controlled stress",
      "Breathing, visualization, and attentional-control strategies",
      "Recovery tracking and feedback to support consistency"
    ],
    whyItMatters:
      "Physical capacity is only part of performance. Focus, composure, and repeatable decision-making matter when pressure rises."
  },
  {
    slug: "military-performance",
    eyebrow: "Tactical Human Performance",
    title: "Military Performance",
    subtitle: "Readiness Built for Operational Demands",
    image: "military-performance.gif",
    mediaClass: "object-cover object-center",
    details: [
      "Tactical movement and task-specific conditioning",
      "Load-bearing endurance and work-capacity development",
      "Stress-exposure drills that combine physical and cognitive demand",
      "Hydration and recovery planning for high-heat environments",
      "Power, acceleration, and repeated-effort development"
    ],
    whyItMatters:
      "Training should transfer to the task. Programming must account for equipment, fatigue, terrain, time pressure, and repeated high-output work."
  },
  {
    slug: "nutrition",
    eyebrow: "Performance Nutrition",
    title: "Nutrition",
    subtitle: "Fueling Performance, Recovery & Readiness",
    image: "nutrition.gif",
    mediaClass: "object-contain object-center p-3",
    details: [
      "Macro- and micronutrient planning for training demands",
      "Hydration and electrolyte strategies under physical stress",
      "Meal timing around performance and recovery",
      "Practical nutrition systems for high-output schedules"
    ],
    whyItMatters:
      "Nutrition supports energy availability, recovery, concentration, and the ability to sustain high-quality work across demanding schedules."
  },
  {
    slug: "biomechanics",
    eyebrow: "Movement Science",
    title: "Biomechanics",
    subtitle: "Analyze Movement. Improve Efficiency.",
    image: "biomechanics-pitch.gif",
    mediaClass: "object-cover object-center",
    details: [
      "Kinematic analysis of joint and segment motion",
      "Movement-efficiency and technique diagnostics",
      "Identification of mechanical patterns linked to excessive loading",
      "Translation of movement findings into practical training changes"
    ],
    whyItMatters:
      "Biomechanics turns movement into measurable information, helping refine technique while reducing unnecessary mechanical stress."
  },
  {
    slug: "injury-prevention",
    eyebrow: "Durability",
    title: "Injury Prevention",
    subtitle: "Build Capacity Before Breakdown",
    image: "injury-prevention.avif",
    mediaClass: "object-cover object-center",
    details: [
      "Prehabilitation for common high-demand regions",
      "Mobility, strength balance, and movement-quality work",
      "Progressive return-to-performance planning",
      "Training-load management and recovery integration"
    ],
    whyItMatters:
      "The goal is not simply to avoid injury; it is to build enough capacity that the body can tolerate the work it is repeatedly asked to perform."
  },
  {
    slug: "ehs-ergonomics",
    eyebrow: "Workplace Performance",
    title: "EHS & Ergonomics",
    subtitle: "Safety Systems That Support Human Performance",
    image: "ehs-card-image.png",
    mediaClass: "object-contain object-center p-4",
    details: [
      "Ergonomic task and workstation assessments",
      "Job hazard analysis for higher-risk work",
      "Root-cause analysis for incidents and near-misses",
      "Data-driven ergonomics reporting and corrective-action tracking",
      "PPE compliance, fit considerations, and practical field implementation",
      "Mobility and fatigue-management strategies for industrial populations"
    ],
    whyItMatters:
      "Strong EHS systems reduce preventable exposure while supporting reliable output, better work design, and long-term workforce durability."
  },
  {
    slug: "research",
    eyebrow: "Evidence & Application",
    title: "My Research",
    subtitle: "Applied Human Performance Questions",
    image: null,
    details: [
      "Sprint mechanics and hamstring-injury risk",
      "Sleep, resilience, and readiness in tactical populations",
      "Energy-system demands in field and high-performance athletes",
      "Translating research findings into usable training and workplace decisions"
    ],
    whyItMatters:
      "Research is most useful when it improves a real decision: how to train, recover, design work, reduce risk, or sustain performance."
  }
];

function Media({ card }) {
  if (!card.image) return null;

  return (
    <div className="card-media">
      <img
        src={assetUrl(card.image)}
        alt={`${card.title} visual`}
        className={`card-image ${card.mediaClass ?? "object-cover object-center"}`}
        loading="lazy"
        decoding="async"
      />
      <div className="card-media-overlay" aria-hidden="true" />
    </div>
  );
}

function FocusCard({ card, index }) {
  return (
    <article
      id={card.slug}
      className="performance-card group"
      style={{ "--card-delay": `${index * 55}ms` }}
    >
      <Media card={card} />

      <div className="card-content">
        <div className="card-number" aria-hidden="true">
          {String(index + 1).padStart(2, "0")}
        </div>

        <p className="card-eyebrow">{card.eyebrow}</p>
        <h2 className="card-title">{card.title}</h2>
        <p className="card-subtitle">{card.subtitle}</p>

        <ul className="card-list">
          {card.details.map((point) => (
            <li key={point}>{point}</li>
          ))}
        </ul>

        <div className="why-block">
          <span className="why-label">Why it matters</span>
          <p>{card.whyItMatters}</p>
        </div>

      </div>
    </article>
  );
}

const analyticsProjects = [
  { title: "Data Quality Inspector", domain: "Data Quality / Python", tools: "Python · Pandas · NumPy · Matplotlib · Automated Testing", status: "Featured", description: "I built a reusable CSV inspection tool that profiles structure, identifies missing and duplicate records, validates expected types, flags potential outliers, and generates a clear report with supporting visualizations.", href: "https://github.com/Rhayko/DataQualityInspector", featured: true },
  { title: "SQL Investigation Lab", domain: "Business Investigation / SQL", tools: "SQL · SQLite · JOINs · CTEs · Window Functions · Python", status: "Featured", description: "I built a seven-table investigation to explain why stable revenue can still produce declining contribution margin. The analysis traces discounting, location-level operating costs, and product returns through reproducible SQL queries.", href: "https://github.com/Rhayko/SQLInvestigationLab", featured: true },
  { title: "NBA Lineup & Fatigue Analytics Lab", domain: "Sports Analytics / Human Performance", tools: "SQL · Python · SQLite · Pandas · Workload Analysis", status: "New", description: "I investigated how lineup efficiency changes across recent workload, rest, travel, and game phase. The project uses possession-weighted ratings to identify late-game situations worth closer coaching and performance review without treating association as causation.", href: "https://github.com/Rhayko/NBALineupFatigueAnalyticsLab", external: true },
  { title: "Operations KPI Dashboard", domain: "Operations / Manufacturing", tools: "Excel · PivotTables · SUMIFS · Lookup Logic · KPI Design", status: "Completed", description: "Investigate dispatch reliability, workload and throughput across 528 synthetic shift records. Includes a working Excel dashboard, validation checks, source data and a reproducible generator.", path: "operations-kpi" },
  { title: "Business & Sales Analysis", domain: "Business / Sales", tools: "SQL · JOINs · CTEs · Window Functions · Power BI Measures", status: "Completed", description: "Trace 2,400 synthetic orders from gross sales to contribution after returns, fulfillment and marketing. The SQL model protects each metric's grain and includes a Power BI handoff.", path: "business-operations" },
  { title: "Workforce Planning Analysis", domain: "Workforce / HR", tools: "Python · Pandas · Data Quality · Confidence Intervals · Hypothesis Testing", status: "Completed", description: "Examine department-level turnover, overtime, absence and missing engagement scores for 720 fictional employees without turning associations into individual risk claims.", path: "workforce-analysis" },
  { title: "Human Performance Research", domain: "Human Performance / Research", tools: "Python · NumPy · Matplotlib · Correlation · Regression", status: "Completed", description: "Analyze 96 synthetic participant pairs across rested and restricted conditions using descriptive statistics, a paired comparison, correlation and simple regression.", path: "human-performance" }
];

function DataPortfolio() {
  return (
    <section className="analytics-section" id="data-analytics" aria-labelledby="analytics-title">
      <div className="analytics-heading">
        <div>
          <p className="section-kicker">Data & Analytics</p>
          <h2 id="analytics-title">Turning raw data<br />into decisions.</h2>
        </div>
        <p>I use data analysis, visualization, and process improvement to transform operational and performance data into clear, actionable information.</p>
      </div>
      <ul className="analytics-skills" aria-label="Analytics skills">
        {["Python", "SQL", "Excel", "Power BI", "SPSS", "Data Cleaning", "Data Visualization", "KPI Analysis", "Statistical Analysis"].map(skill => <li key={skill}>{skill}</li>)}
      </ul>
      <div className="portfolio-caption"><span>Independent portfolio projects</span><span>07 / Completed projects</span></div>
      <div className="analytics-grid">
        {analyticsProjects.map((project, index) => (
          <article className={`analytics-project ${project.featured ? "analytics-project-featured" : ""}`} key={project.title}>
            <div className="project-topline"><span className="project-index">{String(index + 1).padStart(2, "0")}</span><span className="project-status">{project.status}</span></div>
            <div className="project-body">
              <div>
                <p className="project-domain">{project.domain}</p>
                <h3>{project.title}</h3>
                <p className="project-tools">{project.tools}</p>
              </div>
              <div>
                <p className="project-description">{project.description}</p>
                <a className="resource-link project-link" href={project.href ?? `${import.meta.env.BASE_URL}projects/${project.path}/index.html`} target={project.href ? "_blank" : undefined} rel={project.href ? "noopener noreferrer" : undefined}>{project.href ? "Explore the GitHub project" : "View case study & downloads"} <span aria-hidden="true">↗</span></a>
              </div>
            </div>
            <p className="project-disclosure">Independent Portfolio Project <span aria-hidden="true">|</span> Synthetic Dataset</p>
          </article>
        ))}
      </div>
      <p className="portfolio-note">Projects use synthetic datasets to demonstrate analytical methods and business decisions.</p>
    </section>
  );
}

export default function ExerciseScienceSite() {
  const year = new Date().getFullYear();

  return (
    <div className="site-shell">
      <a className="skip-link" href="#disciplines">Skip to disciplines</a>
      <header className="hero" id="top">
        <nav className="top-nav" aria-label="Main navigation">
          <a className="wordmark" href="#top">ZEROED <span>IN</span><span className="brand-dot" aria-hidden="true" /></a>
          <div className="top-links">
            <a href="#about">About</a>
            <a href="#data-analytics">Data & Analytics</a>
            <a href="#disciplines">Disciplines</a>
            <a href="#research">Research</a>
          </div>
          <a className="nav-contact" href="mailto:Rhayko.schwartz@gmail.com">Let’s connect <span aria-hidden="true">↗</span></a>
        </nav>

        <div className="hero-inner">
          <div className="hero-stage">
            <div className="hero-side hero-side-left">
              <p className="side-kicker">The disciplines</p>
              <p>Mind. Body.<br />Mission.</p>
              <span>Science-driven readiness</span>
            </div>
            <div className="hero-graphic">
              <img
                className="hero-image"
                src={assetUrl("human performance.png")}
                alt="Zeroed In Human Performance: tactical operator with strength, resilience, focus, and purpose branding"
                width="1254"
                height="1254"
                fetchPriority="high"
              />
            </div>
            <div className="hero-side hero-side-right">
              <p className="side-kicker">The impact</p>
              <p>Built for<br />real demands.</p>
              <span>Performance with purpose</span>
            </div>
          </div>

          <p className="hero-kicker">Human Performance • Tactical Readiness • EHS</p>
          <h1 className="hero-title"><span>Zeroed In</span></h1>
          <p className="hero-byline">By Rhayko</p>
          <p className="hero-copy">
            Applied performance science for athletes, tactical populations, and
            high-demand workplaces. Built for readiness. Designed for impact.
          </p>

          <nav className="quick-nav" aria-label="Explore disciplines">
            <a href="#mental-performance">Mental</a>
            <a href="#military-performance">Military</a>
            <a href="#biomechanics">Biomechanics</a>
            <a href="#ehs-ergonomics">EHS</a>
            <a href="#research">Research</a>
          </nav>
          <div className="recruiter-actions" aria-label="Portfolio resources">
            <a className="hero-cta" href="#data-analytics">View Data Portfolio <span aria-hidden="true">↗</span></a>
            <a className="resource-link" href="https://github.com/Rhayko" target="_blank" rel="noopener noreferrer">View GitHub <span aria-hidden="true">↗</span></a>
          </div>
          <a className="scroll-cue" href="#disciplines"><span>Scroll to explore</span><span aria-hidden="true">↓</span></a>
        </div>
      </header>

      <main className="content-wrap">
        <DataPortfolio />
        <section id="disciplines" aria-label="Core disciplines">
        <div className="section-heading">
          <div>
            <p className="section-kicker">Core disciplines</p>
            <h2>Performance systems, not isolated pieces.</h2>
          </div>
          <p>
            Each discipline is treated as part of one system: how people move,
            think, recover, work, and perform under real constraints.
          </p>
        </div>

        <section className="cards-grid" aria-label="Areas of expertise">
          {cards.map((card, index) => (
            <FocusCard key={card.slug} card={card} index={index} />
          ))}
        </section>

        </section>
      </main>

      <footer className="site-footer">
        <div>
          <strong>Zeroed In</strong>
          <span>Elite Human Performance Systems</span>
        </div>

        <div className="footer-meta">
          <a href="mailto:Rhayko.schwartz@gmail.com">
            Rhayko.schwartz@gmail.com
          </a>
          <span>© {year} All rights reserved.</span>
        </div>
      </footer>
    </div>
  );
}
