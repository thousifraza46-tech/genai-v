import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import HomePage from "./pages/HomePage";
import AIAssistance from "./pages/AIAssistance";
import GenerateVideo from "./pages/GenerateVideo";
import Animation from "./pages/Animation";
import History from "./pages/History";
import Personalization from "./pages/Personalization";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";
import EditorLab from "./pages/EditorLab";

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route element={<Layout />}>
          <Route path="/app" element={<AIAssistance />} />
          <Route path="/generate-video" element={<GenerateVideo />} />
          <Route path="/animation" element={<Animation />} />
          <Route path="/history" element={<History />} />
          <Route path="/personalization" element={<Personalization />} />
          <Route path="/editor-lab" element={<EditorLab />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
