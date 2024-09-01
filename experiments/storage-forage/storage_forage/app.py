"""
Storage Forage
"""

from datetime import datetime

import pandas as pd
import gradio as gr


def plot(current_vol, annual_vol, term, live_data_ptg):
    """
    Generates the data plots
    """
    current_year = datetime.now().year
    prev_vol = current_vol
    trend = []
    for i in range(term):
        prev_vol = prev_vol + (annual_vol * (1.01**i))
        trend.append({"year": str(current_year + i), "data": prev_vol})

    df = pd.DataFrame(trend)
    return df


demo = gr.Blocks()

with demo:
    gr.Markdown(
        r"# Where should you store your data to minimize cost and (more importantly) effort."
    )

    with gr.Row():
        with gr.Column():
            current_vol_txt = gr.Number(
                label="How much data do you currently have? (GBs)",
                value=50,
                precision=0,
                minimum=0,
                maximum=1048576,
                container=True,
            )
        with gr.Column():
            annual_vol_txt = gr.Number(
                label="How much data do you generate annually? (GBs)",
                value=10,
                precision=0,
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
                label="Frequently Accessed (Hot) Data (%)",
                step=1,
                value=1,
                minimum=0,
                maximum=100,
            )
    with gr.Row():
        run_btn = gr.Button(value="Run")

    output_plt = gr.LinePlot(
        x="year",
        y="data",
        x_label_angle=90,
    )
    run_btn.click(  # pylint: disable=no-member
        plot, [current_vol_txt, annual_vol_txt, term_txt, live_data_ptg_txt], output_plt
    )

demo.launch()
