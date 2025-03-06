use cafe_crm;

-- PRE-FILLING THE TABLES
-- Categories
INSERT INTO menu_categories (category_name) VALUES
('Hot Beverages'),
('Cold Beverages'),
('Bakery Items'),
('South Indian Snacks'),
('Chaats'),
('Desserts');

-- items and price
INSERT INTO menu_items (item_name, category_id, item_price) VALUES
-- 🌡️ Hot Beverages
('Coffee', 1, 20.00),
('Tea', 1, 15.00),
('Filter Coffee', 1, 25.00),
('Masala Tea', 1, 20.00),
('Sukku Malli Coffee', 1, 30.00),

-- ❄️ Cold Beverages
('Jigarthanda', 2, 60.00),
('Nannari Sarbath', 2, 40.00),
('Rose Milk', 2, 50.00),

-- 🥐 Bakery Items
('Egg Puffs', 3, 30.00),
('Vegetable Puffs', 3, 25.00),
('Banana Cake', 3, 35.00),

-- 🍘 South Indian Snacks (Light Snacks Only)
('Murukku', 4, 20.00),
('Mixture', 4, 25.00),
('Thattai', 4, 20.00),
('Ribbon Pakoda', 4, 25.00),

-- 🌮 Chaats
('Masala Puri', 5, 50.00),
('Pani Puri', 5, 40.00),
('Samosa Chaat', 5, 45.00),

-- 🍨 Desserts
('Rasmalai', 6, 80.00),
('Gulab Jamun', 6, 60.00),
('Elaneer Payasam', 6, 90.00);

INSERT INTO discount_types(type_name) VALUES
('flat'), ('percentage');

INSERT INTO discounts (discount_name, type_id, discount_value, min_order_value, is_active) 
VALUES
('10 % offer on First Order', 2, 10, 0, true),
('20% offer on hundreds', 2, 20, 99, true),
('30% offer on five-hundred', 2, 30, 499, true),
('100rs cashback for thousands', 1, 100, 999, true); 


INSERT INTO loyalty_tiers(tier_name, min_points, max_points) VALUES
('bronze', 0, 250),
('silver', 251, 750),
('gold', 751, 1500),
('platinum', 1501, 3000);

INSERT INTO review_categories(category_name) VALUES
('food & drinks'), ('service'), ('ambience'), ('pricing'), ('discount & offers');



