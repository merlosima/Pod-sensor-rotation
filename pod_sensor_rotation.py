# %%
import gradio as gr
from datetime import date, timedelta
import random

# Constants
sensor_sequence = [
    {"site": "Right Stomach", "side": "right"},
    {"site": "Left Stomach", "side": "left"},
    {"site": "Right Stomach", "side": "right"},
    {"site": "Left Stomach", "side": "left"},
    {"site": "Right Arm", "side": "right"},
    {"site": "Left Arm", "side": "left"},
    {"site": "Right Arm", "side": "right"},
    {"site": "Left Arm", "side": "left"},
    {"site": "Right Leg", "side": "right"},
    {"site": "Left Leg", "side": "left"},
    {"site": "Right Leg", "side": "right"},
    {"site": "Left Leg", "side": "left"},
]

valid_pod_sites = {
    "Left Leg": ["Left Stomach", "Right Stomach", "Left Arm", "Left Leg"],
    "Right Leg": ["Left Stomach", "Right Stomach", "Right Arm", "Right Leg"],
    "Left Stomach": ["Left Leg", "Right Leg", "Left Arm", "Right Arm"],
    "Right Stomach": ["Left Leg", "Right Leg", "Left Arm", "Right Arm"],
    "Left Arm": ["Left Arm", "Left Leg", "Left Stomach"],
    "Right Arm": ["Right Arm", "Right Leg", "Right Stomach"]
}

pod_change_days = 3
sensor_change_days = 10

# Initial values
current_pod_site = {"site": "Right Arm", "side": "right"}
current_sensor_site = {"site": "Right Stomach", "side": "right"}
current_pod_date = date(2025, 5, 31)
current_sensor_date = date(2025, 5, 28)
previous_pod_sites = [current_pod_site["site"]]
sensor_index = 0


def get_next_sensor_site(last_sensor_site, index):
    new_index = (index + 1) % len(sensor_sequence)
    while sensor_sequence[new_index]["site"] == last_sensor_site["site"]:
        new_index = (new_index + 1) % len(sensor_sequence)
    return sensor_sequence[new_index], new_index


def get_next_pod_site(sensor_index):
    next_sensor_site = sensor_sequence[sensor_index]["site"]
    possible_sites = valid_pod_sites[next_sensor_site].copy()

    if "Stomach" in next_sensor_site:
        sensor_side = next_sensor_site.split()[0]
        same_side_stomach = f"{sensor_side} Stomach"
        if same_side_stomach in possible_sites:
            possible_sites.remove(same_side_stomach)

    for site in previous_pod_sites[-2:]:
        if site in possible_sites:
            possible_sites.remove(site)

    if not possible_sites:
        possible_sites = valid_pod_sites[next_sensor_site].copy()

    chosen = random.choice(possible_sites)
    previous_pod_sites.append(chosen)
    if len(previous_pod_sites) > 2:
        previous_pod_sites.pop(0)

    return chosen


def forecast_schedule(pod_date, sensor_date, pod_site, sensor_site, index, weeks=4):
    forecast = []
    today = date.today()
    end = today + timedelta(weeks=weeks)
    next_pod_date = pod_date + timedelta(days=pod_change_days)
    next_sensor_date = sensor_date + timedelta(days=sensor_change_days)
    idx = index
    last_sensor = sensor_site

    while next_pod_date <= end or next_sensor_date <= end:
        if next_pod_date <= end:
            site = get_next_pod_site(idx)
            forecast.append(f"{next_pod_date.strftime('%b %d, %Y')}: Pod Change -> {site}")
            next_pod_date += timedelta(days=pod_change_days)
        if next_sensor_date <= end:
            next_sensor, idx = get_next_sensor_site(last_sensor, idx)
            forecast.append(f"{next_sensor_date.strftime('%b %d, %Y')}: Sensor Change -> {next_sensor['site']}")
            last_sensor = next_sensor
            next_sensor_date += timedelta(days=sensor_change_days)

    return "\n".join(sorted(forecast))


def start_session(sensor_site, pod_site, sensor_date, pod_date):
    global current_sensor_site, current_pod_site, current_sensor_date, current_pod_date, sensor_index
    current_sensor_site = {"site": sensor_site, "side": "left" if "Left" in sensor_site else "right"}
    current_pod_site = {"site": pod_site, "side": "left" if "Left" in pod_site else "right"}
    current_sensor_date = date.fromisoformat(sensor_date)
    current_pod_date = date.fromisoformat(pod_date)
    sensor_index = 0
    return f"Sensor: {sensor_site} (Changed on {sensor_date})\nPod: {pod_site} (Changed on {pod_date})"


def handle_sensor_change():
    global current_sensor_site, current_sensor_date, sensor_index
    suggested, sensor_index = get_next_sensor_site(current_sensor_site, sensor_index)
    current_sensor_site = suggested
    current_sensor_date = date.today()
    return f"Next sensor site: {suggested['site']}"


def handle_pod_change():
    global current_pod_site, current_pod_date
    suggested = get_next_pod_site(sensor_index)
    current_pod_site = {"site": suggested}
    current_pod_date = date.today()
    return f"Next pod site: {suggested}"


def display_forecast():
    return forecast_schedule(current_pod_date, current_sensor_date, current_pod_site, current_sensor_site, sensor_index)


with gr.Blocks() as demo:
    gr.Markdown("# 🩺 Pod & Sensor Rotation Scheduler")
    with gr.Row():
        sensor_input = gr.Textbox(label="Current Sensor Site", value=current_sensor_site["site"])
        pod_input = gr.Textbox(label="Current Pod Site", value=current_pod_site["site"])
    with gr.Row():
        sensor_date_input = gr.Textbox(label="Sensor Change Date (YYYY-MM-DD)", value=str(current_sensor_date))
        pod_date_input = gr.Textbox(label="Pod Change Date (YYYY-MM-DD)", value=str(current_pod_date))
    start_btn = gr.Button("✅ Start Session")
    session_output = gr.Textbox(label="Current Site Info")

    gr.Markdown("## ➡️ Choose Change to Make:")
    with gr.Row():
        sensor_change_btn = gr.Button("🔄 Make Sensor Change")
        pod_change_btn = gr.Button("🔄 Make Pod Change")

    site_change_output = gr.Textbox(label="Next Site Suggestion")
    gr.Markdown("---")

    forecast_btn = gr.Button("📅 Show Upcoming Schedule")
    forecast_output = gr.Textbox(label="4-Week Forecast", lines=10)

    # Events
    start_btn.click(start_session, inputs=[sensor_input, pod_input, sensor_date_input, pod_date_input], outputs=session_output)
    sensor_change_btn.click(handle_sensor_change, outputs=site_change_output)
    pod_change_btn.click(handle_pod_change, outputs=site_change_output)
    forecast_btn.click(display_forecast, outputs=forecast_output)

demo.launch()



