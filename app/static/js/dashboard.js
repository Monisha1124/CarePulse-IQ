
async function loadDashboard() {
    const insightsList = document.getElementById("insightsList");

    try {
        insightsList.innerHTML =
            '<div class="loading-card">Loading analytics...</div>';

        const channel = document.getElementById("channelFilter").value;
const department = document.getElementById("departmentFilter").value;

const params = new URLSearchParams({
    channel: channel,
    department: department
});

const response = await fetch("/api/dashboard?" + params.toString());

        if (!response.ok) {
            throw new Error("Dashboard API returned an error.");
        }

        const data = await response.json();

        // Performance cards
        document.getElementById("totalAppointments").textContent =
            data.overview.total_appointments.toLocaleString();

        document.getElementById("completedAppointments").textContent =
            data.overview.completed_appointments.toLocaleString();

        document.getElementById("noShowAppointments").textContent =
            data.overview.no_show_appointments.toLocaleString();

        document.getElementById("noShowRate").textContent =
            data.overview.no_show_rate + "%";

        const commonLayout = {
            font: {
                family: "DM Sans, sans-serif",
                color: "#71818c",
                size: 11
            },
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "rgba(0,0,0,0)",
            margin: { t: 15, r: 15, b: 45, l: 45 },
            autosize: true
        };

        const config = {
            responsive: true,
            displayModeBar: false
        };

        // Channel performance chart
        Plotly.newPlot("channelChart", [
            {
                x: data.channels.map(item => item.channel),
                y: data.channels.map(item => item.total_appointments),
                type: "bar",
                name: "Appointments",
                marker: {
                    color: "#138b88",
                    borderRadius: 5
                },
                hovertemplate: "%{x}<br>Appointments: %{y}<extra></extra>"
            },
            {
                x: data.channels.map(item => item.channel),
                y: data.channels.map(item => item.no_show_rate),
                type: "scatter",
                mode: "lines+markers",
                name: "No-show rate (%)",
                yaxis: "y2",
                line: { color: "#e69a53", width: 3 },
                hovertemplate: "%{x}<br>No-show rate: %{y}%<extra></extra>"
            }
        ], {
            ...commonLayout,
            legend: { orientation: "h", y: -0.25 },
            xaxis: { gridcolor: "transparent" },
            yaxis: { title: "Appointments", gridcolor: "#edf1f3" },
            yaxis2: {
                title: "No-show %",
                overlaying: "y",
                side: "right",
                showgrid: false,
                rangemode: "tozero"
            }
        }, config);

        // Department demand chart
        Plotly.newPlot("departmentChart", [{
            labels: data.departments.map(item => item.department),
            values: data.departments.map(item => item.appointments),
            type: "pie",
            hole: 0.58,
            textinfo: "percent",
            hovertemplate: "%{label}<br>Appointments: %{value}<extra></extra>",
            marker: {
                colors: [
                    "#087f80", "#42aaa0", "#7bc6b9",
                    "#f0b66c", "#8a83bd", "#a8bac7"
                ]
            }
        }], {
            ...commonLayout,
            showlegend: true,
            legend: { orientation: "h", y: -0.15 },
            margin: { t: 5, r: 5, b: 65, l: 5 }
        }, config);

        // Daily demand chart
        Plotly.newPlot("dailyChart", [{
            x: data.daily_demand.map(item => item.date),
            y: data.daily_demand.map(item => item.appointments),
            type: "scatter",
            mode: "lines",
            fill: "tozeroy",
            line: { color: "#078d89", width: 2.5 },
            fillcolor: "rgba(8,127,128,0.10)",
            hovertemplate: "%{x}<br>Appointments: %{y}<extra></extra>"
        }], {
            ...commonLayout,
            xaxis: { title: "Appointment date", gridcolor: "transparent" },
            yaxis: { title: "Appointments", gridcolor: "#edf1f3" }
        }, config);

        // Weekday demand chart
        Plotly.newPlot("weekdayChart", [{
            x: data.weekday_demand.map(item => item.day_of_week),
            y: data.weekday_demand.map(item => item.appointments),
            type: "bar",
            marker: { color: "#268f91" },
            hovertemplate: "%{x}<br>Appointments: %{y}<extra></extra>"
        }], {
            ...commonLayout,
            xaxis: { gridcolor: "transparent" },
            yaxis: { title: "Appointments", gridcolor: "#edf1f3" }
        }, config);

        // Automatically generated insights
        insightsList.innerHTML = "";

        data.insights.forEach((insight, index) => {
            const card = document.createElement("article");
            card.className = "insight-card";

            const number = document.createElement("div");
            number.className = "insight-number";
            number.textContent = `INSIGHT 0${index + 1}`;

            const paragraph = document.createElement("p");
            paragraph.textContent = insight;

            card.appendChild(number);
            card.appendChild(paragraph);
            insightsList.appendChild(card);
        });
        await loadCapacity();

    } catch (error) {
        console.error("Dashboard error:", error);

        insightsList.innerHTML =
            '<div class="loading-card">Unable to load dashboard. Check the Flask terminal and try refreshing.</div>';
    }
}
async function loadFilterOptions() {
    try {
        const response = await fetch("/api/filters");

        if (!response.ok) {
            throw new Error("Unable to load filter options.");
        }

        const data = await response.json();

        const channelSelect = document.getElementById("channelFilter");
        const departmentSelect = document.getElementById("departmentFilter");

        data.channels.forEach(channel => {
            const option = document.createElement("option");
            option.value = channel;
            option.textContent = channel;
            channelSelect.appendChild(option);
        });

        data.departments.forEach(department => {
            const option = document.createElement("option");
            option.value = department;
            option.textContent = department;
            departmentSelect.appendChild(option);
        });

        await loadDashboard();

    } catch (error) {
        console.error("Filter loading error:", error);
    }
}

function resetFilters() {
    document.getElementById("channelFilter").value = "All";
    document.getElementById("departmentFilter").value = "All";

    loadDashboard();
}

document.addEventListener("DOMContentLoaded", loadFilterOptions);
async function loadForecast() {
    const chart = document.getElementById("forecastChart");

    try {
        chart.innerHTML = "Calculating demand forecast...";

        const response = await fetch("/api/forecast");

        if (!response.ok) {
            throw new Error("Forecast API failed.");
        }

        const result = await response.json();

        document.getElementById("forecastMAE").textContent =
            result.evaluation.mae + " appointments";

        const dates = result.forecast.map(
            item => item.date
        );

        const predictions = result.forecast.map(
            item => item.predicted_appointments
        );

        Plotly.newPlot("forecastChart", [{
            x: dates,
            y: predictions,
            type: "scatter",
            mode: "lines+markers",
            name: "Predicted demand",
            line: {
                color: "#087f80",
                width: 3
            },
            marker: {
                size: 7
            },
            fill: "tozeroy",
            fillcolor: "rgba(8,127,128,0.10)",
            hovertemplate:
                "%{x}<br>Predicted appointments: %{y}<extra></extra>"
        }], {
            font: {
                family: "DM Sans, sans-serif",
                color: "#71818c",
                size: 11
            },
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "rgba(0,0,0,0)",
            margin: {
                t: 20,
                r: 20,
                b: 50,
                l: 45
            },
            xaxis: {
                title: "Forecast date",
                gridcolor: "transparent"
            },
            yaxis: {
                title: "Predicted appointments",
                rangemode: "tozero",
                gridcolor: "#edf1f3"
            }
        }, {
            responsive: true,
            displayModeBar: false
        });

    } catch (error) {
        console.error("Forecast error:", error);
        chart.textContent =
            "Unable to generate forecast. Check the Flask terminal.";
    }
}

document.addEventListener("DOMContentLoaded", loadForecast);

async function loadCapacity() {
    const tableBody = document.getElementById("capacityTableBody");

    try {
        const channel = document.getElementById("channelFilter").value;
        const department = document.getElementById("departmentFilter").value;

        const params = new URLSearchParams({
            channel: channel,
            department: department
        });

        const response = await fetch("/api/capacity?" + params.toString());

        if (!response.ok) {
            throw new Error("Capacity API failed.");
        }

        const data = await response.json();

        document.getElementById("dailyCapacity").textContent =
            data.summary.capacity_per_day;

        document.getElementById("overCapacityDays").textContent =
            data.summary.over_capacity_days;

        document.getElementById("shortageSlots").textContent =
            data.summary.total_shortage_slots;

        const rows = data.daily_capacity;

        Plotly.newPlot("capacityChart", [
            {
                x: rows.map(item => item.date),
                y: rows.map(item => item.demand),
                type: "scatter",
                mode: "lines",
                name: "Appointment demand",
                line: { color: "#087f80", width: 2 }
            },
            {
                x: rows.map(item => item.date),
                y: rows.map(item => item.capacity),
                type: "scatter",
                mode: "lines",
                name: "Daily capacity",
                line: { color: "#e69a53", width: 2, dash: "dash" }
            }
        ], {
            font: { family: "DM Sans, sans-serif", color: "#71818c" },
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "rgba(0,0,0,0)",
            margin: { t: 15, r: 15, b: 50, l: 45 },
            xaxis: { title: "Date", gridcolor: "transparent" },
            yaxis: { title: "Appointments", rangemode: "tozero",
                     gridcolor: "#edf1f3" },
            legend: { orientation: "h", y: -0.25 }
        }, {
            responsive: true,
            displayModeBar: false
        });

        const alertRows = rows.filter(
            item => item.status !== "WITHIN CAPACITY"
        );

        if (alertRows.length === 0) {
            tableBody.innerHTML =
                '<tr><td colspan="5">No capacity warnings in this dataset.</td></tr>';
        } else {
            tableBody.innerHTML = "";

            alertRows.forEach(item => {
                const row = document.createElement("tr");

                const statusClass =
                    item.status === "OVER CAPACITY" ? "over" : "near";

                row.innerHTML = `
                    <td>${item.date}</td>
                    <td>${item.demand}</td>
                    <td>${item.capacity}</td>
                    <td>${item.shortage}</td>
                    <td><span class="capacity-status ${statusClass}">
                        ${item.status}
                    </span></td>
                `;

                tableBody.appendChild(row);
            });
        }

    } catch (error) {
        console.error("Capacity analysis error:", error);
        tableBody.innerHTML =
            '<tr><td colspan="5">Unable to load capacity analysis.</td></tr>';
    }
}

function exportReports() {
    const channel = document.getElementById("channelFilter").value;
    const department = document.getElementById("departmentFilter").value;

    const params = new URLSearchParams({
        channel: channel,
        department: department
    });

    window.location.href = "/api/export?" + params.toString();
}
