import subprocess

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip() or result.stderr.strip() or "✅ Command executed."
    except Exception as e:
        return f"❌ Error: {e}"

def handle_performance_command(user_input):
    user_input = user_input.lower()

    if "clear temp" in user_input or "delete temp" in user_input or "free up space" in user_input:
        return {
            "output": [run_command("rm -rf /tmp/*")],
            "summary": "Temporary files cleared to improve performance."
        }

    elif "disk space" in user_input or "check storage" in user_input:
        return {
            "output": [run_command("df -h")],
            "summary": "Disk usage displayed."
        }

    elif "slow" in user_input or "performance issue" in user_input:
        return {
            "output": ["🧹 Try clearing temp files and checking disk space for a quick performance boost."],
            "summary": "General performance advice provided."
        }

    return None
