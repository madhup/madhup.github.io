"""
Storage Forage
"""

from datetime import datetime

import pandas as pd
import gradio as gr
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def provider_s3_standard_useast(total_data, live_data, file_size):
    cost = 0
    if total_data <= 50 * 1024:
        cost += total_data * 0.023
    else:
        cost += 50 * 1024 * 0.023
        remaining_data = total_data - (50 * 1024)
        if remaining_data <= 450 * 1024:
            cost += remaining_data * 0.022
        else:
            cost += (450 * 1024 * 0.023) + ((remaining_data - (450 * 1024)) * 0.021)
    return cost, "S3 Standard - US East (USD)"


def provider_s3_intelligentTiering_useast(total_data, live_data, file_size):
    cost_hot, _ = provider_s3_standard_useast(live_data, 0, 0)
    cost_cold = (total_data - live_data) * 0.0125
    monitoring_cost = (
        0
        if file_size < 0.125
        else ((((total_data * 1024) / file_size) / 1000) * 0.0025)
    )

    return (
        cost_hot + cost_cold + monitoring_cost
    ), "S3 Intelligent Tiering - US East (USD)"


def provider_gcs_standard_useast(total_data, live_data, file_size):
    return (total_data * 0.020), "GCS Standard - US East (USD)"


def provider_gcs_autoclass_useast(total_data, live_data, file_size):
    cost_hot, _ = provider_gcs_standard_useast(live_data, 0, 0)
    cost_cold = (total_data - live_data) * 0.0012
    monitoring_cost = (
        0
        if file_size < 0.125
        else ((((total_data * 1024) / file_size) / 1000) * 0.0025)
    )
    return (cost_hot + cost_cold + monitoring_cost), "GCS Autoclass - US East (USD)"


def provider_googleOne(total_data, live_data, file_size):
    cost = 0
    plan = []
    account = 1
    remaining_data = total_data
    while remaining_data:
        local_cost = 0
        local_plan = "Free"
        if 15 < remaining_data <= 100:
            local_cost = 19.99 / 12
            local_plan = "Basic (100GB)"
        elif remaining_data <= 200:
            local_cost = 29.99 / 12
            local_plan = "Standard (200GB)"
        elif remaining_data <= (2 * 1024):
            local_cost = 99.99 / 12
            local_plan = "Premium (2TB)"
        elif remaining_data <= (5 * 1024):
            local_cost = 249.99 / 12
            local_plan = "Premium (5TB)"
        elif remaining_data <= (10 * 1024):
            local_cost = 49.99
            local_plan = "Premium (10TB)"
        elif remaining_data <= (20 * 1024):
            local_cost = 99.99
            local_plan = "Premium (20TB)"
        else:
            local_cost = 149.99
            local_plan = "Premium (30TB)"

        remaining_data = max(0, remaining_data - (30 * 1024))
        plan.append(f"Subscription {account} - {local_plan}")
        cost += local_cost
        account += 1

    return cost, f"Google One [{' + '.join(plan)}] (USD)"


def provider_oneDrive(total_data, live_data, file_size):
    cost = 0
    plan = []
    account = 1
    remaining_data = total_data
    while remaining_data:
        local_cost = 0
        local_plan = "365 Free (5GB)"
        if 5 < remaining_data <= 100:
            local_cost = 1.67
            local_plan = "365 Basic (100GB)"
        elif remaining_data <= 1024:
            local_cost = 5
            local_plan = "OneDrive For Business (1TB)"
        else:
            local_cost = 8.33
            local_plan = "365 Family (6TB)"

        remaining_data = max(0, remaining_data - (6 * 1024))
        plan.append(f"Subscription {account} - {local_plan}")
        cost += local_cost
        account += 1

    return cost, f"Microsoft [{' + '.join(plan)}] (USD)"


providers = {
    "S3 Standard (US East)": provider_s3_standard_useast,
    "S3 Intelligent Tiering (US East)": provider_s3_intelligentTiering_useast,
    "GCS Standard (US East)": provider_gcs_standard_useast,
    "GCS AutoClass (US East)": provider_gcs_autoclass_useast,
    "Google One (US)": provider_googleOne,
    "One Drive (US)": provider_oneDrive,
}


def plot(current_vol, annual_vol, term, inflation, live_data_ptg, file_size):
    """
    Generates the data plots
    """
    current_year = datetime.now().year + 1
    prev_vol = current_vol
    trend = []
    for i in range(term):
        delta = (annual_vol * ((1 + (inflation / 100)) ** i)) / 12
        for m in range(12):
            prev_vol += delta
            active_data = prev_vol * (live_data_ptg / 1200)
            base_data = {
                "date": f"{str(current_year + i)}-{(m+1):02}-01",
                "full_data": prev_vol,
                "live_data": active_data,
            }
            for provider_func in providers.values():
                cost, plan = provider_func(prev_vol, active_data, file_size)
                base_data[provider_func.__name__ + "_cost"] = cost
                base_data[provider_func.__name__ + "_plan"] = plan
            trend.append(base_data)

    df = pd.DataFrame(trend)
    lifetime_df = {}

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["full_data"],
            hovertemplate=(
                "Month: %{x} | Data (GB): %{y:.2f} | Hot Data (GB): %{text:.4f}"
            ),
            text=df["live_data"],
            name="Data",
        ),
        secondary_y=False,
    )

    for provider_name, provider_func in providers.items():
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df[provider_func.__name__ + "_cost"],
                hovertemplate=("Month: %{x}<br> | Cost: $%{y:.2f}<br> | Plan: %{text}"),
                text=df[provider_func.__name__ + "_plan"],
                name=provider_name,
            ),
            secondary_y=True,
        )
        lifetime_df[provider_name] = sum(df[provider_func.__name__ + "_cost"])

    fig.update_layout(
        title_text="Storage Forage",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_dark",
    )

    fig.update_xaxes(title_text="Month")

    fig.update_yaxes(title_text="Data (GB)", secondary_y=False)
    fig.update_yaxes(title_text="Cost (Monthly)", secondary_y=True)

    return fig, pd.DataFrame([lifetime_df])


demo = gr.Blocks()

with demo:
    gr.Markdown(
        r"# Where should you store your data to minimize cost and (more importantly) effort?"
    )

    with gr.Row():
        with gr.Column():
            current_vol_txt = gr.Number(
                label="How much data do you currently have? (GB)",
                value=50,
                precision=0,
                minimum=0,
                maximum=1048576,
                container=True,
            )
        with gr.Column():
            annual_vol_txt = gr.Number(
                label="How much data do you generate annually? (GB)",
                value=10,
                precision=0,
                minimum=0,
                maximum=1048576,
                container=True,
            )
        with gr.Column():
            avg_file_size_txt = gr.Number(
                label="Average File Size (MB)",
                value=5,
                minimum=0,
                maximum=1048576,
                container=True,
            )

    with gr.Row():
        with gr.Column():
            inflation_rate_txt = gr.Slider(
                label="Annual size inflation (%)",
                step=1,
                value=1,
                minimum=0,
                maximum=100,
                container=True,
            )
        with gr.Column():
            term_txt = gr.Slider(
                label="Years to plan for",
                step=1,
                value=50,
                minimum=0,
                maximum=100,
            )
        with gr.Column():
            live_data_ptg_txt = gr.Slider(
                label="Frequently Accessed (Hot) Data (Annual %)",
                step=1,
                value=1,
                minimum=0,
                maximum=100,
            )
    with gr.Row():
        run_btn = gr.Button(value="Run")

    output_plt = gr.Plot()
    lifetime_df = gr.Dataframe(label="Lifetime Cost")
    run_btn.click(  # pylint: disable=no-member
        plot,
        [
            current_vol_txt,
            annual_vol_txt,
            term_txt,
            inflation_rate_txt,
            live_data_ptg_txt,
            avg_file_size_txt,
        ],
        [output_plt, lifetime_df],
    )

demo.launch()
