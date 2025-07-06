def handle_ad_command(user_input):
    user_input = user_input.lower()

    if "reset password" in user_input:
        return {
            "output": ["🔐 Simulated: Resetting Active Directory password..."],
            "summary": "✅ AD password reset simulated."
        }

    elif "unlock account" in user_input:
        return {
            "output": ["🧑‍🔓 Simulated: Unlocking user account..."],
            "summary": "✅ AD account unlock simulated."
        }

    elif "create user" in user_input:
        return {
            "output": ["🧑‍💼 Simulated: Creating new Active Directory user..."],
            "summary": "✅ AD user creation simulated."
        }

    elif "disable user" in user_input or "delete user" in user_input:
        return {
            "output": ["🗑 Simulated: Disabling or deleting user account..."],
            "summary": "✅ AD user deletion simulated."
        }

    elif "move user" in user_input:
        return {
            "output": ["📂 Simulated: Moving user to a new group..."],
            "summary": "✅ AD user move simulated."
        }

    elif "user details" in user_input or "lookup user" in user_input:
        return {
            "output": ["🔍 Simulated: Displaying user details (name, role, department)..."],
            "summary": "📋 User lookup completed."
        }

    return None

