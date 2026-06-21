import { useState, useEffect } from 'react';
import AgentCard from '../components/AgentCard';

const agents = [
  { id: 'spec-analyst', icon: '🔍', title: 'Spec Analyst', description: 'Analise de especificacoes tecnicas, normas e documentos de engenharia.', tags: ['1M tokens', 'OCR'] },
  { id: 'procurement', icon: '🛒', title: 'Procurement', description: 'Compras automatizadas, comparacao de cotacoes e geracao de pedidos.', tags: ['Cross-selling'] },
  { id: 'inventory', icon: '📦', title: 'Inventory', description: 'Monitoramento de estoque, alertas de escassez e sugestao de substitutos.', tags: ['Tempo real'] },
  { id: 'logistics', icon: '🚚', title: 'Logistics', description: 'Rastreamento de entregas, identificacao de problemas e notas fiscais.', tags: ['Tracking'] },
  { id: 'field-execution', icon: '🏗️', title: 'Field Execution', description: 'Instrucoes de obra, identificacao de desvios e reducao de retrabalho.', tags: ['BIM', 'RA'] },
  { id: 'bim-coordinator', icon: '📐', title: 'BIM Coordinator', description: 'Criacao de elementos 3D, clash detection e validacao de modelos BIM.', tags: ['BIM', '3D'] },
  { id: 'requirements-analyst', icon: '📋', title: 'Requirements Analyst', description: 'Analise de qualidade de requisitos, scores e deteccao de ambiguidades.', tags: ['Qualidade'] },
  { id: 'engineering-assistant', icon: '💬', title: 'Engineering Assistant', description: 'Assistente conversacional para perguntas tecnicas e sumarizacao.', tags: ['Chat', 'IA'] },
  { id: 'work-synopsis', icon: '📝', title: 'Work Synopsis', description: 'Resumo estruturado de tarefas, defeitos e status de obra.', tags: ['Resumo'] },
  { id: 'photo-intelligence', icon: '📸', title: 'Photo Intelligence', description: 'Analise visual de obras, deteccao de riscos e comparacao com cronograma.', tags: ['Visao'] },
  { id: 'rfi-creation', icon: '📄', title: 'RFI Creation', description: 'Criacao automatica de RFIs a partir de duvidas do campo.', tags: ['RFI', 'Docs'] },
  { id: 'compliance', icon: '⚖️', title: 'Compliance Agent', description: 'Gestao de conformidade PGRS/PGRSS e monitoramento regulatorio.', tags: ['PGRS', 'Normas'] },
];

export default function Dashboard() {
  const [health, setHealth] = useState(null);
  const [apiOk, setApiOk] = useState(false);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL || ''}/health`)
      .then((r) => r.json())
      .then((d) => { setHealth(d); setApiOk(true); })
      .catch(() => setApiOk(false));
  }, []);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <div className={`status-badge ${apiOk ? 'online' : 'offline'}`}>
          {apiOk ? 'API Online' : 'API Offline'}
        </div>
      </div>

      {health && (
        <div className="health-bar">
          <span>🤖 Agentes: {health.agents?.join(', ') || 'N/A'}</span>
          <span>🧠 DeepSeek: {health.deepseek === 'connected' ? 'Conectado' : 'Desconectado'}</span>
          <span>📦 Versao: {health.version}</span>
        </div>
      )}

      <div className="agent-grid">
        {agents.map((a) => (
          <AgentCard key={a.id} {...a} />
        ))}
      </div>
    </div>
  );
}
