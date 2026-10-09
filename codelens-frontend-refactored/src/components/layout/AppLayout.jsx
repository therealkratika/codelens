import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import ErrorMessage from "../common/ErrorMessage";
import { useRepository } from "../../context/RepositoryContext";
export default function AppLayout() {
  const { health, activeRepository, error, setError, goToImport } = useRepository();
  return <div className="app-shell"><Sidebar health={health} onImport={goToImport}/><main className="main-area"><Topbar health={health} activeRepository={activeRepository} onImport={goToImport}/><div className="page-content"><ErrorMessage message={error} onDismiss={() => setError("")}/><Outlet/><footer className="footer"><span>CodeLens · Understand your codebase</span><span>AI-powered codebase intelligence</span></footer></div></main></div>;
}
