-- Catálogo real SOC2 — Trust Services Criteria (AICPA 2017, revisado 2022)
-- Parte 01: os 9 Common Criteria "âncora" (CC1.1-CC9.1), obrigatórios em
-- todo relatório SOC2 (categoria Security). Cada CCx tem sub-critérios
-- adicionais (CC6 sozinho tem 8) — completar em partes seguintes, mesma
-- lógica do Banco Mestre de Riscos do NR1.
-- Fonte: AICPA Trust Services Criteria, mapeamento cruzado com Secureframe/Drata/SANS.

SET search_path TO copilots;

INSERT INTO frameworks (id, nome, versao) VALUES
  ('soc2', 'SOC 2', 'AICPA TSC 2017 (rev. 2022)') ON CONFLICT (id) DO NOTHING;

INSERT INTO controles (id, framework_id, categoria, nome, descricao, obrigatorio) VALUES
('CC1.1', 'soc2', 'Control Environment', 'Integridade e valores éticos',
 'A organização demonstra compromisso com integridade e valores éticos.', true),
('CC2.1', 'soc2', 'Communication and Information', 'Comunicação de informações de segurança',
 'A organização obtém/gera e usa informações de qualidade para apoiar o funcionamento do controle interno.', true),
('CC3.1', 'soc2', 'Risk Assessment', 'Definição de objetivos para avaliação de risco',
 'A organização especifica objetivos com clareza suficiente para permitir a identificação e avaliação de riscos.', true),
('CC4.1', 'soc2', 'Monitoring Activities', 'Avaliações contínuas e independentes',
 'A organização seleciona, desenvolve e realiza avaliações contínuas e/ou independentes para verificar se os componentes de controle interno estão presentes e funcionando.', true),
('CC5.1', 'soc2', 'Control Activities', 'Seleção e desenvolvimento de atividades de controle',
 'A organização seleciona e desenvolve atividades de controle que contribuem para a mitigação de riscos a níveis aceitáveis.', true),
('CC6.1', 'soc2', 'Logical and Physical Access Controls', 'Controles de acesso lógico',
 'A organização implementa controles de acesso lógico para proteger contra ameaças de fontes externas às fronteiras do sistema.', true),
('CC6.2', 'soc2', 'Logical and Physical Access Controls', 'Provisionamento e desprovisionamento de acesso',
 'Antes de conceder acesso, a identidade do usuário é registrada e autorizada; o acesso é removido quando não é mais necessário.', true),
('CC6.3', 'soc2', 'Logical and Physical Access Controls', 'Gestão de privilégios de acesso',
 'A organização autoriza, modifica ou remove acesso com base em papéis, responsabilidades ou critério de sistema, aplicando o princípio de menor privilégio.', true),
('CC7.1', 'soc2', 'System Operations', 'Detecção de vulnerabilidades',
 'A organização usa procedimentos de detecção e monitoramento para identificar mudanças em configurações que introduzam vulnerabilidades e componentes maliciosos.', true),
('CC7.2', 'soc2', 'System Operations', 'Monitoramento de eventos de segurança',
 'A organização monitora componentes do sistema e a operação desses componentes para detectar anomalias.', true),
('CC8.1', 'soc2', 'Change Management', 'Gestão de mudanças',
 'A organização autoriza, projeta, desenvolve/adquire, configura, documenta, testa, aprova e implementa mudanças em infraestrutura, dados, software e procedimentos.', true),
('CC9.1', 'soc2', 'Risk Mitigation', 'Mitigação de riscos de negócio',
 'A organização identifica, seleciona e desenvolve atividades de mitigação de risco para riscos decorrentes de interrupções de negócio.', true),
('A1.2', 'soc2', 'Availability', 'Monitoramento de capacidade e disponibilidade',
 'A organização monitora infraestrutura e software para desempenho e disponibilidade, e implementa medidas de recuperação (backup, DR) para atender objetivos de disponibilidade.', false)
ON CONFLICT (id) DO NOTHING;

INSERT INTO perguntas (id, controle_id, texto) VALUES
('Q-CC1.1', 'CC1.1', 'Existe código de conduta/ética formalizado e comunicado aos funcionários?'),
('Q-CC2.1', 'CC2.1', 'Existe política de segurança da informação documentada e comunicada?'),
('Q-CC3.1', 'CC3.1', 'Existe processo formal de avaliação de riscos (risk assessment) documentado?'),
('Q-CC4.1', 'CC4.1', 'Existem auditorias internas ou avaliações independentes periódicas dos controles?'),
('Q-CC5.1', 'CC5.1', 'Existem controles documentados mapeados aos riscos identificados?'),
('Q-CC6.1', 'CC6.1', 'Existe controle de acesso lógico (firewall, VPN, autenticação) documentado?'),
('Q-CC6.2', 'CC6.2', 'Existe processo formal de onboarding/offboarding de acesso a sistemas?'),
('Q-CC6.3', 'CC6.3', 'O acesso é concedido por papel/função com revisão periódica de privilégios?'),
('Q-CC7.1', 'CC7.1', 'Existe ferramenta de scan de vulnerabilidades rodando periodicamente?'),
('Q-CC7.2', 'CC7.2', 'Existe SIEM ou ferramenta de monitoramento de eventos de segurança?'),
('Q-CC8.1', 'CC8.1', 'Existe processo formal de change management (aprovação, teste, deploy)?'),
('Q-CC9.1', 'CC9.1', 'Existe plano de continuidade de negócio / resposta a incidentes documentado?'),
('Q-A1.2', 'A1.2', 'Existe backup automatizado e plano de disaster recovery testado?')
ON CONFLICT (id) DO NOTHING;
