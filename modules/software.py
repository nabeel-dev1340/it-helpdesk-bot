def handle_software_command(command):
    cmd = command.lower()

    if "reinstall teams" in cmd or "reinstall outlook" in cmd or "reinstall zoom" in cmd:
        app_name = cmd.split()[-1].capitalize()
        return {
            "output": [f"📦 Simulated: {app_name} reinstalled successfully."],
            "summary": f"✅ {app_name} has been reinstalled."
        }

    elif "restart app" in cmd or "restart application" in cmd or "app not responding" in cmd:
        return {
            "output": ["⏳ Simulated: Application closed and restarted successfully."],
            "summary": "✅ App restarted after detecting it was unresponsive."
        }

    elif "clear outlook cache" in cmd or "rebuild outlook profile" in cmd:
        return {
            "output": ["📩 Simulated: Outlook cache cleared and profile rebuilt."],
            "summary": "✅ Outlook profile refreshed."
        }

    elif "clear browser cache" in cmd or "clear cookies" in cmd:
        return {
            "output": ["🌐 Simulated: Browser cache, history, and cookies cleared."],
            "summary": "✅ Browser data cleared."
        }

    elif "end background apps" in cmd or "close teams" in cmd or "close zoom" in cmd:
        return {
            "output": ["🛑 Simulated: Background apps like Teams/Zoom have been closed."],
            "summary": "✅ Resource-heavy background apps ended."
        }

    elif "check for software updates" in cmd:
        return {
            "output": ["🆙 Simulated: Checked for updates. All installed software is up to date."],
            "summary": "✅ Software update check complete."
        }

    return None
