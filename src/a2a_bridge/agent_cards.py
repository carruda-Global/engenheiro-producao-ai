from a2a.types import (
    AgentCard,
    AgentSkill,
    AgentCapabilities,
    AgentProvider,
    AgentInterface,
    APIKeySecurityScheme,
    SecurityScheme,
)


def build_agent_card(base_url: str | None = None) -> AgentCard:
    jsonrpc_url = f"{base_url}/a2a/jsonrpc" if base_url else "/a2a/jsonrpc"
    rest_url = f"{base_url}/a2a/rest" if base_url else "/a2a/rest"

    card = AgentCard(
        name="Engenheiro de Produção AI",
        description=(
            "Sistema multiagente para Arquitetura, Engenharia e Construção (AEC). "
            "Oferece 5 agentes especializados: Análise de Especificações Técnicas, "
            "Compras/Procurement, Gestão de Estoque, Logística e Execução em Campo. "
            "Automatize processos de engenharia com IA especializada no setor AEC."
        ),
        version="1.0.0",
        documentation_url="https://engenheiro-producao-ai.onrender.com/docs",
        icon_url=f"{base_url}/static/logo.png" if base_url else "/static/logo.png",
    )

    prov = AgentProvider(
        organization="Projato Engenharia",
        url="https://projato.com.br",
    )
    card.provider.CopyFrom(prov)

    cap = AgentCapabilities(
        streaming=True,
        push_notifications=False,
    )
    card.capabilities.CopyFrom(cap)

    api_key_scheme = APIKeySecurityScheme(
        name="X-API-Key",
        location="header",
    )
    scheme = SecurityScheme()
    scheme.api_key_security_scheme.CopyFrom(api_key_scheme)
    card.security_schemes["api_key"].MergeFrom(scheme)

    card.default_input_modes.append("text")
    card.default_output_modes.append("text")

    _add_skill(
        card,
        id="spec_analysis",
        name="Analisador de Especificações Técnicas",
        description=(
            "Analisa documentos de engenharia (plantas, memoriais, normas) "
            "para extrair requisitos técnicos, identificar contradições e "
            "sinalizar não-conformidades com normas como NBR-6118, NBR-9050."
        ),
        tags=["engenharia", "normas", "documentos", "conformidade"],
        examples=[
            "Analise esta especificação de concreto armado conforme NBR-6118",
            "Verifique não-conformidades neste memorial descritivo",
        ],
    )
    _add_skill(
        card,
        id="procurement",
        name="Processador de Compras",
        description=(
            "Processa pedidos de compra, compara cotações de fornecedores, "
            "gera requisições e otimiza custos de aquisição para obras."
        ),
        tags=["compras", "suprimentos", "fornecedores", "cotação"],
        examples=[
            "Processe pedido de 100 sacos de cimento CP-II",
            "Compare estas cotações e recomende a melhor opção",
        ],
    )
    _add_skill(
        card,
        id="inventory",
        name="Gestor de Estoque de Obra",
        description=(
            "Monitora níveis de estoque em tempo real, identifica itens "
            "em falta, sugere substitutos técnicos e calcula ressuprimento."
        ),
        tags=["estoque", "materiais", "substitutos", "obra"],
        examples=[
            "Verifique o estoque de aço CA-50 e sugira reposição",
            "Preciso de um substituto para cimento CP-II com mesma resistência",
        ],
    )
    _add_skill(
        card,
        id="logistics",
        name="Rastreador Logístico",
        description=(
            "Acompanha envios de materiais, identifica problemas de entrega, "
            "gera alertas de atraso e sugere rotas alternativas."
        ),
        tags=["logística", "entregas", "transporte", "rastreamento"],
        examples=[
            "Rastreie o envio do pedido de materiais para a obra X",
            "Verifique problemas nas entregas programadas para esta semana",
        ],
    )
    _add_skill(
        card,
        id="field_execution",
        name="Gerador de Instruções de Campo",
        description=(
            "Traduz modelos BIM e plantas em instruções claras para "
            "trabalhadores em campo. Identifica desvios de projeto e "
            "reduz retrabalho na execução de obras."
        ),
        tags=["obra", "campo", "execução", "BIM", "instruções"],
        examples=[
            "Gere instruções de execução para esta laje conforme projeto",
            "Compare o executado com o projetado e aponte desvios",
        ],
    )
    _add_skill(
        card,
        id="bim_coordination",
        name="Coordenador BIM",
        description=(
            "Cria elementos 3D via comandos de texto, realiza clash detection "
            "entre disciplinas e valida modelos BIM contra especificacoes."
        ),
        tags=["BIM", "3D", "clash", "modelagem"],
        examples=[
            "Crie uma parede de concreto de 3m x 2.8m com espessura de 15cm",
            "Detecte conflitos entre o projeto estrutural e hidraulico",
        ],
    )
    _add_skill(
        card,
        id="requirements_analysis",
        name="Analisador de Requisitos",
        description=(
            "Avalia requisitos de engenharia contra padroes de qualidade, "
            "gera scores, identifica ambiguidades e sugere melhorias."
        ),
        tags=["requisitos", "qualidade", "normas", "ISO"],
        examples=[
            "Analise a qualidade destes requisitos de fundacao",
            "Verifique consistencia entre os conjuntos de requisitos A e B",
        ],
    )
    _add_skill(
        card,
        id="engineering_assistant",
        name="Assistente de Engenharia",
        description=(
            "Assistente conversacional que responde perguntas tecnicas, "
            "busca informacoes em documentos e sumariza textos longos."
        ),
        tags=["chat", "perguntas", "documentos", "sumario"],
        examples=[
            "O que diz a NBR-6118 sobre cobrimento de armadura?",
            "Sumarize este memorial descritivo de 50 paginas",
        ],
    )
    _add_skill(
        card,
        id="work_synopsis",
        name="Resumidor de Tarefas",
        description=(
            "Gera resumos estruturados de tarefas e defeitos de obra, "
            "capturando contexto, riscos e prazos criticos."
        ),
        tags=["tarefas", "defeitos", "resumo", "cronograma"],
        examples=[
            "Resuma esta lista de defeitos da vistoria da obra",
            "Gere um resumo de status semanal do projeto",
        ],
    )
    _add_skill(
        card,
        id="photo_intelligence",
        name="Inteligencias Visual de Obras",
        description=(
            "Analisa fotos de obras para identificar elementos construtivos, "
            "detectar riscos de seguranca e comparar com cronograma."
        ),
        tags=["fotos", "visao", "seguranca", "EPI", "cronograma"],
        examples=[
            "Analise esta foto do canteiro de obras e identifique riscos",
            "Compare o progresso visual com o cronograma esperado",
        ],
    )
    _add_skill(
        card,
        id="rfi_creation",
        name="Criador de RFIs",
        description=(
            "Gera RFIs (Request for Information) profissionais a partir "
            "de duvidas do campo, buscando em especificacoes tecnicas."
        ),
        tags=["RFI", "documentacao", "especificacao", "consulta"],
        examples=[
            "Crie uma RFI sobre a especificacao do concreto da fundacao",
            "Busque nesta especificacao a resistencia requerida para o aco",
        ],
    )
    _add_skill(
        card,
        id="compliance",
        name="Agente de Conformidade",
        description=(
            "Monitora conformidade legal, gera PGRS/PGRSS, emite alertas "
            "sobre prazos regulatorios e obrigacoes ambientais."
        ),
        tags=["conformidade", "PGRS", "PGRSS", "regulatorio", "ambiental"],
        examples=[
            "Verifique a conformidade deste projeto com a legislacao ambiental",
            "Gere um esboco de PGRS para esta obra",
        ],
    )

    iface_jsonrpc = AgentInterface(
        protocol_binding="JSONRPC",
        protocol_version="1.0",
        url=jsonrpc_url,
    )
    card.supported_interfaces.append(iface_jsonrpc)

    iface_rest = AgentInterface(
        protocol_binding="HTTP+JSON",
        protocol_version="1.0",
        url=rest_url,
    )
    card.supported_interfaces.append(iface_rest)

    return card


def _add_skill(
    card: AgentCard,
    id: str,
    name: str,
    description: str,
    tags: list[str] | None = None,
    examples: list[str] | None = None,
):
    skill = AgentSkill(
        id=id,
        name=name,
        description=description,
        tags=tags or [],
        examples=examples or [],
        input_modes=["text"],
        output_modes=["text"],
    )
    card.skills.append(skill)
