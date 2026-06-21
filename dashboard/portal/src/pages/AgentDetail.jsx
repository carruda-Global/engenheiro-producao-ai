import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../api/client';

const agentConfig = {
  'spec-analyst': {
    name: 'Spec Analyst', icon: '🔍',
    description: 'Analise documentos de engenharia para extrair requisitos e nao-conformidades.',
    fields: [{ key: 'document', label: 'Documento', type: 'textarea', placeholder: 'Cole o documento de engenharia aqui...' }],
    action: (d) => api.analyzeDocument(d.document),
  },
  procurement: {
    name: 'Procurement', icon: '🛒',
    description: 'Processe pedidos de compra e compare cotacoes de fornecedores.',
    fields: [{ key: 'materials', label: 'Materiais (JSON)', type: 'textarea', placeholder: '[{"name": "Cimento", "quantity": 100, "unit": "kg"}]' }],
    action: (d) => api.processOrder(JSON.parse(d.materials || '[]')),
  },
  inventory: {
    name: 'Inventory', icon: '📦',
    description: 'Monitore estoque, receba alertas de escassez e sugira substitutos.',
    fields: [{ key: 'items', label: 'Itens (JSON)', type: 'textarea', placeholder: '[{"name": "Cimento", "stock": 10, "min_stock": 20, "daily_use": 5}]' }],
    action: (d) => api.checkStock(JSON.parse(d.items || '[]')),
  },
  logistics: {
    name: 'Logistics', icon: '🚚',
    description: 'Acompanhe envios e identifique problemas de entrega.',
    fields: [{ key: 'shipment', label: 'Dados do Envio (JSON)', type: 'textarea', placeholder: '{"product": "Cimento", "origin": "SP", "destination": "RJ", "status": "em_transito"}' }],
    action: (d) => api.trackShipment(JSON.parse(d.shipment || '{}')),
  },
  'field-execution': {
    name: 'Field Execution', icon: '🏗️',
    description: 'Gere instrucoes de execucao para equipe em campo.',
    fields: [{ key: 'specs', label: 'Especificacoes do Projeto', type: 'textarea', placeholder: 'Descreva o projeto e as especificacoes tecnicas...' }],
    action: (d) => api.fieldInstructions(d.specs),
  },
};

export default function AgentDetail() {
  const { agentId } = useParams();
  const config = agentConfig[agentId];
  const [form, setForm] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!config) return <div className="error-page">Agente nao encontrado</div>;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await config.action(form);
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="agent-detail">
      <h1>{config.icon} {config.name}</h1>
      <p className="agent-description">{config.description}</p>

      <form onSubmit={handleSubmit} className="agent-form">
        {config.fields.map((f) => (
          <div key={f.key} className="form-group">
            <label>{f.label}</label>
            {f.type === 'textarea' ? (
              <textarea
                rows={6}
                placeholder={f.placeholder}
                value={form[f.key] || ''}
                onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}
              />
            ) : (
              <input
                type="text"
                placeholder={f.placeholder}
                value={form[f.key] || ''}
                onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}
              />
            )}
          </div>
        ))}
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? 'Processando...' : 'Executar'}
        </button>
      </form>

      {error && <div className="error-box">Erro: {error}</div>}

      {result && (
        <div className="result-box">
          <h3>Resultado</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
