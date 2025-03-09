
CREATE DATABASE cafe_crm;
USE cafe_crm;

-- CUSTOMER
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(256) NOT NULL,
    email VARCHAR(256) UNIQUE,
    mobile_no VARCHAR(15) UNIQUE,
    date_of_birth DATE
);

-- MENU
CREATE TABLE menu_categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(256) UNIQUE
);

CREATE TABLE menu_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    item_name VARCHAR(256) NOT NULL UNIQUE,
    category_id INT NOT NULL,
    item_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (category_id) REFERENCES menu_categories(category_id) ON DELETE CASCADE
);

-- DISCOUNTS 
CREATE TABLE discount_types(
    type_id INT PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(30) NOT NULL
);

CREATE TABLE discounts (
    discount_id INT PRIMARY KEY AUTO_INCREMENT,
    discount_name VARCHAR(256) NOT NULL,
    type_id INT NOT NULL,
    discount_value DECIMAL(10,2) NOT NULL,
    min_order_value DECIMAL(10,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (type_id) REFERENCES discount_types(type_id) ON DELETE CASCADE
);

-- ORDERS
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT DEFAULT NULL,
    order_status ENUM('new', 'preparing', 'completed', 'cancelled') DEFAULT 'new',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL
);

CREATE TABLE order_items (
    order_id INT,
    item_id INT,
    quantity INT NOT NULL DEFAULT 1,
    PRIMARY KEY (order_id, item_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (item_id) REFERENCES menu_items(item_id)
);

CREATE TABLE order_payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    payment_type ENUM('cash', 'card', 'upi', 'paypal') DEFAULT 'cash',
    amount_paid DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

CREATE TABLE order_bills (
    order_id INT PRIMARY KEY,
    total_price DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    discount_applied DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    final_price DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    payment_status ENUM('pending', 'partially_paid', 'paid', 'failed') DEFAULT 'pending',
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

CREATE TABLE order_discounts (
	order_discount_id INT PRIMARY KEY AUTO_INCREMENT, 
    order_id INT NOT NULL,
    discount_id INT DEFAULT NULL,
    loyalty_points_used INT DEFAULT 0 CHECK (loyalty_points_used >= 0),
    discount_amount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (discount_id) REFERENCES discounts(discount_id) ON DELETE SET NULL
);

-- LOYALTY PROGRAMS
CREATE TABLE loyalty_tiers(
    tier_id INT PRIMARY KEY AUTO_INCREMENT,
    tier_name VARCHAR(30) NOT NULL,
    min_points INT NOT NULL,
    max_points INT NOT NULL
);

CREATE TABLE loyalty_program(
    loyalty_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    total_points INT DEFAULT 0 CHECK (total_points >= 0),
    tier_id INT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (tier_id) REFERENCES loyalty_tiers(tier_id) ON DELETE CASCADE
);

CREATE TABLE loyalty_points_logs(
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_id INT NULL,
    points_earned INT NULL,
    points_redeemed INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE SET NULL
);

-- FEEDBACKS AND COMPLAINTS

CREATE TABLE review_categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(30) NOT NULL
);

CREATE TABLE feedbacks (
    feedback_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NULL,
    order_id INT NULL,
    item_id INT NULL,
    category_id INT NOT NULL,
    rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 10),
    comments TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES review_categories(category_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES menu_items(item_id) ON DELETE SET NULL
);

CREATE TABLE complaints (
    complaint_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NULL,
    order_id INT NULL,
    category_id INT NOT NULL,
    item_id INT NULL,
    comments TEXT NOT NULL,
    status ENUM('pending', 'resolved', 'in_progress', 'dismissed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES review_categories(category_id) ON DELETE CASCADE
);


-- PROCEDURES

-- 1. Get customer order counts
DELIMITER //
CREATE PROCEDURE GetCustomerOrderCounts()
BEGIN
    SELECT
        c.name, 
        c.email, 
        c.date_of_birth, 
        c.mobile_no, 
        COUNT(o.customer_id) AS total_no_of_orders
    FROM customers AS c
    INNER JOIN orders AS o
    ON o.customer_id = c.customer_id
    GROUP BY c.customer_id;
END;
//
DELIMITER ;

-- 2. Get top spending customers (pass a number as an argument)
DELIMITER //
CREATE PROCEDURE GetTopSpendingCustomers(IN result_count int)
BEGIN
    SELECT 
        c.name, 
        SUM(ob.total_price) AS total_spent
    FROM orders AS o
    INNER JOIN order_bills AS ob
        ON o.order_id = ob.order_id
    INNER JOIN customers AS c
        ON o.customer_id = c.customer_id
    GROUP BY c.customer_id
    ORDER BY total_spent DESC
    LIMIT result_count;
END;
//
DELIMITER ;

-- 3. Get monthly revenue
DELIMITER //
CREATE PROCEDURE GetMonthlyRevenue()
BEGIN
    SELECT 
        MONTH(o.created_at) AS month,
        SUM(ob.total_price) AS total_potential_revenue,
        SUM(ob.final_price) AS total_collected_revenue
    FROM orders AS o
    INNER JOIN order_bills AS ob
        ON o.order_id = ob.order_id
    GROUP BY MONTH(o.created_at);
END;
//
DELIMITER ;

-- 4. Get customer average spending
DELIMITER //
CREATE PROCEDURE GetCustomerAverageSpending()
BEGIN
    SELECT 
        c.name, 
        AVG(ob.total_price) AS average_order_value
    FROM orders AS o
    INNER JOIN order_bills AS ob
        ON o.order_id = ob.order_id
    INNER JOIN customers AS c
        ON c.customer_id = o.customer_id
    GROUP BY c.customer_id;
END;
//
DELIMITER ;

-- 5. Get peak order hours
DELIMITER //
CREATE PROCEDURE GetPeakOrderHours()
BEGIN
    SELECT 
        HOUR(created_at) AS order_hour, 
        COUNT(order_id) AS order_count
    FROM orders 
    GROUP BY HOUR(created_at)
    ORDER BY order_count DESC;
END;
//
DELIMITER ;

-- 6. Get redeemed points percentage
DELIMITER //
CREATE PROCEDURE GetRedeemedPointsPercentage()
BEGIN
    SELECT 
        (SELECT COUNT(order_id) 
         FROM loyalty_points_logs 
         WHERE points_redeemed IS NOT NULL) 
        * 100.0 / NULLIF((SELECT COUNT(order_id) FROM loyalty_points_logs), 0) AS Percentage;
END;
//
DELIMITER ;

-- 7. Get most ordered menu items
DELIMITER //
CREATE PROCEDURE GetMostOrderedMenuItems()
BEGIN
    SELECT 
        m.*, 
        COUNT(o.order_id) AS total_orders
    FROM menu_items AS m
    INNER JOIN order_items AS o
        ON m.item_id = o.item_id
    GROUP BY o.item_id
    ORDER BY total_orders DESC;
END;
//
DELIMITER ;

-- 8. Get complaint category counts
DELIMITER //
CREATE PROCEDURE GetComplaintCategoryCounts()
BEGIN
    SELECT 
        rc.category_name, 
        COUNT(c.category_id) AS no_of_complaints
    FROM complaints AS c
    INNER JOIN review_categories AS rc
        ON c.category_id = rc.category_id
    GROUP BY c.category_id
    ORDER BY no_of_complaints DESC;
END;
//
DELIMITER ;

-- 9. Get menu item average ratings
DELIMITER //
CREATE PROCEDURE GetMenuItemAverageRatings()
BEGIN
    SELECT 
        mi.item_name, 
        AVG(f.rating) AS avg_rating
    FROM feedbacks AS f
    JOIN menu_items AS mi 
        ON f.item_id = mi.item_id
    GROUP BY mi.item_name
    ORDER BY avg_rating DESC;
END;
//
DELIMITER ;

-- 10. Get frequent customers (pass a minimum order count)
DELIMITER //
CREATE PROCEDURE GetFrequentCustomers(IN min_orders INT)
BEGIN
    SELECT 
        c.*, 
        COUNT(o.order_id) AS order_count
    FROM customers AS c
    INNER JOIN orders AS o
        ON c.customer_id = o.customer_id
    GROUP BY c.customer_id
    HAVING COUNT(o.order_id) > min_orders;
END;
//
DELIMITER ;


CALL GetCustomerOrderCounts();
CALL GetTopSpendingCustomers(10);
CALL GetMonthlyRevenue();
CALL GetCustomerAverageSpending();
CALL GetPeakOrderHours();
CALL GetRedeemedPointsPercentage();
CALL GetMostOrderedMenuItems();
CALL GetComplaintCategoryCounts();
CALL GetMenuItemAverageRatings();
CALL GetFrequentCustomers(2);

