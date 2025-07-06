import subprocess

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip() or result.stderr.strip() or "✅ Command executed."
    except Exception as e:
        return f"❌ Error: {e}"

def handle_device_command(user_input):
    user_input = user_input.lower()

    if "restart device" in user_input:
        return {
            "output": [run_command("sudo shutdown -r now")],
            "summary": "🔄 Device is restarting..."
        }

    elif "fix sound" in user_input or "no sound" in user_input:
        return {
            "output": ["🎧 Please ensure your output device is selected correctly. Try restarting core audio with: `sudo killall coreaudiod`"],
            "summary": "🛠 Sound troubleshooting step suggested."
        }

    elif "webcam" in user_input:
        return {
            "output": ["📷 Ensure the camera is not being used by another app. Try rebooting if issue persists."],
            "summary": "🛠 Webcam troubleshooting suggestion."
        }

    elif "bluetooth" in user_input:
        return {
            "output": [run_command("sudo pkill bluetoothd")],
            "summary": "🔄 Bluetooth service restarted."
        }

    return None
