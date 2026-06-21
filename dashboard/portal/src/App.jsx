import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import AgentDetail from './pages/AgentDetail';
import Subscription from './pages/Subscription';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/agent/:agentId" element={<AgentDetail />} />
          <Route path="/subscription" element={<Subscription />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
