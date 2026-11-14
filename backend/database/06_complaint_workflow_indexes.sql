
-- =====================================================================
-- F. COMPLAINT WORKFLOW INDEXES
-- =====================================================================

CREATE INDEX idx_complaints_customer
    ON complaints(customer_id);

CREATE INDEX idx_complaints_order
    ON complaints(order_id);

CREATE INDEX idx_complaints_product
    ON complaints(product_id);

CREATE INDEX idx_complaints_category
    ON complaints(category_id);

CREATE INDEX idx_complaints_rule
    ON complaints(priority_rule_id);

CREATE INDEX idx_complaints_repeat_of
    ON complaints(repeat_of_complaint_id);

CREATE INDEX idx_complaints_status
    ON complaints(status);

CREATE INDEX idx_complaints_priority
    ON complaints(priority);

CREATE INDEX idx_complaints_created
    ON complaints(created_at);

CREATE INDEX idx_messages_complaint
    ON complaint_messages(complaint_id, sent_at);

CREATE INDEX idx_assignments_complaint
    ON complaint_assignments(complaint_id);

CREATE INDEX idx_assignments_team
    ON complaint_assignments(team_id);

CREATE INDEX idx_assignments_agent
    ON complaint_assignments(agent_id);

CREATE INDEX idx_status_hist_complaint
    ON complaint_status_history(complaint_id, changed_at);

CREATE INDEX idx_sla_clocks_priority
    ON sla_clocks(priority_level);

CREATE INDEX idx_sla_events_sla
    ON sla_events(sla_id, event_time);

CREATE INDEX idx_resolutions_complaint
    ON resolutions(complaint_id);

CREATE INDEX idx_resolutions_agent
    ON resolutions(resolved_by);

CREATE INDEX idx_surveys_complaint
    ON surveys(complaint_id);

CREATE INDEX idx_surveys_resolution
    ON surveys(resolution_id);

CREATE INDEX idx_decisions_complaint
    ON decision_logs(complaint_id);

CREATE INDEX idx_exceptions_record
    ON exception_cases(entity_name, record_id);

CREATE INDEX idx_gt_record
    ON gt.ground_truth(entity_name, record_id);
