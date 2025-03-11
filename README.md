# Cafe CRM Database Project

## Introduction
Cafe CRM is a database system designed to manage a cafe's customer relationships, orders, menu, discounts, loyalty programs, feedback, and complaints. The system includes structured tables, relationships, constraints, and stored procedures to ensure efficient data management and business insights.

## Database Schema

### 1. Customers
Stores customer details such as name, email, mobile number, and date of birth.

### 2. Menu
- `menu_categories`: Categorizes menu items.
- `menu_items`: Contains individual menu items, linked to categories with prices.

### 3. Discounts
- `discount_types`: Defines types of discounts.
- `discounts`: Manages available discounts, their values, and eligibility criteria.

### 4. Orders
- `orders`: Tracks customer orders and their statuses.
- `order_items`: Links menu items to orders with quantities.
- `order_payments`: Records payments with different payment types.
- `order_bills`: Stores order totals, applied discounts, and payment status.
- `order_discounts`: Logs discount applications and loyalty points used.

### 5. Loyalty Programs
- `loyalty_tiers`: Defines loyalty membership tiers based on points.
- `loyalty_program`: Tracks customer loyalty points and membership tiers.
- `loyalty_points_logs`: Logs loyalty points earned and redeemed.

### 6. Feedback & Complaints
- `review_categories`: Defines categories for feedback.
- `feedbacks`: Captures customer feedback, ratings, and comments.
- `complaints`: Stores customer complaints and their resolution statuses.

## Stored Procedures
The database includes several stored procedures to generate reports and insights:
1. `GetCustomerOrderCounts()` - Retrieves order counts per customer.
2. `GetTopSpendingCustomers(IN result_count INT)` - Fetches top spenders.
3. `GetMonthlyRevenue()` - Computes monthly revenue statistics.
4. `GetCustomerAverageSpending()` - Determines average spending per customer.
5. `GetPeakOrderHours()` - Finds peak ordering hours.
6. `GetRedeemedPointsPercentage()` - Calculates the percentage of redeemed loyalty points.
7. `GetMostOrderedMenuItems()` - Identifies the most ordered menu items.
8. `GetComplaintCategoryCounts()` - Counts complaints per category.
9. `GetMenuItemAverageRatings()` - Computes average ratings for menu items.
10. `GetFrequentCustomers(IN min_orders INT)` - Lists customers with high order counts.

## Usage
- The database is created using MySQL.
- Run `CREATE DATABASE cafe_crm;` before executing the schema.
- Ensure proper indexing for optimized performance.
- Use stored procedures for data analysis and reports.

## Conclusion
Cafe CRM provides an efficient way to manage a cafe’s operations, ensuring seamless customer experience, optimized order handling, and actionable business insights through structured data management.
