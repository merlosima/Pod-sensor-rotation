# %% [markdown]
# Final version for site rotation program - 6/1/25

# %%
from datetime import datetime, timedelta
import random

# Define sensor sequence
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

# Define all pod sites
pod_sites = [
    {"site": "Left Arm", "side": "left"},
    {"site": "Right Arm", "side": "right"},
    {"site": "Left Leg", "side": "left"},
    {"site": "Right Leg", "side": "right"},
    {"site": "Left Stomach", "side": "left"},
    {"site": "Right Stomach", "side": "right"}
]

# Define valid pod placements based on sensor site
valid_pod_sites = {
    "Left Leg": ["Right Leg", "Left Stomach", "Right Stomach", "Left Arm"],
    "Right Leg": ["Left Leg", "Left Stomach", "Right Stomach", "Right Arm"],
    "Left Stomach": ["Left Leg", "Right Leg", "Left Arm"],
    "Right Stomach": ["Left Leg", "Right Leg", "Right Arm"],
    "Left Arm": ["Left Arm", "Left Leg", "Left Stomach", "Right Stomach"],
    "Right Arm": ["Right Arm", "Right Leg", "Left Stomach", "Right Stomach"]
}

def get_next_site(current_index, rotation_list):
    return (current_index + 1) % len(rotation_list)

def prompt_user_for_pod_site(suggested, options):
    print(f"\nSuggested pod site: {suggested['site']} ({suggested['side']})")
    print("Choose an option:")
    print("  1. Accept suggested site")
    print("  2. Choose a different site")
    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            return suggested
        elif choice == "2":
            print("\nAvailable alternative sites:")
            for idx, opt in enumerate(options):
                print(f"{idx + 1}. {opt['site']} ({opt['side']})")
            while True:
                try:
                    selection = int(input("Enter the number of your preferred site: "))
                    if 1 <= selection <= len(options):
                        return options[selection - 1]
                    else:
                        print("Invalid number. Try again.")
                except ValueError:
                    print("Please enter a valid number.")
        else:
            print("Invalid input. Please enter 1 or 2.")

# Initial setup
last_sensor_index = 0
last_pod_date = datetime.strptime("2025-05-31", "%Y-%m-%d")
last_sensor_date = datetime.strptime("2025-05-28", "%Y-%m-%d")

current_sensor_site = {"site": "Right Stomach", "side": "right"}
current_pod_site = {"site": "Right Arm", "side": "right"}
last_pod_site = current_pod_site

print("Initial Sites in Use:")
print(f"Sensor is placed at {current_sensor_site['site']} ({current_sensor_site['side']})")
print(f"Pod is placed at {current_pod_site['site']} ({current_pod_site['side']})\n")

# Track changes
upcoming_changes = []
end_date = datetime.strptime("2025-07-31", "%Y-%m-%d")
first_pod_prompt = True
change_events = []

while last_sensor_date <= end_date or last_pod_date <= end_date:
    # Sensor change
    if last_sensor_date <= end_date:
        next_sensor_date = last_sensor_date + timedelta(days=10)
        if next_sensor_date > end_date:
            break

        next_sensor_index = get_next_site(last_sensor_index, sensor_sequence)
        next_sensor_site = sensor_sequence[next_sensor_index]

        upcoming_changes.append(
            (next_sensor_date, f"Sensor Change at {next_sensor_site['site']} ({next_sensor_site['side']})")
        )
        change_events.append(('sensor', next_sensor_date, next_sensor_site))

        last_sensor_date = next_sensor_date
        last_sensor_index = next_sensor_index

    # Pod change
    if last_pod_date <= end_date:
        next_pod_date = last_pod_date + timedelta(days=3)
        if next_pod_date > end_date:
            break

        allowed_pods = valid_pod_sites[next_sensor_site["site"]]
        possible_pod_sites = [site for site in pod_sites if site["site"] in allowed_pods]
        valid_next_pods = [site for site in possible_pod_sites if site["site"] != last_pod_site["site"]]
        suggested_pod_site = random.choice(valid_next_pods) if valid_next_pods else random.choice(possible_pod_sites)

        if first_pod_prompt:
            next_pod_site = prompt_user_for_pod_site(suggested_pod_site, valid_next_pods or possible_pod_sites)
            first_pod_prompt = False
        else:
            next_pod_site = suggested_pod_site

        upcoming_changes.append(
            (next_pod_date, f"Pod Change at {next_pod_site['site']} ({next_pod_site['side']})")
        )
        change_events.append(('pod', next_pod_date, next_pod_site))

        last_pod_date = next_pod_date
        last_pod_site = next_pod_site

# Sort changes
upcoming_changes.sort(key=lambda x: x[0])
change_events.sort(key=lambda x: x[1])

# Update current sites if today is a change date
today = datetime.today().date()
for change_type, change_date, new_site in change_events:
    if change_date.date() == today:
        if change_type == 'sensor':
            current_sensor_site = new_site
        elif change_type == 'pod':
            current_pod_site = new_site

# Display updated current site
print("\n[Updated Sites for Today]")
print(f"Current Sensor Site: {current_sensor_site['site']} ({current_sensor_site['side']})")
print(f"Current Pod Site: {current_pod_site['site']} ({current_pod_site['side']})")

# Show next changes
future = [evt for evt in change_events if evt[1].date() > today]
if future:
    next_sensor = next((e for e in future if e[0] == 'sensor'), None)
    next_pod = next((e for e in future if e[0] == 'pod'), None)

    print("\n[Next Scheduled Changes]")
    if next_sensor:
        print(f"Next Sensor Change: {next_sensor[1].date()} at {next_sensor[2]['site']} ({next_sensor[2]['side']})")
    if next_pod:
        print(f"Next Pod Change:    {next_pod[1].date()} at {next_pod[2]['site']} ({next_pod[2]['side']})")

# Print full schedule
print("\nFull Upcoming Schedule for June and July 2025:")
for date, change in upcoming_changes:
    print(f"{date.date()} --> {change}")


