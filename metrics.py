"""
HeatGuard AI - CPU Scheduling Metrics

Calculates:
1. Completion Time (CT)
2. Turnaround Time (TAT)
3. Waiting Time (WT)
4. Response Time (RT)
5. Average performance metrics
"""

import pandas as pd

def calculate_metrics(results):
    """
    Calculate scheduling metrics for every process.

    Each result must contain:
    arrival_time, burst_time, start_time,
    completion_time, response_time
    """

    calculated = []

    for process in results:
        arrival = process["arrival_time"]
        burst = process["burst_time"]
        start = process["start_time"]
        completion = process["completion_time"]

        # Turnaround Time = Completion Time - Arrival Time
        turnaround = completion - arrival

        # Waiting Time = Turnaround Time - Burst Time
        waiting = turnaround - burst

        # Response Time = First CPU Start - Arrival Time
        response = start - arrival

        calculated.append({
            **process,
            "turnaround_time": turnaround,
            "waiting_time": waiting,
            "response_time": response
        })

    return calculated

def get_average_metrics(results):
    """
    Calculate average waiting, turnaround,
    and response times.

    Returns zero averages if the list is empty.
    """

    if not results:
        return {
            "avg_waiting_time": 0,
            "avg_turnaround_time": 0,
            "avg_response_time": 0
        }

    total = len(results)

    avg_waiting = sum(
        p["waiting_time"] for p in results
    ) / total

    avg_turnaround = sum(
        p["turnaround_time"] for p in results
    ) / total

    avg_response = sum(
        p["response_time"] for p in results
    ) / total

    return {
        "avg_waiting_time": round(avg_waiting, 2),
        "avg_turnaround_time": round(avg_turnaround, 2),
        "avg_response_time": round(avg_response, 2)
    }

def create_metrics_dataframe(results):
    """
    Convert calculated metrics into a pandas DataFrame
    for display in the Streamlit dashboard.
    """

    columns = [
        "process_id",
        "region",
        "severity",
        "priority",
        "arrival_time",
        "burst_time",
        "start_time",
        "completion_time",
        "turnaround_time",
        "waiting_time",
        "response_time"
    ]

    df = pd.DataFrame(results)

    available_columns = [
        column for column in columns
        if column in df.columns
    ]

    return df[available_columns]