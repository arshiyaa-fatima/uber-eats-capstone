import pandas as pd
import numpy as np
from faker import Faker
import os
from datetime import datetime, timedelta
import random

# Initialize Faker with Indian locale for grounded data
fake = Faker('en_IN')
np.random.seed(42)
Faker.seed(42)

# Configuration
NUM_CUSTOMERS = 1000
NUM_RESTAURANTS = 200
NUM_DRIVERS = 300
NUM_ORDERS = 5000
OUTPUT_DIR = 'data/raw/'

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Customers
print("Generating Customers...")
customers = pd.DataFrame({
    'customer_id': [f'C{str(i).zfill(5)}' for i in range(1, NUM_CUSTOMERS + 1)],
    'name': [fake.name() for _ in range(NUM_CUSTOMERS)],
    'city': [fake.city() for _ in range(NUM_CUSTOMERS)],
    'signup_date': [fake.date_between(start_date='-2y', end_date='today') for _ in range(NUM_CUSTOMERS)]
})

# 2. Restaurants
print("Generating Restaurants...")
categories = ['North Indian', 'South Indian', 'Biryani', 'Fast Food', 'Chinese', 'Desserts', 'Healthy Food']
restaurants = pd.DataFrame({
    'restaurant_id': [f'R{str(i).zfill(4)}' for i in range(1, NUM_RESTAURANTS + 1)],
    'name': [fake.company() + " " + random.choice(['Kitchen', 'Diner', 'Eatery', 'Cafe']) for _ in range(NUM_RESTAURANTS)],
    'category': np.random.choice(categories, NUM_RESTAURANTS),
    'avg_restaurant_rating': np.round(np.random.uniform(3.0, 5.0, NUM_RESTAURANTS), 1)
})

# 3. Drivers
print("Generating Drivers...")
drivers = pd.DataFrame({
    'driver_id': [f'D{str(i).zfill(4)}' for i in range(1, NUM_DRIVERS + 1)],
    'name': [fake.name() for _ in range(NUM_DRIVERS)],
    'vehicle_type': np.random.choice(['Bike', 'Scooter'], NUM_DRIVERS, p=[0.7, 0.3]),
    'avg_driver_rating': np.round(np.random.uniform(3.5, 5.0, NUM_DRIVERS), 1)
})

# 4. Orders
print("Generating Orders...")
start_time = datetime.now() - timedelta(days=180)
order_timestamps = [start_time + timedelta(minutes=random.randint(1, 180 * 24 * 60)) for _ in range(NUM_ORDERS)]

orders = pd.DataFrame({
    'order_id': [f'O{str(i).zfill(6)}' for i in range(1, NUM_ORDERS + 1)],
    'customer_id': np.random.choice(customers['customer_id'], NUM_ORDERS),
    'restaurant_id': np.random.choice(restaurants['restaurant_id'], NUM_ORDERS),
    'order_timestamp': sorted(order_timestamps),
    'order_amount': np.round(np.random.uniform(150.0, 2500.0, NUM_ORDERS), 2),
    'order_status': np.random.choice(['Completed', 'Cancelled'], NUM_ORDERS, p=[0.95, 0.05])
})

# Filter out cancelled orders for downstream successful delivery logic
completed_orders = orders[orders['order_status'] == 'Completed']['order_id'].tolist()
num_completed = len(completed_orders)

# 5. Deliveries
print("Generating Deliveries...")
weather_conditions = ['Clear', 'Cloudy', 'Rain', 'Heavy Rain']
traffic_conditions = ['Light', 'Moderate', 'Heavy', 'Gridlock']

deliveries = pd.DataFrame({
    'delivery_id': [f'DEL{str(i).zfill(6)}' for i in range(1, num_completed + 1)],
    'order_id': completed_orders,
    'driver_id': np.random.choice(drivers['driver_id'], num_completed),
    'delivery_distance_km': np.round(np.random.uniform(0.5, 12.0, num_completed), 1),
    'weather_condition': np.random.choice(weather_conditions, num_completed, p=[0.6, 0.2, 0.15, 0.05]),
    'traffic_condition': np.random.choice(traffic_conditions, num_completed, p=[0.3, 0.4, 0.2, 0.1]),
    'prep_time_min': np.random.randint(10, 30, num_completed)
})

# Statistical Correlation: Delivery time heavily depends on distance, weather, and traffic
def calculate_delivery_time(row):
    base_time = row['delivery_distance_km'] * 3.5 
    weather_penalty = {'Clear': 0, 'Cloudy': 2, 'Rain': 10, 'Heavy Rain': 20}[row['weather_condition']]
    traffic_penalty = {'Light': 0, 'Moderate': 5, 'Heavy': 15, 'Gridlock': 25}[row['traffic_condition']]
    
    total_time = base_time + weather_penalty + traffic_penalty + np.random.normal(2, 2)
    return max(5, int(total_time)) # Minimum 5 mins

deliveries['delivery_time_min'] = deliveries.apply(calculate_delivery_time, axis=1)

# 6. Payments
print("Generating Payments...")
payments = pd.DataFrame({
    'payment_id': [f'P{str(i).zfill(6)}' for i in range(1, num_completed + 1)],
    'order_id': completed_orders,
    'payment_method': np.random.choice(['UPI', 'Credit Card', 'Debit Card', 'Cash'], num_completed, p=[0.6, 0.2, 0.1, 0.1])
})

# Correlation: Tip amounts drop if delivery is delayed; higher tips during rain
def calculate_tip(order_id):
    delivery = deliveries[deliveries['order_id'] == order_id].iloc[0]
    order_val = orders[orders['order_id'] == order_id]['order_amount'].iloc[0]
    
    base_tip = order_val * 0.05
    if delivery['delivery_time_min'] > 45:
        base_tip = 0 # No tip for late delivery
    elif delivery['weather_condition'] in ['Rain', 'Heavy Rain']:
        base_tip *= 1.5 # Empathy tip
        
    return np.round(max(0, base_tip + np.random.normal(0, 10)), 0)

payments['tip_amount'] = [calculate_tip(oid) for oid in completed_orders]
payments['payment_status'] = 'Success'

# 7. Reviews
print("Generating Reviews...")
# Correlation: Sentiments and ratings directly reflect delivery times and prep times
def generate_review(order_id):
    delivery = deliveries[deliveries['order_id'] == order_id].iloc[0]
    total_time = delivery['prep_time_min'] + delivery['delivery_time_min']
    
    if total_time < 40:
        rating = np.random.choice([4, 5], p=[0.3, 0.7])
        texts = ["Super fast delivery!", "Food was piping hot.", "Great service and taste.", "Loved it!"]
    elif total_time < 60:
        rating = np.random.choice([3, 4], p=[0.6, 0.4])
        texts = ["Decent experience.", "Food was okay, slightly delayed.", "Standard delivery."]
    else:
        rating = np.random.choice([1, 2], p=[0.6, 0.4])
        texts = ["Terrible experience, food was cold.", "Took way too long to arrive.", "Driver was stuck in traffic forever.", "Will not order again."]
        
    return rating, random.choice(texts)

review_data = [generate_review(oid) for oid in completed_orders]
reviews = pd.DataFrame({
    'review_id': [f'REV{str(i).zfill(6)}' for i in range(1, num_completed + 1)],
    'order_id': completed_orders,
    'customer_id': [orders[orders['order_id'] == oid]['customer_id'].iloc[0] for oid in completed_orders],
    'rating': [r[0] for r in review_data],
    'review_text': [r[1] for r in review_data]
})

# Export all datasets
print("Exporting datasets to CSV...")
customers.to_csv(os.path.join(OUTPUT_DIR, 'customers.csv'), index=False)
restaurants.to_csv(os.path.join(OUTPUT_DIR, 'restaurants.csv'), index=False)
drivers.to_csv(os.path.join(OUTPUT_DIR, 'drivers.csv'), index=False)
orders.to_csv(os.path.join(OUTPUT_DIR, 'orders.csv'), index=False)
deliveries.to_csv(os.path.join(OUTPUT_DIR, 'deliveries.csv'), index=False)
payments.to_csv(os.path.join(OUTPUT_DIR, 'payments.csv'), index=False)
reviews.to_csv(os.path.join(OUTPUT_DIR, 'reviews.csv'), index=False)

print("Data generation complete. Files saved in:", OUTPUT_DIR)