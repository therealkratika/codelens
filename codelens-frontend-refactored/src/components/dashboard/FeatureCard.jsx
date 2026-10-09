import { useNavigate } from "react-router-dom";
export default function FeatureCard({ to, icon, title, description, action }) {
  const navigate = useNavigate();
  return <button className="tool-card" onClick={() => navigate(to)}><div className="tool-icon lavender">{icon}</div><h3>{title}</h3><p>{description}</p><span>{action || "Explore →"}</span></button>;
}
