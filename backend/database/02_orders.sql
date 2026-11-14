

CREATE TABLE orders (
    order_id                    VARCHAR(25)   PRIMARY KEY
                                CHECK (order_id ~ '^ORD-2026-[0-9]{6}$'),
    customer_id                 VARCHAR(20)   NOT NULL REFERENCES customers(customer_id),
    order_date                  TIMESTAMPTZ   NOT NULL,
    order_value                 NUMERIC(12,2) NOT NULL CHECK (order_value >= 0),  -- = SUM(order_items.line_total)
    order_status                VARCHAR(30)   NOT NULL
                                CHECK (order_status IN
                                ('PLACED','SHIPPED','DELIVERED','CANCELLED','RETURNED','LOST')),
    delivered_but_not_received  BOOLEAN       NOT NULL DEFAULT FALSE,
    delivery_date               TIMESTAMPTZ,
    created_at                  TIMESTAMPTZ   NOT NULL
);

CREATE TABLE order_items (                                -- bridge: orders <-> products
    order_item_id  VARCHAR(30)   PRIMARY KEY,             -- OIT-2026-000001-01
    order_id       VARCHAR(25)   NOT NULL REFERENCES orders(order_id),
    product_id     VARCHAR(20)   NOT NULL REFERENCES products(product_id),
    quantity       INTEGER       NOT NULL CHECK (quantity > 0),
    unit_price     NUMERIC(12,2) NOT NULL CHECK (unit_price >= 0),
    line_total     NUMERIC(12,2) NOT NULL,
    CHECK (line_total = quantity * unit_price),
    UNIQUE (order_id, product_id)
);
