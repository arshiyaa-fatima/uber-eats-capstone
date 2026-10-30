"""
Uber Eats Operational & Customer Intelligence System
End-to-End ML Pipeline (Day 6 Deliverable)
"""

import pandas as pd
import numpy as np
import os
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestRegressor
from statsmodels.tsa.arima.model import ARIMA
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score

# Ensure data folder exists
DATA_DIR = '../data/raw' if os.path.exists('../data/raw') else 'data/raw'

print(">>> [Step 1/5] Ingesting Raw Datasets...")
orders = pd.read_csv(os.path.join(DATA_DIR, 'orders.csv'))
reviews = pd.read_csv(os.path.join(DATA_DIR, 'reviews.csv'))
deliveries = pd.read_csv(os.path.join(DATA_DIR, 'deliveries.csv'))

# Preprocess timestamps
orders['order_timestamp'] = pd.to_datetime(orders['order_timestamp'])
orders['is_weekend'] = orders['order_timestamp'].dt.dayofweek >= 5
orders['is_late_night'] = (orders['order_timestamp'].dt.hour >= 22) | (orders['order_timestamp'].dt.hour < 4)
orders['is_cancelled'] = (orders['order_status'] == 'Cancelled').astype(int)

# --- Module 1: Customer Segmentation ---
print(">>> [Step 2/5] Running Customer Segmentation (K-Means)...")
cust_orders = orders.groupby('customer_id').agg(
    total_orders=('order_id', 'count'),
    total_spending=('order_amount', 'sum'),
    average_order_value=('order_amount', 'mean'),
    weekend_orders=('is_weekend', 'sum'),
    late_night_orders=('is_late_night', 'sum')
).reset_index()

cust_reviews = reviews.groupby('customer_id').agg(
    average_rating_given=('rating', 'mean')
).reset_index()

customer_features = pd.merge(cust_orders, cust_reviews, on='customer_id', how='left').fillna(0)
X_cust = customer_features.drop(columns=['customer_id'])

scaler = StandardScaler()
X_cust_scaled = scaler.fit_transform(X_cust)

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
customer_features['cluster'] = kmeans.fit_predict(X_cust_scaled)

# Name clusters based on profiles
cluster_names = {
    0: "Budget / Occasional Users",
    1: "Occasional High-Spenders",
    2: "Premium Frequent Night-Owls",
    3: "High-Value Regulars"
}
customer_features['segment_name'] = customer_features['cluster'].map(cluster_names)
print("Customer Segmentation Complete. Segments mapped:")
print(customer_features['segment_name'].value_counts())

# --- Module 2: NLP Customer Feedback & Sentiment Analysis ---
print(">>> [Step 3/5] Running NLP Customer Feedback & Sentiment Pipeline...")
reviews_filt = reviews[reviews['rating'] != 3].copy()
reviews_filt['sentiment_target'] = np.where(reviews_filt['rating'] > 3, 1, 0)

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    if not isinstance(text, str):
        return ""
    tokens = nltk.word_tokenize(text.lower())
    return " ".join([lemmatizer.lemmatize(w) for w in tokens if w.isalpha() and w not in stop_words])

reviews_filt['cleaned_text'] = reviews_filt['review_text'].apply(clean_text)

tfidf = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
X_nlp = tfidf.fit_transform(reviews_filt['cleaned_text'])
y_nlp = reviews_filt['sentiment_target']

X_tr_n, X_te_n, y_tr_n, y_te_n = train_test_split(X_nlp, y_nlp, test_size=0.2, random_state=42)
nb_clf = MultinomialNB()
nb_clf.fit(X_tr_n, y_tr_n)
nlp_acc = accuracy_score(y_te_n, nb_clf.predict(X_te_n))
print(f"NLP Sentiment Classifier Trained. Test Accuracy: {nlp_acc:.4f}")

# --- Module 3: Delivery Time Prediction Regression ---
print(">>> [Step 4/5] Training Delivery Time Regression Model...")
deliv_merged = pd.merge(orders, deliveries, on='order_id', how='inner')
deliv_merged['hour_of_day'] = deliv_merged['order_timestamp'].dt.hour
features_reg = [
    'order_amount', 'delivery_distance_km', 'prep_time_min',
    'weather_condition', 'traffic_condition', 'hour_of_day', 'is_weekend'
]
X_reg = pd.get_dummies(deliv_merged[features_reg], drop_first=True)
y_reg = deliv_merged['delivery_time_min']

X_tr_r, X_te_r, y_tr_r, y_te_r = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)
rf_reg = RandomForestRegressor(n_estimators=100, random_state=42)
rf_reg.fit(X_tr_r, y_tr_r)
y_pred_reg = rf_reg.predict(X_te_r)

print(f"Regression Trained. MAE: {mean_absolute_error(y_te_r, y_pred_reg):.2f} mins | R²: {r2_score(y_te_r, y_pred_reg):.4f}")

# --- Module 4: Hourly Demand Time-Series Forecasting ---
print(">>> [Step 5/5] Fitting Hourly Demand Forecasting Engine...")
hourly_ts = orders.set_index('order_timestamp').resample('h').agg(order_count=('order_id', 'count')).fillna(0)
hourly_ts = hourly_ts.asfreq('h', fill_value=0)

arima = ARIMA(hourly_ts['order_count'], order=(2, 0, 2))
arima_fit = arima.fit()
next_24h_forecast = arima_fit.forecast(steps=24)
print(f"Forecasting Complete. Next 24-Hour Projected Total Orders: {int(next_24h_forecast.sum())}")

print("\n>>> End-to-End Pipeline Execution Successful!")