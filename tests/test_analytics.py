import io
import zipfile

import pytest

from app.main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def test_homepage_loads(client):
    response = client.get("/")
    assert response.status_code == 200


def test_filter_options(client):
    response = client.get("/api/filters")

    assert response.status_code == 200
    assert response.is_json


def test_dashboard_api(client):
    response = client.get("/api/dashboard")

    assert response.status_code == 200
    assert response.is_json


def test_dashboard_with_filters(client):
    response = client.get(
        "/api/dashboard?channel=Website&department=Dental"
    )

    assert response.status_code == 200
    assert response.is_json


def test_forecast_api(client):
    response = client.get("/api/forecast")

    assert response.status_code == 200
    assert response.is_json


def test_capacity_api(client):
    response = client.get("/api/capacity")

    assert response.status_code == 200
    assert response.is_json


def test_export_reports(client):
    response = client.get(
        "/api/export?channel=Website&department=Dental"
    )

    assert response.status_code == 200
    assert len(response.data) > 0

    zip_file = zipfile.ZipFile(io.BytesIO(response.data))
    exported_files = zip_file.namelist()

    expected_files = {
        "appointment_records.csv",
        "channel_performance.csv",
        "department_demand.csv",
        "daily_capacity_report.csv",
    }

    assert expected_files.issubset(set(exported_files))