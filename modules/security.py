def handle_security_command(command):
    cmd = command.lower()

    if "update antivirus" in cmd or "force antivirus" in cmd:
        return {
            "output": ["🛡 Simulated: Antivirus definitions updated (e.g., Windows Defender, CrowdStrike)."],
            "summary": "✅ Antivirus updated successfully."
        }

    elif "check encryption" in cmd or "bitlocker status" in cmd:
        return {
            "output": ["🔐 Simulated: Encryption status checked. BitLocker is enabled and protecting the drive."],
            "summary": "✅ Encryption status verified."
        }

    elif "turn firewall off" in cmd:
        return {
            "output": ["🧱 Simulated: Firewall disabled. (⚠️ Warning: This is not recommended!)"],
            "summary": "⚠️ Firewall has been turned off."
        }

    elif "turn firewall on" in cmd:
        return {
            "output": ["🧱 Simulated: Firewall enabled."],
            "summary": "✅ Firewall has been turned on."
        }

    elif "scan for malware" in cmd or "malware scan" in cmd:
        return {
            "output": ["🧪 Simulated: Quick malware scan completed. No threats detected."],
            "summary": "✅ Malware scan finished."
        }

    elif "failed login" in cmd or "brute force" in cmd or "suspicious login" in cmd:
        return {
            "output": ["🔍 Simulated: Reviewed system logs. Multiple failed login attempts detected from 192.168.1.55."],
            "summary": "⚠️ Suspicious activity flagged."
        }

    return None
