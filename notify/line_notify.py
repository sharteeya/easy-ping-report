"""
Send message to LINE notify.
"""
import configparser
import requests

TOKEN_FILE_PATH = "./token.ini"

def message_formater(data: dict):
    """
    Format data to message.
    """
    message = (
        f"Ping test of {data.get('ip')} has ended with "
        f"{data.get('average_ping')}ms average ping and {data.get('lpercentage')}% packet loss. "
        f"Check the html report for more details."
    )
    return message

def send_message(message: str):
    """
    Send message via LINE notify API.
    """
    config = configparser.ConfigParser()
    config.read(TOKEN_FILE_PATH)
    if "LINE_NOTIFY" not in config:
        print("Can not find LINE notify token setting. Skipped.")
        return

    token = config["LINE_NOTIFY"].get("token")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Bearer {token}",
    }
    params = { "message": message }
    try:
        req = requests.post(
            "https://notify-api.line.me/api/notify",
            headers=headers,
            params=params,
            timeout=30,
        )
    except TimeoutError:
        print("Request timeout. Skipped.")
    except Exception:
        print("Unknown error. Skipped.")

    if req.status_code != 200:
        print(f"Error with status code {str(req.status_code)}.")
    else:
        print("Message sent to LINE notify.")

if __name__ == "__main__":
    pass
