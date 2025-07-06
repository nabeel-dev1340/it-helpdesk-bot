import datetime

def handle_qol_command(command):
    cmd = command.lower()

    if "send reminder" in cmd or "remind me" in cmd:
        return {
            "output": ["🔔 Simulated: Reminder has been scheduled and sent to the user."],
            "summary": "✅ Reminder sent successfully."
        }

    elif "schedule restart" in cmd or "restart later" in cmd or "off-hours" in cmd:
        return {
            "output": ["⏰ Simulated: System restart has been scheduled for off-hours."],
            "summary": "✅ Restart scheduled successfully."
        }

    elif "auto close ticket" in cmd or "close after inactivity" in cmd:
        return {
            "output": ["📤 Simulated: Ticket flagged to auto-close after 48 hours of inactivity."],
            "summary": "✅ Ticket auto-close rule applied."
        }

    elif "send resolution summary" in cmd or "email summary" in cmd:
        return {
            "output": ["📧 Simulated: Resolution summary has been generated and emailed to the user."],
            "summary": "✅ Resolution summary sent."
        }

    return None
