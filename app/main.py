import io
import zipfile
from flask import send_file
from flask import Flask, render_template, jsonify, request

try:
    from .analytics import (
        load_data,
        get_overview,
        get_channel_performance,
        get_department_demand,
        get_daily_demand,
        get_weekday_demand,
        get_advance_booking_analysis,
        get_risk_segments,
        generate_insights,
        run_full_analysis,
        get_demand_forecast
    )
except ImportError:
    from analytics import (
        load_data,
        get_overview,
        get_channel_performance,
        get_department_demand,
        get_daily_demand,
        get_weekday_demand,
        get_advance_booking_analysis,
        get_risk_segments,
        generate_insights,
        run_full_analysis,
        get_demand_forecast
    )
app = Flask(__name__)


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/api/filters")
def filter_options():
    df = load_data()

    return jsonify({
        "channels": sorted(df["channel"].dropna().unique().tolist()),
        "departments": sorted(df["department"].dropna().unique().tolist())
    })


@app.route("/api/dashboard")
def dashboard_api():
    df = load_data()

    selected_channel = request.args.get("channel", "All")
    selected_department = request.args.get("department", "All")

    if selected_channel != "All":
        df = df[df["channel"] == selected_channel]

    if selected_department != "All":
        df = df[df["department"] == selected_department]

    if df.empty:
        return jsonify({"error": "No appointments match these filters."}), 404

    daily = get_daily_demand(df)

    return jsonify({
        "overview": get_overview(df),
        "channels": get_channel_performance(df).to_dict(orient="records"),
        "departments": get_department_demand(df).to_dict(orient="records"),
        "daily_demand": [
            {
                "date": row["appointment_date"].strftime("%Y-%m-%d"),
                "appointments": int(row["appointments"])
            }
            for _, row in daily.iterrows()
        ],
        "weekday_demand": get_weekday_demand(df).to_dict(
            orient="records"
        ),
        "insights": generate_insights(df)
    })


@app.route("/api/forecast")
def forecast_api():
    df = load_data()
    result = get_demand_forecast(df, forecast_days=14)
    return jsonify(result)

@app.route("/api/capacity")
def capacity_api():
    df = load_data()

    selected_channel = request.args.get("channel", "All")
    selected_department = request.args.get("department", "All")

    if selected_channel != "All":
        df = df[df["channel"] == selected_channel]

    if selected_department != "All":
        df = df[df["department"] == selected_department]

    if df.empty:
        return jsonify({"error": "No matching appointments."}), 404

    capacity = 25

    daily = (
        df.groupby("appointment_date")
        .size()
        .reset_index(name="demand")
        .sort_values("appointment_date")
    )

    daily["capacity"] = capacity
    daily["unused_slots"] = (
        daily["capacity"] - daily["demand"]
    ).clip(lower=0)

    daily["shortage"] = (
        daily["demand"] - daily["capacity"]
    ).clip(lower=0)

    daily["status"] = daily["demand"].apply(
        lambda demand: (
            "OVER CAPACITY" if demand > capacity
            else "NEAR CAPACITY" if demand >= capacity * 0.8
            else "WITHIN CAPACITY"
        )
    )

    alerts = daily[daily["shortage"] > 0]

    return jsonify({
        "daily_capacity": [
            {
                "date": row["appointment_date"].strftime("%Y-%m-%d"),
                "demand": int(row["demand"]),
                "capacity": int(row["capacity"]),
                "shortage": int(row["shortage"]),
                "unused_slots": int(row["unused_slots"]),
                "status": row["status"]
            }
            for _, row in daily.iterrows()
        ],
        "summary": {
            "capacity_per_day": capacity,
            "days_analyzed": len(daily),
            "over_capacity_days": len(alerts),
            "total_shortage_slots": int(alerts["shortage"].sum())
        }
    })


@app.route("/api/export")
def export_reports():
    df = load_data()

    selected_channel = request.args.get("channel", "All")
    selected_department = request.args.get("department", "All")

    if selected_channel != "All":
        df = df[df["channel"] == selected_channel]

    if selected_department != "All":
        df = df[df["department"] == selected_department]

    if df.empty:
        return jsonify({"error": "No matching records to export."}), 404

    channel_report = get_channel_performance(df)
    department_report = get_department_demand(df)

    daily_report = (
        df.groupby("appointment_date")
        .size()
        .reset_index(name="appointments")
    )

    capacity = 25
    daily_report["capacity"] = capacity
    daily_report["shortage"] = (
        daily_report["appointments"] - capacity
    ).clip(lower=0)
    daily_report["status"] = daily_report["appointments"].apply(
        lambda value: (
            "OVER CAPACITY" if value > capacity
            else "NEAR CAPACITY" if value >= capacity * 0.8
            else "WITHIN CAPACITY"
        )
    )

    memory_file = io.BytesIO()

    with zipfile.ZipFile(
        memory_file, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as archive:
        archive.writestr(
            "appointment_records.csv",
            df.to_csv(index=False)
        )

        archive.writestr(
            "channel_performance.csv",
            channel_report.to_csv(index=False)
        )

        archive.writestr(
            "department_demand.csv",
            department_report.to_csv(index=False)
        )

        archive.writestr(
            "daily_capacity_report.csv",
            daily_report.to_csv(index=False)
        )

    memory_file.seek(0)

    return send_file(
        memory_file,
        mimetype="application/zip",
        as_attachment=True,
        download_name="CarePulse_IQ_Analytics_Reports.zip"
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)

