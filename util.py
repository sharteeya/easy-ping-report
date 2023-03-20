"""
Utility for other program
"""
import re
import os
import socket

def parse_duration(duration: str):
    """
    Parse duration string and return the total seconds.
    """
    if len(duration) == 0:
        return 0

    seconds = 0
    day = re.search(string=duration, pattern=r"(\d*)[dD]")
    hour = re.search(string=duration, pattern=r"(\d*)[hH]")
    minute = re.search(string=duration, pattern=r"(\d*)[mM]")
    sec = re.search(string=duration, pattern=r"(\d*)[sS]")
    if day is not None:
        seconds += int(day.group(1)) * 86400
    if hour is not None:
        seconds += int(hour.group(1)) * 3600
    if minute is not None:
        seconds += int(minute.group(1)) * 60
    if sec is not None:
        seconds += int(sec.group(1))

    return seconds

def get_log_name(log_path: str, log_name: str):
    """
    Generate log name and prevent dupe name.
    """
    log_dir = os.listdir(log_path)
    if log_name in log_dir:
        log_idx = 2
        while f"{log_name}_{log_idx}" in log_dir:
            log_idx += 1

        return f"{log_name}_{log_idx}", f"{log_path}/{log_name}_{log_idx}"

    return log_name, f"{log_path}/{log_name}"

def get_local_ip(req_server: str="8.8.8.8"):
    """
    Obtain local IP by send a request.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((req_server, 80))
        sock.close()
        return sock.getsockname()[0]
    except Exception as err:
        print(f"Can not obtain local ip due to connect fail. {err}")
        return ""

if __name__ == "__main__":
    pass
