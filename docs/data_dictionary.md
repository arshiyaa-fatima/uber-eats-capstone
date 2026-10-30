# Uber Eats Operational & Customer Intelligence System - Data Dictionary

This document outlines the schema and relationships for the 7 synthetic datasets generated for the Uber Eats Operational & Customer Intelligence System.

## 1. Customers (`customers.csv`)
Contains customer demographic and account information.

| Column | Data Type | Description |
| :--- | :--- | :--- |
| `customer_id` | String | Primary Key. Unique identifier for the customer (e.g., C00001). |
| `name` | String | Full name of the customer. |
| `city` | String | City of residence (Indian cities). |
| `signup_date` | Date | Date the customer registered on the platform. |

## 2. Restaurants (`restaurants.csv`)
Contains restaurant details and historical ratings.

| Column | Data Type | Description |
| :--- | :--- | :--- |
| `restaurant_id` | String | Primary Key. Unique identifier for the restaurant (e.g., R0001). |
| `name` | String | Name of the restaurant. |
| `category` | String | Cuisine type (e.g., North Indian, Biryani, Fast Food). |
| `avg_restaurant_rating` | Float | Average historical rating of the restaurant (3.0 to 5.0). |

## 3. Drivers (`drivers.csv`)
Contains delivery partner details and ratings.

| Column | Data Type | Description |
| :--- | :--- | :--- |
| `driver_id` | String | Primary Key. Unique identifier for the delivery driver (e.g., D0001). |
| `name` | String | Full name of the delivery driver. |
| `vehicle_type` | String | Vehicle used for delivery (Bike, Scooter). |
| `avg_driver_rating` | Float | Average historical rating of the driver (3.5 to 5.0). |

## 4. Orders (`orders.csv`)
Core transactional table recording all placed orders.

| Column | Data Type | Description |
| :--- | :--- | :--- |
| `order_id` | String | Primary Key. Unique identifier for the order (e.g., O000001). |
| `customer_id` | String | Foreign Key linking to `customers.csv`. |
| `restaurant_id` | String | Foreign Key linking to `restaurants.csv`. |
| `order_timestamp` | Datetime | Date and exact time the order was placed. |
| `order_amount` | Float | Total value of the order in INR (₹). |
| `order_status` | String | Current status of the order (Completed, Cancelled). |

## 5. Deliveries (`deliveries.csv`)
Contains logistical data, weather, traffic, and timing metrics for completed orders.

| Column | Data Type | Description |
| :--- | :--- | :--- |
| `delivery_id` | String | Primary Key. Unique identifier for the delivery leg. |
| `order_id` | String | Foreign Key linking to `orders.csv`. |
| `driver_id` | String | Foreign Key linking to `drivers.csv`. |
| `delivery_distance_km` | Float | Distance between restaurant and customer in kilometers. |
| `weather_condition` | String | Weather during delivery (Clear, Cloudy, Rain, Heavy Rain). |
| `traffic_condition` | String | Traffic level during delivery (Light, Moderate, Heavy, Gridlock). |
| `prep_time_min` | Integer | Time taken by the restaurant to prepare the food (in minutes). |
| `delivery_time_min` | Integer | Calculated transit time impacted by distance, weather, and traffic. |

## 6. Payments (`payments.csv`)
Contains payment methods, Copied to clipboardtip amounts, and transaction status.

| Column | Data Type | Description |
| :--- | :--- | :--- |
| `payment_id` | String | Primary Key. Unique identifier for the payment transaction. |
| `order_id` | String | Foreign Key linking to `orders.csv`. |
| `payment_method` | String | Mode of payment (UPI, Credit Card, Debit Card, Cash). |
| `tip_amount` | Float | Gratuity paid to the driver. Correlates negatively with delivery delays and positively with bad weather. |
| `payment_status` | String | Status of the transaction (Success). |

## 7. Reviews (`reviews.csv`)
Contains customer feedback, ratings, and NLP-ready review text.

| Column | Data Type | Description |
| :--- | :--- | :--- |
| `review_id` | String | Primary Key. Unique identifier for the review. |
| `order_id` | String | Foreign Key linking to `orders.csv`. |
| `customer_id` | String | Foreign Key linking to `customers.csv`. |
| `rating` | Integer | Rating given by the customer (1 to 5). Correlates with total wait time. |
| `review_text` | String | Textual feedback. Sentiment correlates with the numerical rating and wait time. |