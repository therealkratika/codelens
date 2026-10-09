import { Navigate, Route, Routes } from "react-router-dom";
import { RepositoryProvider, useRepository } from "./context/RepositoryContext";
import AppLayout from "./components/layout/AppLayout";
import ImportPage from "./pages/ImportPage";
import DashboardPage from "./pages/DashboardPage";
import ArchitecturePage from "./pages/ArchitecturePage";
import CodeExplorerPage from "./pages/CodeExplorerPage";
import ChunksPage from "./pages/ChunksPage";
import ChatPage from "./pages/ChatPage";
import RepositoriesPage from "./pages/RepositoriesPage";
import SettingsPage from "./pages/SettingsPage";
import "./styles/global.css";
import "./styles/layout.css";
import "./styles/components.css";
import "./styles/pages.css";
function ProtectedWorkspace() {
  const { activeRepository } = useRepository();
  return activeRepository ? <AppLayout/> : <Navigate to="/" replace/>;
}
export default function App() {
  return <RepositoryProvider><Routes>
    <Route path="/" element={<ImportPage/>}/>
    <Route element={<ProtectedWorkspace/>}>
      <Route path="/dashboard" element={<DashboardPage/>}/>
      <Route path="/repositories" element={<RepositoriesPage/>}/>
      <Route path="/architecture" element={<ArchitecturePage/>}/>
      <Route path="/code" element={<CodeExplorerPage/>}/>
      <Route path="/chunks" element={<ChunksPage/>}/>
      <Route path="/chat" element={<ChatPage/>}/>
      <Route path="/settings" element={<SettingsPage/>}/>
    </Route>
    <Route path="*" element={<Navigate to="/" replace/>}/>
  </Routes></RepositoryProvider>;
}
