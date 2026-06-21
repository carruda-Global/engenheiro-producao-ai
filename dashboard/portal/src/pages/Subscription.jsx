import { useState, useEffect } from 'react';
import { api } from '../api/client';

const planIcons = { starter: '🔍', professional: '🛒', enterprise: '🏢', full_suite: '🚀', compliance_pack: '⚖️' };
const planColors = { starter: '#3b82f6', professional: '#8b5cf6', enterprise: '#f59e0b', full_suite: '#10b981', compliance_pack: '#ef4444' };

export default function Subscription() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [checkoutLoading, setCheckoutLoading] = useState(null);

  useEffect(() => {
    api.plans()
      .then((d) => setPlans(d.plans))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const formatPrice = (cents) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(cents / 100);

  const handleSubscribe = async (planId) => {
    setCheckoutLoading(planId);
    try {
      const data = await api.createCheckout(planId);
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        alert('Erro ao criar checkout. Tente novamente.');
      }
    } catch (err) {
      alert('Erro: ' + err.message);
    } finally {
      setCheckoutLoading(null);
    }
  };

  if (loading) return <div className="loading">Carregando planos...</div>;

  const featured = 'full_suite';

  return (
    <div className="subscription-page">
      <h1>💳 Planos e Assinaturas</h1>
      <p className="subtitle">Escolha o plano ideal para sua empresa de engenharia</p>

      <div className="plans-grid">
        {plans.map((plan) => (
          <div key={plan.id} className={`plan-card ${plan.id === featured ? 'featured' : ''}`}
               style={{ borderTop: `4px solid ${planColors[plan.id] || '#3b82f6'}` }}>
            <div className="plan-icon">{planIcons[plan.id] || '🤖'}</div>
            <h3>{plan.name}</h3>
            <div className="plan-price">{formatPrice(plan.price)}<span>/mes</span></div>
            <div className="plan-agent-count">
              {plan.agents.length} {plan.agents.length === 1 ? 'agente' : 'agentes'}
            </div>
            <ul className="plan-features">
              {plan.features.map((f, i) => (
                <li key={i}>{f}</li>
              ))}
            </ul>
            <div className="plan-agents">
              {plan.agents.map((a) => (
                <span key={a} className="tag">{a}</span>
              ))}
            </div>
            <button
              className="btn-primary"
              onClick={() => handleSubscribe(plan.id)}
              disabled={checkoutLoading === plan.id}
            >
              {checkoutLoading === plan.id ? 'Redirecionando...' : 'Assinar Agora'}
            </button>
          </div>
        ))}
      </div>

      <div className="upgrade-info" style={{ marginTop: 32, padding: 20, background: '#f8fafc', borderRadius: 12 }}>
        <h3>🔄 Upgrade a qualquer momento</h3>
        <p>Starter → Professional → Enterprise → Full Suite</p>
        <p style={{ fontSize: '0.9rem', color: '#64748b' }}>
          Todos os planos incluem 15 dias de trial gratuito. Cancele quando quiser.
        </p>
      </div>
    </div>
  );
}
