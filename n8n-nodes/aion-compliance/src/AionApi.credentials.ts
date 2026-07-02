import { ICredentialType, INodeProperties } from 'n8n-workflow';

export class AionApi implements ICredentialType {
  name = 'aionApi';
  displayName = 'AION API';
  documentationUrl = 'https://engenheiro-producao-ai.onrender.com/docs';

  properties: INodeProperties[] = [
    {
      displayName: 'API Key',
      name: 'apiKey',
      type: 'string',
      typeOptions: { password: true },
      default: '',
      required: true,
      description: 'Sua chave de API do AION. Obtenha em https://engenheiro-producao-ai.onrender.com',
    },
    {
      displayName: 'Base URL',
      name: 'baseUrl',
      type: 'string',
      default: 'https://engenheiro-producao-ai.onrender.com',
      required: true,
      description: 'URL base da API AION',
    },
  ];
}
