const {
  createApp,
  Bundle,
  ZObject,
} = require("zapier-platform-core");

const App = createApp({
  version: require("./package.json").version,
  platformVersion: require("zapier-platform-core").version,

  title: "AION Compliance",
  description:
    "106 agentes de IA para compliance regulatorio: NR-1, LGPD, EU AI Act, CSRD, DORA, NIS2, SOC2, ISO27001. Automatize checks de compliance nos seus contatos e empresas do HubSpot, Pipefy e mais.",

  authentication: {
    type: "custom",
    test: {
      url: "{{bundle.authData.base_url}}/api/agents/health",
      method: "GET",
    },
    fields: [
      {
        key: "api_key",
        label: "API Key",
        type: "string",
        required: true,
        helpText: "Sua chave de API do AION. Obtenha em https://engenheiro-producao-ai.onrender.com",
      },
      {
        key: "base_url",
        label: "API Base URL",
        type: "string",
        required: false,
        default: "https://engenheiro-producao-ai.onrender.com",
        helpText: "URL base da API AION",
      },
    ],
  },

  requestTemplate: {
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer {{bundle.authData.api_key}}",
    },
  },

  triggers: {
    new_compliance_check: {
      key: "new_compliance_check",
      noun: "Compliance Check",
      display: {
        label: "New Compliance Check",
        description: "Triggers when a new compliance check is completed.",
      },
      operation: {
        inputFields: [
          {
            key: "service",
            type: "string",
            required: false,
            helpText: "Filter by service (ex: compliance-nr1, compliance-lgpd, compliance-eu-ai-act)",
          },
        ],
        perform: async (z, bundle) => {
          const url = `${bundle.authData.base_url}/api/tasks?status=completed`;
          const response = await z.request({
            url,
            method: "GET",
          });
          return response.data?.tasks || [];
        },
        sample: {
          id: "task_123",
          service: "compliance-nr1",
          status: "completed",
          company: "Empresa Exemplo Ltda",
          result: { risk_score: 0.35 },
          created_at: "2026-07-02T12:00:00Z",
        },
      },
    },
  },

  creates: {
    run_nr1_check: {
      key: "run_nr1_check",
      noun: "NR-1 Check",
      display: {
        label: "Run NR-1 Psychosocial Risk Check",
        description: "Executa diagnostico de riscos psicossociais NR-1.",
      },
      operation: {
        inputFields: [
          { key: "company", label: "Company Name", type: "string", required: true },
          { key: "sector", label: "Sector", type: "string", required: false },
          { key: "employees", label: "Number of Employees", type: "integer", required: false },
        ],
        perform: async (z, bundle) => {
          const url = `${bundle.authData.base_url}/api/agents/execute`;
          const response = await z.request({
            url,
            method: "POST",
            body: {
              agent_id: "nr1_psicossocial",
              task_type: "execute",
              payload: {
                empresa: bundle.inputData.company,
                setor: bundle.inputData.sector,
                funcionarios: bundle.inputData.employees,
              },
            },
          });
          return response.data;
        },
        sample: {
          task_id: "task_123",
          status: "queued",
          poll_url: "/api/tasks/task_123",
          summary: "Diagnostico NR-1 iniciado",
        },
      },
    },

    run_lgpd_scan: {
      key: "run_lgpd_scan",
      noun: "LGPD Scan",
      display: {
        label: "Run LGPD Privacy Scan",
        description: "Executa varredura de dados pessoais conforme LGPD.",
      },
      operation: {
        inputFields: [
          { key: "company", label: "Company Name", type: "string", required: true },
          { key: "data_types", label: "Data Types (comma separated)", type: "string", required: false },
        ],
        perform: async (z, bundle) => {
          const url = `${bundle.authData.base_url}/api/agents/execute`;
          const response = await z.request({
            url,
            method: "POST",
            body: {
              agent_id: "lgpd_operacional",
              task_type: "execute",
              payload: {
                empresa: bundle.inputData.company,
                tipo_dados: bundle.inputData.data_types,
              },
            },
          });
          return response.data;
        },
        sample: {
          task_id: "task_124",
          status: "queued",
          poll_url: "/api/tasks/task_124",
          summary: "LGPD scan iniciado",
        },
      },
    },

    run_eu_ai_act_check: {
      key: "run_eu_ai_act_check",
      noun: "EU AI Act Check",
      display: {
        label: "Run EU AI Act Readiness Check",
        description: "Classifica sistemas de IA conforme EU AI Act.",
      },
      operation: {
        inputFields: [
          { key: "company", label: "Company Name", type: "string", required: true },
          { key: "ai_systems", label: "AI Systems Description", type: "text", required: true },
        ],
        perform: async (z, bundle) => {
          const url = `${bundle.authData.base_url}/api/eu-ai-act/readiness-check`;
          const response = await z.request({
            url,
            method: "POST",
            body: {
              empresa: bundle.inputData.company,
              ai_systems: bundle.inputData.ai_systems,
            },
          });
          return response.data;
        },
        sample: {
          status: "completed",
          risk_classification: "high-risk",
          risk_score: 0.72,
          summary: "Sistema classificado como alto risco (Article 6, Annex III)",
        },
      },
    },

    create_compliance_report: {
      key: "create_compliance_report",
      noun: "Compliance Report",
      display: {
        label: "Create Compliance Report",
        description: "Gera relatorio de compliance consolidado.",
      },
      operation: {
        inputFields: [
          { key: "company", label: "Company Name", type: "string", required: true },
          {
            key: "frameworks",
            label: "Frameworks (comma separated)",
            type: "string",
            required: false,
            default: "nr1,lgpd,eu-ai-act",
          },
        ],
        perform: async (z, bundle) => {
          const url = `${bundle.authData.base_url}/api/agents/execute`;
          const frameworks = (bundle.inputData.frameworks || "nr1,lgpd,eu-ai-act")
            .split(",")
            .map((f) => f.trim());
          const response = await z.request({
            url,
            method: "POST",
            body: {
              agent_id: "compliance",
              task_type: "execute",
              payload: {
                empresa: bundle.inputData.company,
                frameworks,
              },
            },
          });
          return response.data;
        },
        sample: {
          task_id: "task_125",
          status: "queued",
          poll_url: "/api/tasks/task_125",
          summary: "Relatorio de compliance consolidado iniciado",
        },
      },
    },
  },

  searches: {
    find_subscription: {
      key: "find_subscription",
      noun: "Subscription",
      display: {
        label: "Find Subscription",
        description: "Busca detalhes de uma assinatura AION.",
      },
      operation: {
        inputFields: [
          {
            key: "subscription_id",
            type: "string",
            required: true,
            helpText: "ID da assinatura",
          },
        ],
        perform: async (z, bundle) => {
          const url = `${bundle.authData.base_url}/api/v1/subscriptions/${bundle.inputData.subscription_id}`;
          const response = await z.request({
            url,
            method: "GET",
          });
          return [response.data];
        },
        sample: {
          id: "sub_123",
          plan: "compliance_essencial",
          status: "active",
          customer_email: "cliente@exemplo.com",
        },
      },
    },
  },
});

module.exports = App;
