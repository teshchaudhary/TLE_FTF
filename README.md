Here’s a refined version of your README with improved readability and structure:

---

# 🌍 Disaster Monitor

**Disaster Monitor** is a **real-time disaster tracking system** built with **FastAPI**, **Elasticsearch**, and **Streamlit**. It allows users to **search, filter, visualize, and monitor natural disasters** and alerts across various locations. The system provides an **interactive dashboard** for real-time data exploration and analysis.

---

## 🛠 Features

### **Backend (FastAPI + Elasticsearch)**

* **Disaster Index & API**:

  * Search disasters by:

    * Keyword
    * Disaster type (e.g., earthquake, flood, cyclone, wildfire, tsunami)
    * Location
    * Date range
    * Max results
  * Programmatically ingest disaster data via the `/disasters/fetch` endpoint.
* **Alerts Index & API**:

  * Search alerts by:

    * Severity (low, medium, high)
    * Max results
  * Periodic alert generation (configurable frequency via `run_alerts.py`).

---

### **Frontend (Streamlit Dashboard)**

* **Sidebar Filters**:

  * Keyword search
  * Filter by disaster type and severity (with an "All" option)
  * Location filter
  * Date range with an "All Dates" checkbox
  * Alert severity filter
  * Max results slider

* **Disaster Table**:

  * Displays essential disaster info like:

    * Title, type, severity, location, publication date, source, and links

* **Timeline Chart**:

  * Visualizes disaster counts over time, grouped by severity.

* **Alerts Table**:

  * Displays the latest alerts with type, severity, and timestamp.

* **Latest Alert Marquee**:

  * Dynamically displays the most recent alerts in a scrolling marquee.

* **Interactive Map**:

  * Displays scatter plot and heatmap layers for disasters and alerts.
  * Color-coded by severity, with tooltips providing detailed info and clickable links.

* **Legend**:

  * Clearly maps colors to disaster and alert severity levels.

---

## 📂 Project Structure

```
disaster_monitor
├── .env
├── .git
├── .gitignore
├── README.md
├── backend
│   ├── app
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routes
│   │   │   ├── __init__.py
│   │   │   ├── alerts.py
│   │   │   └── disasters.py
│   │   └── services
│   │       ├── alerts.py
│   │       ├── elastic.py
│   │       ├── fetch_news.py
│   │       └── nlp.py
│   └── requirements.txt
├── data
│   ├── disasters.parquet
│   └── logs
│       └── pipeline.log
├── elastic
│   ├── kibana
│   └── mappings
│       ├── alerts.json
│       └── disasters.json
├── frontend
│   ├── app.py
│   ├── components
│   │   ├── alerts_marquee.py
│   │   ├── disasters_table.py
│   │   ├── filters.py
│   │   ├── legend.py
│   │   ├── map_view.py
│   │   └── timeline_chart.py
│   └── requirements.txt
└── scripts
    ├── create_alerts_index.py
    ├── fetch_and_index.py
    └── run_alerts.py
```

---

## ⚙️ Setup Instructions

### **Prerequisites**

* Python 3.13+
* Elasticsearch 8.x (local or remote)
* Streamlit
* FastAPI
* Uvicorn

**Python Dependencies**:

```bash
pip install -r requirements.txt
```

---

### **1. Elasticsearch Setup**

1. Install Elasticsearch and start it locally:

   ```bash
   wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.10.0-linux-x86_64.tar.gz
   tar -xzf elasticsearch-8.10.0-linux-x86_64.tar.gz
   cd elasticsearch-8.10.0
   ./bin/elasticsearch
   ```

2. Create the disaster and alert indices:

   ```bash
   python backend/scripts/create_disasters_index.py
   python backend/scripts/create_alerts_index.py
   ```

---

### **2. Run the Backend**

Start FastAPI with Uvicorn:

```bash
uvicorn backend.app.main:app --reload
```

**API Endpoints**:

* `GET /disasters/search` – Search disasters
* `POST /disasters/fetch` – Ingest new disasters
* `GET /alerts/search` – Search alerts
* `POST /alerts/run` – Run alert generation script

---

### **3. Run the Frontend**

Start the Streamlit dashboard:

```bash
cd frontend
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

---

## 📚 Usage Notes

* Filters allow you to select "All" for disaster types, severity, and date ranges.
* Latest alerts are displayed in a dynamic, scrolling marquee.
* The interactive map allows you to click disaster pins to view more details and navigate to external sources.
* The timeline chart shows disaster counts over time, grouped by severity.

---
