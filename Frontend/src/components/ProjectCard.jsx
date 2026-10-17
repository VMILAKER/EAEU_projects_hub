import { useState } from 'react'

function groupByCountry(participants = []) {
  const groups = {}
  for (const item of participants) {
    const [country, name] = Object.entries(item)[0] || []
    if (!country) continue
    ;(groups[country] ||= []).push(name)
  }
  return groups
}

export default function ProjectCard({ project }) {
  const [expanded, setExpanded] = useState(false)
  const facts = project.key_facts ? project.key_facts.split(';').map((f) => f.trim()).filter(Boolean) : []
  const participants = groupByCountry(project.participants)

  return (
    <article className="card project">
      <div className="project__tags">
        {project.scope && <span className="tag tag--scope">{project.scope}</span>}
        {project.stage && <span className="tag tag--stage">{project.stage}</span>}
      </div>

      <h3 className="project__title">{project.project_name}</h3>
      {project.description && <p className="project__description">{project.description}</p>}

      {Object.keys(participants).length > 0 && (
        <div className="project__section">
          <h4>Участники</h4>
          {Object.entries(participants).map(([country, names]) => (
            <div key={country} className="participants">
              <span className="participants__country">{country}:</span> {names.join(', ')}
            </div>
          ))}
        </div>
      )}

      {expanded && facts.length > 0 && (
        <div className="project__section">
          <h4>Ключевые факты</h4>
          <ul className="facts">
            {facts.map((fact, i) => (
              <li key={i}>{fact}</li>
            ))}
          </ul>
        </div>
      )}

      {expanded && project.links?.length > 0 && (
        <div className="project__section">
          <h4>Источники</h4>
          <ul className="links">
            {project.links.map((link) => (
              <li key={link}>
                <a href={link} target="_blank" rel="noreferrer">
                  {link}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}

      {(facts.length > 0 || project.links?.length > 0) && (
        <button className="btn btn--link" onClick={() => setExpanded((v) => !v)}>
          {expanded ? 'Свернуть' : 'Ключевые факты и источники'}
        </button>
      )}
    </article>
  )
}
