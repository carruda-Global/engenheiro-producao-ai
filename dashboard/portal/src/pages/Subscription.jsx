import { useState, useEffect } from 'react';
import { api } from '../api/client';

const planIcons = { starter: '🔍', professional: '🛒', enterprise: '🏢', full_suite: '🚀' };

export default function Subscription() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.plans()
      .then((d) => setPlans(d.plans))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const formatPrice = (cents) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(cents / 100);

  if (loading) return <div className="loading">Carregando planos...</div>;

  return (
    <div className="subscription-page">
      <h1>💳 Planos e Assinaturas</h1>
      <p className="subtitle">Escolha o plano ideal para sua empresa</p>

      <div className="plans-grid">
        {plans.map((plan) => (
          <div key={plan.id} className={`plan-card ${plan.id === 'full_suite' ? 'featured' : ''}`}>
            <div className="plan-icon">{planIcons[plan.id] || '🤖'}</div>
            <h3>{plan.name}</h3>
            <div className="plan-price">{formatPrice(plan.price)}<span>/mes</span></div>
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
            <button className="btn-primary" onClick={() => window.open('#', '_blank')}>
              Assinar
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
