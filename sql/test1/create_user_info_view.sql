-- Create user_info view that combines user and department information
CREATE OR REPLACE VIEW user_info AS
SELECT
    u.id AS user_id,
    u.username,
    u.email,
    u.first_name,
    u.last_name,
    d.name AS department_name,
    d.manager_id,
    CASE
        WHEN u.is_active = 1 THEN 'active'
        ELSE 'inactive'
    END AS is_active,
    u.created_at,
    u.updated_at
FROM user u
LEFT JOIN department d ON u.department_id = d.id;