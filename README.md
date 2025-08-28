---

# 🌍 Disaster Monitor

Disaster Monitor is a **real-time disaster tracking system** built with **FastAPI**, **Elasticsearch**, and **Streamlit**. It allows users to **search, filter, visualize, and monitor natural disasters** and alerts across locations, providing an interactive dashboard for data exploration.

---

## **Features Implemented**

### **Backend (FastAPI + Elasticsearch)**

* **Disaster Index & API**

  * Search disasters using:

    * Keyword
    * Disaster type (earthquake, flood, cyclone, wildfire, tsunami)
    * Location
    * Date range
    * Max results
  * Ingest disaster data programmatically via `/disasters/fetch`
* **Alerts Index & API**

  * Search alerts using:

    * Severity (low, medium, high)
    * Max results
  * Periodic alert generation script (`run_alerts.py`)
  * Supports testing with configurable frequency

### **Frontend (Streamlit Dashboard)**

* **Sidebar Filters**

  * Keyword search
  * Disaster type and severity (with "All" option)
  * Location
  * Date range with "All Dates" checkbox
  * Alert severity
  * Max results slider
* **Disaster Table**

  * Displays title, type, severity, location, publication date, source, and link
* **Timeline Chart**

  * Shows disaster counts over time grouped by severity
* **Alerts Table**

  * Displays latest alerts with type, severity, and timestamp
* **Latest Alert Marquee**

  * Dynamically displays the most recent alerts in a scrolling marquee
* **Interactive Map**

  * Scatter plot and heatmap layers for disasters and alerts
  * Color-coded by severity
  * Tooltip with detailed info including clickable link
* **Legend**

  * Clearly maps colors to severity levels for disasters and alerts

---

## **Project Structure**

```
disaster_monitor/
│
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI entrypoint
│   │   ├── routes/
│   │   │   ├── disasters.py   # Disasters API endpoints
│   │   │   └── alerts.py      # Alerts API endpoints
│   │   └── utils/             # Helper functions (optional)
│   └── scripts/
│       ├── create_disasters_index.py
│       ├── create_alerts_index.py
│       └── run_alerts.py
│
├── frontend/
│   └── app.py                 # Streamlit dashboard
│
├── requirements.txt           # Python dependencies
└── README.md
```

---

## **Prerequisites**

* Python 3.13+
* Elasticsearch 8.x (running locally or accessible remotely)
* Streamlit
* FastAPI
* Uvicorn

**Python Dependencies:**

```bash
pip install -r requirements.txt
```

**requirements.txt example:**

```
fastapi
uvicorn
elasticsearch
streamlit
pandas
pydeck
altair
requests
```

---

## **Setup Instructions**

### **1. Elasticsearch Setup**

* Install Elasticsearch and start it locally:

```bash
# Example for Linux
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.10.0-linux-x86_64.tar.gz
tar -xzf elasticsearch-8.10.0-linux-x86_64.tar.gz
cd elasticsearch-8.10.0
./bin/elasticsearch
```

* Create indices for disasters and alerts:

```bash
python backend/scripts/create_disasters_index.py
python backend/scripts/create_alerts_index.py
```

### **2. Run Backend**

* Start FastAPI with Uvicorn:

```bash
uvicorn backend.app.main:app --reload
```

* API endpoints:

  * `GET /disasters/search` – search disasters
  * `POST /disasters/fetch` – fetch and ingest new disasters
  * `GET /alerts/search` – search alerts
  * `POST /alerts/run` – run alert generation script

### **3. Run Frontend**

* Start Streamlit dashboard:

```bash
cd frontend
streamlit run app.py
```

* Open the local URL in your browser (usually `http://localhost:8501`)

---

## **Usage Notes**

* Filters allow selecting "All" for disaster types, severity, and date ranges.
* Latest alerts are displayed in a scrolling marquee.
* Map is interactive: click pins to view details and navigate to source links.
* Timeline shows counts of disasters over time grouped by severity.

---

## **To-Do / Next Steps**

* Rotate multiple alerts in marquee
* Add sorting and pagination for tables
* Enhance map interactivity (hover info, cluster markers)
* Integrate disaster `content` in table and tooltips
* Unit tests for APIs and scripts
* Dockerize backend and frontend for deployment

---
