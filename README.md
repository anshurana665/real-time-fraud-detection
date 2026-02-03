# Real-Time Fraud Detection System 🕵️‍♂️🚫

## Overview
An end-to-end data engineering pipeline that detects fraudulent financial transactions in real-time. The system ingests high-throughput data using Apache Kafka, processes it with a Random Forest Classifier, and visualizes vectors in a 3D Streamlit dashboard.

## Tech Stack
* **Ingestion:** Apache Kafka, Zookeeper
* **Containerization:** Docker, Docker Compose
* **ML Model:** Scikit-Learn (Random Forest), Pandas
* **Database:** PostgreSQL
* **Visualization:** Streamlit, Plotly (3D)
* **Alerting:** SMTP (Real-time Email Notifications)

## Key Features
* ✅ **Zero-Latency Detection:** Processes transactions as they arrive.
* ✅ **Dockerized Environment:** Entire stack launches with `docker compose up`.
* ✅ **Automated Alerts:** Emails security teams instantly upon fraud detection.