

CREATE TABLE complaints (
    complaint_id            VARCHAR(25)  PRIMARY KEY
                            CHECK (complaint_id ~ '^CMP-2026-[0-9]{6}$'),
    customer_id             VARCHAR(20)  REFERENCES customers(customer_id),   -- NULL only for injected anomaly
    order_id                VARCHAR(25)  REFERENCES orders(order_id),
    product_id              VARCHAR(20)  REFERENCES products(product_id),
    category_id             VARCHAR(20)  REFERENCES complaint_categories(category_id),
    priority_rule_id        VARCHAR(20)  REFERENCES priority_rules(priority_rule_id),
    complaint_text          TEXT         NOT NULL,
    channel                 VARCHAR(30)  NOT NULL
                            CHECK (channel IN ('EMAIL','PHONE','WEBSITE',
                                               'MOBILE_APP','LIVE_CHAT','SOCIAL_MEDIA')),
    sentiment               VARCHAR(20)
                            CHECK (sentiment IN ('NEUTRAL','NEGATIVE','VERY_NEGATIVE')),
    severity                VARCHAR(20)
                            CHECK (severity IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    priority                VARCHAR(10)
                            CHECK (priority IN ('P1','P2','P3','P4')),
    priority_score          INTEGER,
    class_rule_fired        VARCHAR(120),                 -- e.g. R-SAFETY-01
    is_safety_related       BOOLEAN      NOT NULL DEFAULT FALSE,
    is_repeat               BOOLEAN      NOT NULL DEFAULT FALSE,
    repeat_of_complaint_id  VARCHAR(25)  REFERENCES complaints(complaint_id),
    status                  VARCHAR(30)  NOT NULL
                            CHECK (status IN ('OPEN','CLASSIFIED','ASSIGNED','IN_PROGRESS',
                                              'WAITING_FOR_CUSTOMER','ESCALATED','RESOLVED',
                                              'CLOSED','REOPENED')),
    reopen_count            INTEGER      NOT NULL DEFAULT 0 CHECK (reopen_count >= 0),
    closed_at               TIMESTAMPTZ,
    created_at              TIMESTAMPTZ  NOT NULL,
    updated_at              TIMESTAMPTZ  NOT NULL,
    CHECK (updated_at >= created_at)
);

CREATE TABLE complaint_messages (
    message_id    VARCHAR(40)  PRIMARY KEY,               -- MSG-CMP-2026-000001-001
    complaint_id  VARCHAR(25)  NOT NULL REFERENCES complaints(complaint_id),
    sender_type   VARCHAR(20)  NOT NULL
                  CHECK (sender_type IN ('CUSTOMER','AGENT','SYSTEM')),
    sender_id     VARCHAR(30),                            -- customer_id or agent_id
    message_text  TEXT         NOT NULL,
    channel       VARCHAR(30)  NOT NULL
                  CHECK (channel IN ('EMAIL','PHONE','WEBSITE',
                                     'MOBILE_APP','LIVE_CHAT','SOCIAL_MEDIA')),
    sent_at       TIMESTAMPTZ  NOT NULL
);

CREATE TABLE complaint_assignments (                      -- ownership history, append-only
    assignment_id      VARCHAR(40)  PRIMARY KEY,          -- ASG-CMP-2026-000001-01
    complaint_id       VARCHAR(25)  NOT NULL REFERENCES complaints(complaint_id),
    team_id            VARCHAR(20)  NOT NULL REFERENCES teams(team_id),
    agent_id           VARCHAR(20)  REFERENCES agents(agent_id),
    assigned_at        TIMESTAMPTZ  NOT NULL,
    ended_at           TIMESTAMPTZ,                       -- NULL = current owner
    assignment_reason  TEXT,
    CHECK (ended_at IS NULL OR ended_at >= assigned_at)
);
CREATE UNIQUE INDEX uq_current_complaint_assignment
    ON complaint_assignments (complaint_id)
    WHERE ended_at IS NULL;

CREATE TABLE complaint_status_history (                   -- every lifecycle transition
    history_id    VARCHAR(40)  PRIMARY KEY,               -- HST-CMP-2026-000001-001
    complaint_id  VARCHAR(25)  NOT NULL REFERENCES complaints(complaint_id),
    old_status    VARCHAR(30),                            -- NULL for first status
    new_status    VARCHAR(30)  NOT NULL
                  CHECK (new_status IN ('OPEN','CLASSIFIED','ASSIGNED','IN_PROGRESS',
                                        'WAITING_FOR_CUSTOMER','ESCALATED','RESOLVED',
                                        'CLOSED','REOPENED')),
    changed_by    VARCHAR(50)  NOT NULL,
    reason        TEXT,
    changed_at    TIMESTAMPTZ  NOT NULL
);

CREATE TABLE sla_clocks (                                 -- 1:1 with complaint
    sla_id                VARCHAR(40)  PRIMARY KEY,       -- SLA-CMP-2026-000001
    complaint_id          VARCHAR(25)  NOT NULL UNIQUE REFERENCES complaints(complaint_id),
    priority_level        VARCHAR(10)  NOT NULL REFERENCES sla_policy(priority_level),
    started_at            TIMESTAMPTZ  NOT NULL,
    response_deadline     TIMESTAMPTZ  NOT NULL,          -- started_at + response_minutes (+ pauses)
    resolution_deadline   TIMESTAMPTZ  NOT NULL,
    first_response_at     TIMESTAMPTZ,
    resolved_at           TIMESTAMPTZ,
    response_breached     BOOLEAN      NOT NULL DEFAULT FALSE,
    resolution_breached   BOOLEAN      NOT NULL DEFAULT FALSE,
    is_paused             BOOLEAN      NOT NULL DEFAULT FALSE,
    paused_at             TIMESTAMPTZ,
    total_paused_minutes  INTEGER      NOT NULL DEFAULT 0 CHECK (total_paused_minutes >= 0),
    CHECK (resolution_deadline >= response_deadline),
    CHECK (is_paused = (paused_at IS NOT NULL))
);

CREATE TABLE sla_events (                                 -- pause / resume / breach / escalate history
    sla_event_id  VARCHAR(40)  PRIMARY KEY,               -- SLE-CMP-2026-000001-001
    sla_id        VARCHAR(40)  NOT NULL REFERENCES sla_clocks(sla_id),
    event_type    VARCHAR(30)  NOT NULL
                  CHECK (event_type IN ('STARTED','FIRST_RESPONSE','PAUSED','RESUMED','EXTENDED',
                                        'RESPONSE_BREACHED','RESOLUTION_BREACHED',
                                        'ESCALATED','COMPLETED')),
    event_time    TIMESTAMPTZ  NOT NULL,
    reason        TEXT,
    metadata      JSONB
);

CREATE TABLE resolutions (                                -- 1:N per complaint (reopen cycles)
    resolution_id     VARCHAR(40)   PRIMARY KEY,          -- RES-CMP-2026-000001 (cycle 1), ...-02 for cycle 2
    complaint_id      VARCHAR(25)   NOT NULL REFERENCES complaints(complaint_id),
    cycle_no          INTEGER       NOT NULL DEFAULT 1 CHECK (cycle_no >= 1),
    resolution_type   VARCHAR(50)   NOT NULL
                      CHECK (resolution_type IN ('REFUND','REPLACEMENT','REPAIR',
                                                 'EXPLANATION','REDELIVERY','NO_ACTION')),
    outcome           VARCHAR(50)   NOT NULL
                      CHECK (outcome IN ('RESOLVED','REJECTED','PARTIAL')),
    resolution_notes  TEXT,
    resolved_by       VARCHAR(20)   REFERENCES agents(agent_id),
    resolved_at       TIMESTAMPTZ   NOT NULL,
    refund_amount     NUMERIC(12,2) CHECK (refund_amount IS NULL OR refund_amount >= 0),
    is_final          BOOLEAN       NOT NULL DEFAULT FALSE,
    UNIQUE (complaint_id, cycle_no)
);

CREATE TABLE surveys (
    survey_id      VARCHAR(40)  PRIMARY KEY,              -- SRV-CMP-2026-000001
    complaint_id   VARCHAR(25)  NOT NULL REFERENCES complaints(complaint_id),
    resolution_id  VARCHAR(40)  NOT NULL REFERENCES resolutions(resolution_id),
    sent_at        TIMESTAMPTZ  NOT NULL,
    submitted_at   TIMESTAMPTZ,                           -- NULL = no response
    rating         INTEGER      CHECK (rating BETWEEN 1 AND 5),
    feedback       TEXT,
    CHECK (submitted_at IS NULL OR submitted_at >= sent_at)
);