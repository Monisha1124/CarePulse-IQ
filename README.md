# CarePulse IQ
### Turning Data Into Better Decisions

**Track:** Track 02 – Customers, Channels & Demand

CarePulse IQ is a healthcare appointment demand analytics and decision-support platform designed to help healthcare providers understand patient booking patterns, identify demand trends, evaluate appointment channels, and plan service capacity.

## Problem Statement

Healthcare providers often struggle to understand appointment demand across booking channels and medical departments. Poor visibility into booking patterns can lead to inefficient capacity allocation, appointment overload, and unused appointment slots.

## Our Solution

CarePulse IQ transforms appointment records into actionable insights through an interactive analytics dashboard, demand forecasting, channel analysis, and capacity planning.

## Key Features

- **Appointment Analytics:** Monitor total appointments and appointment outcomes.
- **Channel Performance:** Compare Website, Mobile App, Phone, Walk-in, and WhatsApp booking channels.
- **Department Demand:** Analyze demand across medical departments.
- **Demand Forecasting:** Generate a 14-day appointment demand forecast using a Random Forest model.
- **Capacity Planning:** Compare daily appointment demand against an adjustable demonstration capacity threshold.
- **Risk Segmentation:** Explore descriptive appointment segments associated with no-shows.
- **Interactive Filters:** Filter analytics by booking channel and department.
- **Report Export:** Download filtered analytics reports as ZIP files containing CSV reports.
- **Data Validation:** Detect missing columns, invalid dates, duplicate appointment IDs, and invalid values.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend | Flask |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| Visualization | Plotly |
| Frontend | HTML, CSS, JavaScript |
| Data Storage | CSV |
| Testing | Pytest |

## Project Structure

```text
CarePulse_IQ/
│
├── app/
│   ├── main.py
│   ├── analytics.py
│   ├── database.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/
│       └── js/
│
├── data/
│   └── appointments.csv
│
├── scripts/
│   └── generate_data.py
│
├── tests/
│   └── test_analytics.py
│
├── requirements.txt
├── README.md
└── LICENSE
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd CarePulse_IQ
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
pip install pytest
```

### 5. Generate the dataset

```bash
python scripts/generate_data.py
```

### 6. Run the application

```bash
python app/main.py
```

Open:

```text
http://127.0.0.1:5000
```

## Run Automated Tests

```bash
python -m pytest -q
```

## Dataset Information

The current prototype uses 1,500 synthetically generated appointment records.

The dataset includes:

- Appointment ID
- Booking date
- Appointment date
- Booking channel
- Medical department
- Patient age
- Advance booking days
- Appointment status

**Important:** The dataset is synthetic and does not contain real patient records.

## Limitations and Future Enhancements

- Integrate a real healthcare appointment database.
- Add configurable hospital-specific staffing and capacity information.
- Evaluate forecasting against real historical appointment data.
- Improve no-show prediction with validated real-world data.
- Add secure user authentication and role-based access.
- Integrate Exasol if available and authorized for the competition environment.

## Responsible Use

CarePulse IQ is an analytics and planning prototype. Its forecasts and risk segments are not medical diagnoses and should not be used to make individual patient-care decisions.

Capacity thresholds are demonstration assumptions and must be configured using actual operational data before real-world use.

## License

This project is released under the MIT License.
