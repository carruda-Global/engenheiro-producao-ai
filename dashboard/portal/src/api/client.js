const API_BASE = import.meta.env.VITE_API_URL || '';

async function request(path, options = {}) {
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: { message: res.statusText } }));
    throw new Error(err.error?.message || err.detail || 'Erro na requisicao');
  }
  return res.json();
}

export const api = {
  health: () => request('/health'),
  agents: () => request('/api/v1/agents'),
  analyzeDocument: (document) =>
    request('/api/v1/agents/spec-analyst/analyze', {
      method: 'POST', body: JSON.stringify({ document }),
    }),
  processOrder: (materials) =>
    request('/api/v1/agents/procurement/process-order', {
      method: 'POST', body: JSON.stringify({ materials }),
    }),
  checkStock: (items) =>
    request('/api/v1/agents/inventory/check-stock', {
      method: 'POST', body: JSON.stringify({ items }),
    }),
  trackShipment: (shipment) =>
    request('/api/v1/agents/logistics/track-shipment', {
      method: 'POST', body: JSON.stringify({ shipment }),
    }),
  fieldInstructions: (specs) =>
    request('/api/v1/agents/field-execution/instructions', {
      method: 'POST', body: JSON.stringify({ specs }),
    }),
  agentAction: (agentId, action, data) =>
    request(`/api/v1/agents/${agentId}/${action}`, {
      method: 'POST', body: JSON.stringify(data),
    }),
  runWorkflow: (document) =>
    request('/api/v1/agents/workflow', {
      method: 'POST', body: JSON.stringify({ document }),
    }),
  plans: () => request('/api/v1/subscriptions/plans'),
  getPlan: (id) => request(`/api/v1/subscriptions/plans/${id}`),
  createCheckout: (planId, successUrl, cancelUrl) =>
    request('/api/v1/subscriptions/checkout', {
      method: 'POST',
      body: JSON.stringify({
        plan_id: planId,
        success_url: successUrl || window.location.origin + '/subscription?success=true',
        cancel_url: cancelUrl || window.location.origin + '/subscription?canceled=true',
      }),
    }),
  upgradePlan: (subscriptionId, newPlanId) =>
    request('/api/v1/cross-selling/upgrade/' + newPlanId),
  getUpsells: (planId) => request('/api/v1/cross-selling/upsell/' + planId),
};
