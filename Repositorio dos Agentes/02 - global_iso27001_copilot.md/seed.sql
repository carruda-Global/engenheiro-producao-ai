-- Catálogo real ISO/IEC 27001:2022 — Anexo A. Parte 01: 16 controles
-- representativos dos 4 temas (93 controles totais). Usa o mesmo schema
-- "copilots" já criado para o SOC2 (Repositorio dos Agentes/01.../schema.sql).

SET search_path TO copilots;

INSERT INTO frameworks (id, nome, versao) VALUES
  ('iso27001', 'ISO/IEC 27001', '2022 (Anexo A)') ON CONFLICT (id) DO NOTHING;

INSERT INTO controles (id, framework_id, categoria, nome, descricao, obrigatorio) VALUES
('ISO-5.1', 'iso27001', 'Organizacional', 'Policies for Information Security', 'Política de segurança da informação aprovada pela direção e comunicada.', true),
('ISO-5.2', 'iso27001', 'Organizacional', 'Information Security Roles and Responsibilities', 'Papéis e responsabilidades de segurança claramente definidos.', true),
('ISO-5.3', 'iso27001', 'Organizacional', 'Segregation of Duties', 'Segregação de funções para tarefas conflitantes.', true),
('ISO-5.15', 'iso27001', 'Organizacional', 'Access Control', 'Política formal de controle de acesso baseada em papéis.', true),
('ISO-5.23', 'iso27001', 'Organizacional', 'Information Security for Use of Cloud Services', 'Avaliação de segurança de provedores de nuvem.', true),
('ISO-5.24', 'iso27001', 'Organizacional', 'Information Security Incident Management Planning', 'Plano de resposta a incidentes de segurança.', true),
('ISO-6.3', 'iso27001', 'Pessoas', 'Information Security Awareness, Education and Training', 'Treinamento periódico de conscientização em segurança.', true),
('ISO-6.7', 'iso27001', 'Pessoas', 'Remote Working', 'Política formal de trabalho remoto.', false),
('ISO-7.1', 'iso27001', 'Físico', 'Physical Security Perimeters', 'Perímetros de segurança física definidos e protegidos.', true),
('ISO-7.2', 'iso27001', 'Físico', 'Physical Entry', 'Controle de acesso físico a áreas seguras.', true),
('ISO-8.7', 'iso27001', 'Tecnológico', 'Protection Against Malware', 'Proteção antimalware ativa em endpoints e servidores.', true),
('ISO-8.8', 'iso27001', 'Tecnológico', 'Management of Technical Vulnerabilities', 'Processo de patch management.', true),
('ISO-8.13', 'iso27001', 'Tecnológico', 'Information Backup', 'Backup regular com teste de restauração.', true),
('ISO-8.15', 'iso27001', 'Tecnológico', 'Logging', 'Registro de eventos de sistema.', true),
('ISO-8.16', 'iso27001', 'Tecnológico', 'Monitoring Activities', 'Monitoramento ativo de rede/sistemas.', true),
('ISO-8.24', 'iso27001', 'Tecnológico', 'Use of Cryptography', 'Criptografia de dados sensíveis em repouso e trânsito.', true)
ON CONFLICT (id) DO NOTHING;
