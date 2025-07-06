def handle_printer_command(command):
    cmd = command.lower()

    if "can't print" in cmd or "printer not working" in cmd or "i can't print" in cmd:
        return {
            "output": ["🖨️ Simulated: Restarted print spooler service."],
            "summary": "✅ Print spooler restarted. Please try printing again."
        }

    elif "clear queue" in cmd or "stuck print queue" in cmd:
        return {
            "output": ["📄 Simulated: Cleared all jobs from the print queue."],
            "summary": "✅ Print queue cleared."
        }

    elif "reinstall printer" in cmd or "install printer" in cmd:
        return {
            "output": ["🖨️ Simulated: Reinstalled default printer driver."],
            "summary": "✅ Printer driver reinstalled."
        }

    elif "auto-detect printer" in cmd or "detect printer" in cmd:
        return {
            "output": ["🔍 Simulated: Auto-detected printers and re-added default one."],
            "summary": "✅ Printer auto-detection complete."
        }

    elif "offline printer" in cmd or "printer offline" in cmd:
        return {
            "output": ["🛠 Simulated: Troubleshot offline printer error and brought printer online."],
            "summary": "✅ Printer back online."
        }

    return None
