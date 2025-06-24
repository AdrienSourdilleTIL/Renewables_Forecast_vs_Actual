import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.dates import DateFormatter
import numpy as np

def load_and_merge_cdm_files(cdm_dir):
    csv_files = list(cdm_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError("No CDM CSV files found.")

    df_list = []
    for f in csv_files:
        df = pd.read_csv(f, parse_dates=["start_date"])
        if not {"start_date", "production_type", "forecast_value", "actual_value"}.issubset(df.columns):
            print(f"⚠️ Skipping {f.name}: missing required columns.")
            continue
        df_list.append(df)

    combined_df = pd.concat(df_list, ignore_index=True)
    combined_df.sort_values("start_date", inplace=True)
    combined_df = combined_df.drop_duplicates(subset=["start_date", "production_type"], keep="last")

    return combined_df

def plot_forecast_vs_actual(df, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)

    latest_date = df["start_date"].dt.date.max().strftime("%Y-%m-%d")
    time_format = DateFormatter('%I %p')  # Format as hour + AM/PM

    for prod_type in df["production_type"].unique():
        subset = df[df["production_type"] == prod_type].sort_values("start_date")
        plt.figure(figsize=(12, 6))
        plt.plot(subset["start_date"], subset["forecast_value"], label="Forecast", linestyle="--")
        plt.plot(subset["start_date"], subset["actual_value"], label="Actual", linestyle="-")
        plt.title(f"{prod_type} Forecast vs Actual ({latest_date})")
        plt.xlabel("Time")
        plt.ylabel("MW")
        plt.gca().xaxis.set_major_formatter(time_format)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        file_path = output_dir / f"{prod_type.lower()}_forecast_vs_actual.png"
        plt.savefig(file_path)
        plt.close()

def plot_total_renewables(df, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)

    # Aggregate forecast and actual values while keeping NaN where all values are missing
    grouped = df.groupby("start_date").agg({
    "forecast_value": lambda x: x.sum() if x.notna().any() else np.nan,
    "actual_value":   lambda x: x.sum() if x.notna().any() else np.nan,
    }).reset_index()

    grouped = grouped.sort_values("start_date")
    latest_date = grouped["start_date"].dt.date.max().strftime("%Y-%m-%d")
    time_format = DateFormatter('%I %p')

    plt.figure(figsize=(12, 6))
    plt.plot(grouped["start_date"], grouped["forecast_value"], label="Total Forecast", linestyle="--")
    plt.plot(grouped["start_date"], grouped["actual_value"], label="Total Actual", linestyle="-")
    plt.title(f"Total Renewables Forecast vs Actual ({latest_date})")
    plt.xlabel("Time")
    plt.ylabel("MW")
    plt.gca().xaxis.set_major_formatter(time_format)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    file_path = output_dir / "total_renewables_forecast_vs_actual.png"
    plt.savefig(file_path)
    plt.close()

def plot_forecast_error_over_time(df, chart_dir):
    chart_dir.mkdir(parents=True, exist_ok=True)

    df = df.copy()
    df["pct_error"] = ((df["forecast_value"] - df["actual_value"]) / df["actual_value"].replace(0, pd.NA)) * 100
    df["mw_delta"] = df["forecast_value"] - df["actual_value"]
    df["hour"] = df["start_date"].dt.hour

    grouped = df.groupby("hour").agg({
        "pct_error": "mean",
        "mw_delta": "mean"
    }).reset_index()

    unique_dates = df["start_date"].dt.date.unique()
    date_str = unique_dates[0].strftime("%Y-%m-%d") if len(unique_dates) == 1 else "Multiple Dates"

    plt.figure(figsize=(14, 7))
    colors = ["green" if x < 0 else "red" for x in grouped["pct_error"]]
    bars = plt.bar(grouped["hour"], grouped["pct_error"], color=colors)
    plt.title(f"Average Forecast % Error Over Time on {date_str}")
    plt.xlabel("Hour of Day")
    plt.ylabel("Average % Error")
    plt.xticks(range(0, 24), [f"{h}h" for h in range(24)])
    plt.grid(axis="y")

    for idx, row in grouped.iterrows():
        plt.text(row["hour"], row["pct_error"], f"{row['mw_delta']:.0f} MW",
                 ha="center",
                 va="bottom" if row["pct_error"] >= 0 else "top",
                 fontsize=9,
                 color="black")

    # Add legend manually
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='red', label='Actual < Forecast (Underproduce)'),
        Patch(facecolor='green', label='Actual > Forecast (Overproduce)')
    ]
    plt.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()
    file_path = chart_dir / "forecast_error_over_time.png"
    plt.savefig(file_path)
    plt.close()

if __name__ == "__main__":
    base_path = Path(__file__).resolve().parent.parent
    cdm_dir = base_path / "data" / "CDM"
    chart_dir = base_path / "charts"

    df = load_and_merge_cdm_files(cdm_dir)
    plot_forecast_vs_actual(df, chart_dir)
    plot_total_renewables(df, chart_dir)
    plot_forecast_error_over_time(df, chart_dir)
