DO $$
BEGIN
  -- S� executa se a tabela ainda n�o existe
  IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'subscriptions') THEN
    CREATE TABLE subscriptions (
        id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        external_id TEXT NOT NULL,
        customer_id TEXT NOT NULL,
        customer_email TEXT DEFAULT '',
        customer_name TEXT DEFAULT '',
        plan_id TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        activated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        cancelled_at TIMESTAMPTZ,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        metadata JSONB DEFAULT '{}',
        UNIQUE(source, external_id)
    );
    CREATE INDEX idx_subscriptions_customer_id ON subscriptions(customer_id);
    CREATE INDEX idx_subscriptions_status ON subscriptions(status);
  END IF;

  IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'processed_webhook_events') THEN
    CREATE TABLE processed_webhook_events (
        event_id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        processed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        event_type TEXT NOT NULL,
        payload JSONB DEFAULT '{}'
    );
    CREATE INDEX idx_webhook_events_source ON processed_webhook_events(source);
  END IF;

  IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'agent_executions') THEN
    CREATE TABLE agent_executions (
        id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
        tenant_id TEXT NOT NULL,
        agent_id TEXT NOT NULL,
        task_type TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'queued',
        input_summary TEXT,
        result_summary TEXT,
        llm_tokens_used INTEGER DEFAULT 0,
        cost_brl NUMERIC(10,4) DEFAULT 0,
        queued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        started_at TIMESTAMPTZ,
        completed_at TIMESTAMPTZ,
        error_message TEXT
    );
    CREATE INDEX idx_agent_executions_tenant ON agent_executions(tenant_id);
    CREATE INDEX idx_agent_executions_status ON agent_executions(status);
  END IF;

  IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'agent_registry') THEN
    CREATE TABLE agent_registry (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        cluster TEXT NOT NULL,
        description TEXT,
        llm_model TEXT NOT NULL DEFAULT 'deepseek-chat',
        status TEXT NOT NULL DEFAULT 'active',
        plan_ids TEXT[] DEFAULT '{}',
        config JSONB DEFAULT '{}',
        version TEXT DEFAULT '1.0.0',
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
  END IF;

  IF NOT EXISTS (SELECT FROM pg_tables WHERE tablename = 'audit_log') THEN
    CREATE TABLE audit_log (
        id BIGSERIAL PRIMARY KEY,
        tenant_id TEXT,
        actor TEXT NOT NULL,
        action TEXT NOT NULL,
        resource_type TEXT NOT NULL,
        resource_id TEXT,
        details JSONB DEFAULT '{}',
        ip_address TEXT,
        hash TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX idx_audit_log_tenant ON audit_log(tenant_id);
    CREATE INDEX idx_audit_log_created ON audit_log(created_at DESC);
  END IF;
END $$;
