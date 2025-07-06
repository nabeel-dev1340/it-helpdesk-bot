import subprocess

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip() or result.stderr.strip() or "✅ Command executed."
    except Exception as e:
        return f"❌ Error: {e}"

def handle_network_command(user_input):
    user_input = user_input.lower()

    if "flush dns" in user_input:
        return {
            "output": [
                run_command("sudo dscacheutil -flushcache"),
                run_command("sudo killall -HUP mDNSResponder")
            ],
            "summary": "🧹 DNS cache flushed."
        }

    elif "check internet" in user_input or "ping" in user_input:
        result = run_command("ping -c 3 8.8.8.8")
        if "0% packet loss" in result:
            return {
                "output": [result],
                "summary": "✅ Internet connection is active."
            }
        elif "100% packet loss" in result:
            return {
                "output": [result],
                "summary": "❌ No internet connection detected."
            }
        else:
            return {
                "output": [result],
                "summary": "⚠️ Partial connectivity. Please investigate further."
            }

    elif "restart network" in user_input or "network adapter" in user_input:
        return {
            "output": [
                run_command("sudo ifconfig en0 down"),
                run_command("sudo ifconfig en0 up")
            ],
            "summary": "🔄 Network adapter restarted."
        }

    elif "reset wifi" in user_input:
        return {
            "output": [
                run_command("networksetup -removepreferredwirelessnetwork en0 'YourNetworkName'")
            ],
            "summary": "📡 Wi-Fi profile removed. Reconnect to network manually."
        }

    return None
