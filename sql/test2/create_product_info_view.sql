CREATE VIEW product_info AS
SELECT
    p.product_id,
    p.product_name,
    p.description,
    p.price,
    p.stock_quantity,
    p.category_id,
    c.category_name,
    c.category_description,
    c.parent_category_id,
    p.created_at,
    p.updated_at
FROM products p
LEFT JOIN categories c ON p.category_id = c.category_id;