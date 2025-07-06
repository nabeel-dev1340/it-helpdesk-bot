import subprocess

def handle_system_command(intent):
    responses = []

    if intent == "clear temp files":
        try:
            result = subprocess.run("rm -rf /tmp/*", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                responses.append("🧹 Temp files cleared successfully.")
            else:
                responses.append(f"⚠️ Failed to clear temp files:\n{result.stderr}")
        except Exception as e:
            responses.append(f"❌ Error: {str(e)}")

    elif intent == "check disk":
        try:
            result = subprocess.run("df -h", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.splitlines()
                responses.append("\n".join(lines[:3]))  # Show just first 3 lines
            else:
                responses.append(f"⚠️ Failed to check disk:\n{result.stderr}")
        except Exception as e:
            responses.append(f"❌ Error: {str(e)}")

    elif intent == "show uptime":
        try:
            result = subprocess.run("uptime", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                responses.append(f"🕒 Uptime: {result.stdout.strip()}")
            else:
                responses.append(f"⚠️ Failed to get uptime:\n{result.stderr}")
        except Exception as e:
            responses.append(f"❌ Error: {str(e)}")

    return responses



