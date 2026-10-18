import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import pandas as pd
import os


DATA_FILE = os.path.join("data", "appointments.csv")


def load_data():
    from pathlib import Path
    import pandas as pd

    project_root = Path(__file__).resolve().parent.parent
    data_path = project_root / "data" / "appointments.csv"

    if not data_path.exists():
        raise FileNotFoundError(
            "appointments.csv not found. "
            "Run: python scripts/generate_data.py"
        )

    df = pd.read_csv(data_path)

    required_columns = [
        "appointment_id",
        "booking_date",
        "appointment_date",
        "day_of_week",
        "channel",
        "department",
        "patient_age",
        "days_in_advance",
        "status"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if df.empty:
        raise ValueError("Appointment dataset is empty.")

    if df["appointment_id"].isnull().any():
        raise ValueError("Appointment IDs cannot be empty.")

    if df["appointment_id"].duplicated().any():
        raise ValueError("Duplicate appointment IDs detected.")

    df["booking_date"] = pd.to_datetime(
        df["booking_date"], errors="coerce"
    )

    df["appointment_date"] = pd.to_datetime(
        df["appointment_date"], errors="coerce"
    )

    if df["appointment_date"].isnull().any():
        raise ValueError("Invalid appointment dates detected.")

    if df["booking_date"].isnull().any():
        raise ValueError("Invalid booking dates detected.")

    if (df["patient_age"] < 0).any():
        raise ValueError("Patient age cannot be negative.")

    if (df["days_in_advance"] < 0).any():
        raise ValueError("Advance booking days cannot be negative.")

    return df


def get_overview(df):
    """Calculate overall business performance."""

    total = len(df)
    completed = int((df["status"] == "COMPLETED").sum())
    no_shows = int((df["status"] == "NO_SHOW").sum())

    no_show_rate = (
        round((no_shows / total) * 100, 2)
        if total else 0
    )

    completion_rate = (
        round((completed / total) * 100, 2)
        if total else 0
    )

    return {
        "total_appointments": total,
        "completed_appointments": completed,
        "no_show_appointments": no_shows,
        "no_show_rate": no_show_rate,
        "completion_rate": completion_rate
    }


def get_channel_performance(df):
    """Compare appointment channels."""

    result = (
        df.groupby("channel")
        .agg(
            total_appointments=("appointment_id", "count"),
            no_shows=("status", lambda x: (x == "NO_SHOW").sum())
        )
        .reset_index()
    )

    result["no_show_rate"] = (
        result["no_shows"] /
        result["total_appointments"] * 100
    ).round(2)

    return result.sort_values(
        "total_appointments", ascending=False
    )


def get_department_demand(df):
    """Identify departments with the highest demand."""

    result = (
        df.groupby("department")
        .size()
        .reset_index(name="appointments")
        .sort_values("appointments", ascending=False)
    )

    return result


def get_daily_demand(df):
    """Calculate demand for each appointment date."""

    result = (
        df.groupby("appointment_date")
        .size()
        .reset_index(name="appointments")
        .sort_values("appointment_date")
    )

    return result


def get_weekday_demand(df):
    """Compare demand across weekdays."""

    weekday_order = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    result = (
        df.groupby("day_of_week")
        .size()
        .reindex(weekday_order, fill_value=0)
        .reset_index(name="appointments")
    )

    return result


def get_advance_booking_analysis(df):
    """Analyze how early appointments are booked."""

    result = (
        df.groupby("days_in_advance")
        .agg(
            total_appointments=("appointment_id", "count"),
            no_shows=("status", lambda x: (x == "NO_SHOW").sum())
        )
        .reset_index()
    )

    result["no_show_rate"] = (
        result["no_shows"] /
        result["total_appointments"] * 100
    ).round(2)

    return result


def get_risk_segments(df):
    """
    Identify appointment segments with elevated no-show rates.
    This is descriptive analysis, not an individual prediction.
    """

    result = (
        df.groupby(["channel", "days_in_advance"])
        .agg(
            total_appointments=("appointment_id", "count"),
            no_shows=("status", lambda x: (x == "NO_SHOW").sum())
        )
        .reset_index()
    )

    result = result[result["total_appointments"] >= 5].copy()

    result["no_show_rate"] = (
        result["no_shows"] /
        result["total_appointments"] * 100
    ).round(2)

    return result.sort_values(
        "no_show_rate", ascending=False
    )


def generate_insights(df):
    """Generate understandable business recommendations."""

    insights = []

    overview = get_overview(df)
    channels = get_channel_performance(df)
    departments = get_department_demand(df)
    weekdays = get_weekday_demand(df)

    if not channels.empty:
        worst_channel = channels.iloc[
            channels["no_show_rate"].argmax()
        ]

        insights.append(
            f"{worst_channel['channel']} has the highest "
            f"observed channel no-show rate "
            f"({worst_channel['no_show_rate']}%). "
            "Consider testing reminder messages for this channel."
        )

    if not departments.empty:
        top_department = departments.iloc[0]

        insights.append(
            f"{top_department['department']} has the highest "
            f"appointment demand with "
            f"{top_department['appointments']} appointments. "
            "Review staffing and appointment capacity."
        )

    if not weekdays.empty:
        busiest_day = weekdays.loc[
            weekdays["appointments"].idxmax()
        ]

        insights.append(
            f"{busiest_day['day_of_week']} is the busiest "
            f"appointment day with "
            f"{busiest_day['appointments']} appointments. "
            "Consider allocating additional capacity."
        )

    insights.append(
        f"The overall observed no-show rate is "
        f"{overview['no_show_rate']}%. "
        "Monitor this metric regularly to evaluate improvements."
    )

    return insights


def run_full_analysis():
    """Run all analytics and return results."""

    df = load_data()

    return {
        "overview": get_overview(df),
        "channels": get_channel_performance(df),
        "departments": get_department_demand(df),
        "daily_demand": get_daily_demand(df),
        "weekday_demand": get_weekday_demand(df),
        "advance_booking": get_advance_booking_analysis(df),
        "risk_segments": get_risk_segments(df),
        "insights": generate_insights(df)
    }

def build_forecast_features(series):
    """Create time-series features using only past appointment demand."""

    frame = pd.DataFrame({"appointments": series})

    frame["lag_1"] = frame["appointments"].shift(1)
    frame["lag_7"] = frame["appointments"].shift(7)
    frame["lag_14"] = frame["appointments"].shift(14)

    frame["rolling_mean_7"] = (
        frame["appointments"].shift(1).rolling(7).mean()
    )

    frame["day_of_week"] = frame.index.dayofweek
    frame["month"] = frame.index.month
    frame["day_of_year"] = frame.index.dayofyear

    return frame.dropna()


def get_demand_forecast(df, forecast_days=14):
    """
    Train a Random Forest model and forecast future daily demand.

    Evaluation uses a chronological holdout with actual historical
    lag values. Future forecasts are generated recursively.
    """

    daily = (
        df.groupby("appointment_date")
        .size()
        .sort_index()
    )

    # Include dates with zero appointments.
    full_dates = pd.date_range(
        daily.index.min(),
        daily.index.max(),
        freq="D"
    )

    series = daily.reindex(full_dates, fill_value=0)
    series.index.name = "date"

    features = build_forecast_features(series)

    feature_columns = [
        "lag_1",
        "lag_7",
        "lag_14",
        "rolling_mean_7",
        "day_of_week",
        "month",
        "day_of_year"
    ]

    if len(features) < 40:
        raise ValueError(
            "Not enough historical data to train the forecasting model."
        )

    X = features[feature_columns]
    y = features["appointments"]

    # Chronological 80/20 split. No random shuffling.
    split_index = int(len(features) * 0.8)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]
    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    evaluation_model = RandomForestRegressor(
        n_estimators=250,
        max_depth=8,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    evaluation_model.fit(X_train, y_train)

    test_predictions = evaluation_model.predict(X_test)
    mae = mean_absolute_error(y_test, test_predictions)

    # Fit a final model on all available historical observations.
    final_model = RandomForestRegressor(
        n_estimators=250,
        max_depth=8,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    final_model.fit(X, y)

    # Generate future predictions recursively.
    history = list(series.astype(float).values)
    last_date = series.index[-1]
    forecast = []

    for step in range(1, forecast_days + 1):
        future_date = last_date + pd.Timedelta(days=step)

        row = pd.DataFrame([{
            "lag_1": history[-1],
            "lag_7": history[-7],
            "lag_14": history[-14],
            "rolling_mean_7": sum(history[-7:]) / 7,
            "day_of_week": future_date.dayofweek,
            "month": future_date.month,
            "day_of_year": future_date.dayofyear
        }])

        prediction = float(final_model.predict(row[feature_columns])[0])

        # Appointment counts cannot be negative.
        prediction = max(0, prediction)

        forecast.append({
            "date": future_date.strftime("%Y-%m-%d"),
            "predicted_appointments": round(prediction, 1)
        })

        history.append(prediction)

    return {
        "forecast": forecast,
        "evaluation": {
            "method": "Chronological 80/20 holdout",
            "mae": round(float(mae), 2),
            "test_observations": len(y_test)
        }
    }
if __name__ == "__main__":
    results = run_full_analysis()

    print("\n========== CAREPULSE IQ ANALYTICS ==========\n")

    print("BUSINESS OVERVIEW")
    for key, value in results["overview"].items():
        print(f"{key}: {value}")

    print("\nCHANNEL PERFORMANCE")
    print(results["channels"].to_string(index=False))

    print("\nDEPARTMENT DEMAND")
    print(results["departments"].to_string(index=False))

    print("\nWEEKDAY DEMAND")
    print(results["weekday_demand"].to_string(index=False))

    print("\nBUSINESS INSIGHTS")
    for number, insight in enumerate(results["insights"], 1):
        print(f"{number}. {insight}")

    print("\n============================================")
