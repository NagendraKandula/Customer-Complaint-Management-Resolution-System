
-- =====================================================================
-- E. MASTER AND ORDER TABLE INDEXES
-- =====================================================================

CREATE INDEX idx_agents_team
    ON agents(team_id);

CREATE INDEX idx_categories_team
    ON complaint_categories(default_team_id);

CREATE INDEX idx_orders_customer
    ON orders(customer_id);

CREATE INDEX idx_order_items_order
    ON order_items(order_id);

CREATE INDEX idx_order_items_product
    ON order_items(product_id);
