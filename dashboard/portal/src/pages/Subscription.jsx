import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';

const planIcons = { starter: '🔍', professional: '🛒', enterprise: '🏢', full_suite: '🚀', compliance_pack: '⚖️',
  regulatory_starter: '🧠', regulatory_professional: '⚖️', regulatory_full: '🏛️', esg_carbon_pack: '🌱' };
const planColors = { starter: '#3b82f6', professional: '#8b5cf6', enterprise: '#f59e0b', full_suite: '#10b981',
  compliance_pack: '#ef4444', regulatory_starter: '#6366f1', regulatory_professional: '#8b5cf6',
  regulatory_full: '#7c3aed', esg_carbon_pack: '#059669' };

export default function Subscription() {
  const { t } = useTranslation();
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

  if (loading) return <div className="loading">{t('subscription.loading')}</div>;

  return (
    <div className="subscription-page">
      <h1>💳 {t('subscription.title')}</h1>
      <p className="subtitle">{t('subscription.subtitle')}</p>

      <div className="plans-grid">
        {plans.map((plan) => (
          <div key={plan.id} className="plan-card"
               style={{ borderTop: `4px solid ${planColors[plan.id] || '#3b82f6'}` }}>
            <div className="plan-icon">{planIcons[plan.id] || '🤖'}</div>
            <h3>{plan.name}</h3>
            <div className="plan-price">{formatPrice(plan.price)}<span>{t('subscription.per_month')}</span></div>
            <div className="plan-agent-count">
              {plan.agents.length} {plan.agents.length === 1 ? t('subscription.agent') : t('subscription.agents')}
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
              {checkoutLoading === plan.id ? t('subscription.redirecting') : t('subscription.subscribe')}
            </button>
          </div>
        ))}
      </div>

      <div className="upgrade-info" style={{ marginTop: 32, padding: 20, background: '#f8fafc', borderRadius: 12 }}>
        <h3>🔄 {t('subscription.upgrade_title')}</h3>
        <p>{t('subscription.upgrade_path')}</p>
        <p style={{ fontSize: '0.9rem', color: '#64748b' }}>
          {t('subscription.trial_info')}
        </p>
      </div>
    </div>
  );
}
