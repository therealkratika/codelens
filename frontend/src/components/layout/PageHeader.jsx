export default function PageHeader({ eyebrow, title, description, action }) {
  return <div className="welcome-row"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1>{description && <p className="muted">{description}</p>}</div>{action}</div>;
}
