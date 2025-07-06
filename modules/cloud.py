def handle_cloud_command(user_input):
    user_input = user_input.lower()

    if "reset microsoft 365 password" in user_input:
        return {
            "output": ["🔐 Simulated: Resetting Microsoft 365 password..."],
            "summary": "✅ Microsoft 365 password reset simulated."
        }

    elif "resync outlook" in user_input or "sync outlook" in user_input:
        return {
            "output": ["📩 Simulated: Re-syncing Outlook mailbox..."],
            "summary": "✅ Outlook sync simulated."
        }

    elif "refresh sharepoint" in user_input:
        return {
            "output": ["🔄 Simulated: Refreshing SharePoint access..."],
            "summary": "✅ SharePoint access refreshed."
        }

    elif "restore onedrive" in user_input:
        return {
            "output": ["📁 Simulated: Restoring deleted OneDrive files..."],
            "summary": "✅ OneDrive files restored."
        }

    elif "request license" in user_input:
        return {
            "output": ["🗂 Simulated: Requesting new Microsoft 365 license..."],
            "summary": "✅ License request sent."
        }

    elif "blocked sign-in" in user_input or "account disabled" in user_input:
        return {
            "output": ["🚫 Simulated: Detecting blocked sign-in or disabled account..."],
            "summary": "⚠️ Sign-in issue detected."
        }

    return None
