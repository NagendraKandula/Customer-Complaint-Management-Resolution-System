-- =====================================================================
-- A. MASTER / REFERENCE TABLES
-- =====================================================================

CREATE TABLE teams (
    team_id      VARCHAR(20)  PRIMARY KEY,                -- TEAM-01
    team_name    VARCHAR(80)  NOT NULL UNIQUE,
    description  TEXT,
    is_active    BOOLEAN      NOT NULL DEFAULT TRUE
);

CREATE TABLE agents (
    agent_id             VARCHAR(20)  PRIMARY KEY,        -- AGT-001
    team_id              VARCHAR(20)  NOT NULL REFERENCES teams(team_id),
    agent_name           VARCHAR(120) NOT NULL,
    email                VARCHAR(255) NOT NULL UNIQUE,
    max_open_complaints  INTEGER      NOT NULL CHECK (max_open_complaints > 0),
    is_active            BOOLEAN      NOT NULL DEFAULT TRUE
);

CREATE TABLE complaint_categories (                       -- 10 rows
    category_id      VARCHAR(20)  PRIMARY KEY,            -- CAT-01
    category_name    VARCHAR(80)  NOT NULL UNIQUE,        -- e.g. PRODUCT_SAFETY
    description      TEXT,
    base_severity    VARCHAR(20)  NOT NULL
                     CHECK (base_severity IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    is_safety        BOOLEAN      NOT NULL DEFAULT FALSE,
    default_team_id  VARCHAR(20)  NOT NULL REFERENCES teams(team_id),
    is_active        BOOLEAN      NOT NULL DEFAULT TRUE
);

-- condition_json keys (document in README), e.g.:
--   {"type":"OVERRIDE","if":{"is_safety_related":true}}
--   {"type":"SCORE_BAND","min_score":8,"max_score":99}
--   {"type":"POINTS","factor":"order_value_gt","value":50000}
CREATE TABLE priority_rules (
    priority_rule_id  VARCHAR(20)  PRIMARY KEY,           -- PR-01
    rule_name         VARCHAR(120) NOT NULL,
    condition_json    JSONB        NOT NULL,
    priority_level    VARCHAR(10)  NOT NULL
                      CHECK (priority_level IN ('P1','P2','P3','P4')),
    priority_score    INTEGER,                            -- points contributed by the rule
    effective_from    TIMESTAMPTZ  NOT NULL,
    effective_to      TIMESTAMPTZ,
    is_active         BOOLEAN      NOT NULL DEFAULT TRUE,
    CHECK (effective_to IS NULL OR effective_to > effective_from)
);

CREATE TABLE sla_policy (                                 -- 4 rows, one per priority
    priority_level            VARCHAR(10) PRIMARY KEY
                              CHECK (priority_level IN ('P1','P2','P3','P4')),
    response_minutes          INTEGER NOT NULL CHECK (response_minutes > 0),
    resolution_minutes        INTEGER NOT NULL CHECK (resolution_minutes > 0),
    escalation_threshold_pct  INTEGER NOT NULL DEFAULT 80
                              CHECK (escalation_threshold_pct BETWEEN 1 AND 100),
    CHECK (resolution_minutes >= response_minutes)
);

CREATE TABLE customers (
    customer_id    VARCHAR(20)  PRIMARY KEY
                   CHECK (customer_id ~ '^CUS-[0-9]{6}$'),
    full_name      VARCHAR(150) NOT NULL,                 -- synthetic only
    email          VARCHAR(255) UNIQUE,
    phone          VARCHAR(20),
    customer_tier  VARCHAR(30)  NOT NULL
                   CHECK (customer_tier IN ('STANDARD','SILVER','GOLD','PLATINUM')),
    is_vulnerable  BOOLEAN      NOT NULL DEFAULT FALSE,   -- synthetic flag
    created_at     TIMESTAMPTZ  NOT NULL
);

CREATE TABLE products (
    product_id          VARCHAR(20)   PRIMARY KEY,        -- PRD-0001
    product_name        VARCHAR(150)  NOT NULL,
    product_category    VARCHAR(80)   NOT NULL,
    unit_price          NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
    is_safety_critical  BOOLEAN       NOT NULL DEFAULT FALSE,
    is_active           BOOLEAN       NOT NULL DEFAULT TRUE
);
