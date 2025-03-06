
CREATE DATABASE cafe_crm;
USE cafe_crm;

-- ----------------- CUSTOMER ------------------

CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(256) NOT NULL,
    email VARCHAR(256) UNIQUE,
    mobile_no VARCHAR(15) UNIQUE,
    date_of_birth DATE
);


-- --------------------------------------------

-- ----------------- MENU ---------------------

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


-- -------------------------------------------

-- ---------------- DISCOUNTS -----------------

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
-- --------------------------------------------

-- ---------------- ORDERS --------------------

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

-- --------------------------------------------

-- ----------- LOYALTY PROGRAMS --------------

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

-- --------------------------------------------

-- -------- FEEDBACKS AND COMPLAINTS -----------

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

-- --------------------------------------------