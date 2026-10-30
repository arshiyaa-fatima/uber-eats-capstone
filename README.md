# Uber Eats Operational & Customer Intelligence System

An end-to-end Machine Learning and Operational Intelligence system built to optimize food delivery logistics, predict delivery delays, extract actionable customer sentiment, and forecast demand surges.

---

## Project Overview

This capstone implements an end-to-end data analytics and machine learning pipeline for a food delivery marketplace. Combining unsupervised segmentation, natural language processing (NLP), supervised regression, and time-series forecasting, the project addresses core operational bottlenecks:

- **Customer Lifetime Value & Behavior:** Uncovering spending habits, order cadences, and behavioral cohorts.
- **Service Feedback Intelligence:** Identifying root causes of dissatisfaction through review sentiment and n-gram analysis.
- **Logistics ETA Precision:** Predicting end-to-end delivery transit duration based on spatial, prep-time, and environmental variables.
- **Fleet & Capacity Planning:** Forecasting hourly demand oscillations to optimize courier pre-allocation.

---

## Repository Structure

```text
uber-eats-capstone/
├── data/
│   ├── raw/                       # Raw input CSV datasets (orders, deliveries, reviews, etc.)
│   └── hourly_demand.csv          # Resampled hourly time-series dataset
├── docs/
│   └── business_insights.md       # Strategic insights, business interpretations, and recommendations
├── notebooks/
│   ├── day2_customer_restaurant_segmentation.ipynb
│   ├── day3_nlp_sentiment_analysis.ipynb
│   ├── day4_delivery_time_prediction.ipynb
│   └── day5_hourly_demand_forecasting.ipynb
├── scripts/
│   ├── generate_data.py           # Synthetic data generation engine
│   └── pipeline.py                # Standalone end-to-end operational ML pipeline
├── .gitignore
└── README.md
