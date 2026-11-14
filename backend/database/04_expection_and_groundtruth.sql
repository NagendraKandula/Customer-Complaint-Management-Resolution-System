CREATE SCHEMA IF NOT EXISTS gt;

CREATE TABLE decision_logs (                              -- explainable decisions
    decision_id     VARCHAR(40)  PRIMARY KEY,             -- DEC-CMP-2026-000001-CAT
    complaint_id    VARCHAR(25)  NOT NULL REFERENCES complaints(complaint_id),
    decision_type   VARCHAR(40)  NOT NULL
                    CHECK (decision_type IN ('CATEGORY','SEVERITY','PRIORITY','ASSIGNMENT','SLA')),
    input_factors   JSONB        NOT NULL,
    selected_value  VARCHAR(100) NOT NULL,
    rule_name       VARCHAR(120) NOT NULL,
    reason          TEXT         NOT NULL,
    decided_at      TIMESTAMPTZ  NOT NULL
);


CREATE TABLE exception_cases (                            -- detected exceptions (validator output)
    exception_id     VARCHAR(40)  PRIMARY KEY,            -- EXC-000001
    entity_name      VARCHAR(50)  NOT NULL,
    record_id        VARCHAR(50)  NOT NULL,
    exception_type   VARCHAR(80)  NOT NULL
                     CHECK (exception_type IN ('COMPLAINT_NO_CUSTOMER','RESOLUTION_BEFORE_COMPLAINT',
                                               'SLA_PAUSE_INCORRECT','REPEAT_NOT_LINKED',
                                               'SAFETY_LOW_QUEUE','SURVEY_BEFORE_CLOSURE')),
    description      TEXT,
    severity         VARCHAR(20)  NOT NULL
                     CHECK (severity IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    detected_at      TIMESTAMPTZ  NOT NULL,               -- fixed base date, never now()
    status           VARCHAR(30)  NOT NULL DEFAULT 'OPEN'
                     CHECK (status IN ('OPEN','INVESTIGATING','RESOLVED')),
    resolution_notes TEXT
);



CREATE TABLE gt.ground_truth (
    ground_truth_id    VARCHAR(40)  PRIMARY KEY,          -- GT-000001
    entity_name        VARCHAR(50)  NOT NULL,             -- complaints / resolutions / sla_clocks / surveys
    record_id          VARCHAR(50)  NOT NULL,
    issue_type         VARCHAR(100) NOT NULL
                       CHECK (issue_type IN ('BASELINE','COMPLAINT_NO_CUSTOMER',
                                             'RESOLUTION_BEFORE_COMPLAINT','SLA_PAUSE_INCORRECT',
                                             'REPEAT_NOT_LINKED','SAFETY_LOW_QUEUE',
                                             'SURVEY_BEFORE_CLOSURE')),
    expected_value     JSONB,   -- e.g. {"category":"PRODUCT_SAFETY","priority":"P1","team":"TEAM-04","sla_minutes":15}
    actual_value       JSONB,
    expected_detection BOOLEAN  NOT NULL DEFAULT FALSE,   -- TRUE for injected anomalies
    scenario_name      VARCHAR(100),
    notes              TEXT
);
