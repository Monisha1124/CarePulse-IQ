
import csv
import random
import os
from datetime import datetime, timedelta

random.seed(42)

OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "appointments.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

channels = ["Website", "Mobile App", "Phone", "Walk-in", "WhatsApp"]
departments = [
    "General Medicine",
    "Dental",
    "Cardiology",
    "Dermatology",
    "Pediatrics",
    "Orthopedics"
]

days = ["Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"]

records = []
start_date = datetime(2025, 1, 1)

for i in range(1500):
    appointment_date = start_date + timedelta(days=random.randint(0, 600))
    booking_date = appointment_date - timedelta(
        days=random.randint(0, 30)
    )

    channel = random.choice(channels)
    department = random.choice(departments)
    age = random.randint(1, 85)

    # Simulate realistic no-show patterns
    no_show_probability = 0.15

    if channel == "Phone":
        no_show_probability += 0.08
    if channel == "Walk-in":
        no_show_probability -= 0.07
    if (appointment_date - booking_date).days > 14:
        no_show_probability += 0.15
    if appointment_date.strftime("%A") == "Monday":
        no_show_probability += 0.05

    no_show_probability = max(
        0.02, min(no_show_probability, 0.80)
    )

    status = (
        "NO_SHOW"
        if random.random() < no_show_probability
        else "COMPLETED"
    )

    records.append({
        "appointment_id": f"APT{i + 1:05d}",
        "booking_date": booking_date.strftime("%Y-%m-%d"),
        "appointment_date": appointment_date.strftime("%Y-%m-%d"),
        "day_of_week": appointment_date.strftime("%A"),
        "channel": channel,
        "department": department,
        "patient_age": age,
        "days_in_advance": (appointment_date - booking_date).days,
        "status": status
    })

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)

print("CarePulse IQ dataset generated successfully!")
print(f"Total records: {len(records)}")
print(f"Saved to: {OUTPUT_FILE}")
