"""
Parse ping log.
"""
import argparse
import time
import csv
import re
import os
import numpy as np
import matplotlib.pyplot as plt
from gen_html import render_template

def print_path(start_time, ip):
    """
    Print save path.
    """
    print(f"""\033[1;33m
         ________________________________________________________________________
        |                                                                        |
        |    REPORT SAVED IN FOLDER ./reports/{ip}/{start_time} <<
        |________________________________________________________________________|\033[1;37m\n"""
    )

def parse_log(log_path):
    """
    Parse ping log to get data.
    """
    timestamps = []
    pings = []
    loss_packet = []
    loss_group = []
    cur_group = []
    response = 0
    loss = 0
    highest = 0
    with open(log_path, "r", encoding="UTF-8") as log:
        for line in log:
            try:
                line = line.lower()
                if "start ping" in line:
                    pass
                elif "program terminated" in line:
                    break
                elif "no response" in line:
                    timestamp = re.search(string=line, pattern=r"\[(.*),\d*\]").group(1)
                    ping = None
                    timestamps.append(timestamp)
                    pings.append(ping)
                    loss += 1
                    loss_packet.append(timestamp)
                    if len(cur_group) == 0:
                        cur_group = [timestamp, 1]
                    else:
                        cur_group[1] += 1
                else:
                    timestamp = re.search(string=line, pattern=r"\[(.*),\d*\]").group(1)
                    ping = re.search(string=line, pattern=r"(\d+\.\d+) ms").group(1)
                    highest = max(float(ping), highest)
                    timestamps.append(timestamp)
                    pings.append(ping)
                    response += 1
                    if len(cur_group) > 0:
                        loss_group.append(cur_group)
                        cur_group = []

            except AttributeError as err:
                print(f"Error on parse line. Skipped line: {err}.")

        if len(cur_group) > 0:
            loss_group.append(cur_group)

    return {
        "timestamps": timestamps,
        "pings": pings,
        "response": response,
        "loss": loss,
        "loss_group": loss_group,
        "highest_ping": round(highest, 3),
        "average_ping": round(np.nanmean(np.array(pings, dtype=float)), 3),
        "loss_packet": loss_packet,
    }

def draw_fig(timestamps: dict, pings: dict, ip: str,
             figsize: tuple=(16, 5), y_default_high: int=50):
    """
    Draw image of pings by matplotlib.
    """
    try:
        pin = np.array(pings, dtype=float)
        fig = plt.figure(figsize=figsize)
        axe = fig.add_subplot()
        axe.plot(timestamps, pin)
        axe.xaxis.set_ticks([timestamps[0], timestamps[-1]])
        axe.yaxis.set_ticks([0, np.nanmean(pin), max(np.nanmax(pin), y_default_high)])
        axe.set_xlabel("Time")
        axe.set_ylabel("Ping (ms)")

        fig.savefig(f"./reports/{ip}/{timestamps[0]}/ping_overview.png", bbox_inches="tight")
    except ValueError as err:
        print(f"Can not generate image. {err}")

def export_csv(timestamps: dict, pings: dict, ip: str):
    """
    Export csv file of timestamps and pings.
    """
    with open(f"./reports/{ip}/{timestamps[0]}/ping.csv", "w", newline="", encoding="UTF-8") as out:
        writer = csv.writer(out)
        writer.writerow(["timestamp", "ping"])
        for timestamp, ping in zip(timestamps, pings):
            writer.writerow([timestamp, ping])

def export_report(log_name: str, log_path: str="./logs",
                  exp_csv: bool=True, notify: str=""):
    """
    Generate html and export to folder.
    """
    ip = re.search(string=log_path, pattern=r".*/(\d+\.\d+\.\d+\.\d+)").group(1)
    parsed_log = parse_log(log_path=f"{log_path}/{log_name}")
    timestamps = parsed_log["timestamps"]
    pings = parsed_log["pings"]
    os.makedirs("./reports", exist_ok=True)
    os.makedirs(f"./reports/{ip}", exist_ok=True)
    os.makedirs(f"./reports/{ip}/{timestamps[0]}", exist_ok=True)

    html = render_template(data={
         "ip": ip,
         "start_time": timestamps[0],
         "end_time": timestamps[-1],
         "log_path": log_path,
         "loss": parsed_log.get("loss"),
         "loss_group": parsed_log.get("loss_group"),
         "highest_ping": parsed_log.get("highest_ping"),
         "average_ping": parsed_log.get("average_ping"),
         "lpercentage": round(parsed_log.get("loss") / len(pings) * 100, 3),
         "loss_packet": parsed_log.get("loss_packet"),
         "response": parsed_log.get("response"),
         "gen_time": time.strftime("%Y/%m/%d %H:%M:%S")
    })

    with open(f"./reports/{ip}/{timestamps[0]}/report.html", "w", encoding="UTF-8") as export_html:
        export_html.write(html)

    if exp_csv:
        export_csv(timestamps=timestamps, pings=pings, ip=ip)

    if notify == "line_notify":
        # pylint: disable-next=import-outside-toplevel
        from notify import line_notify
        message = line_notify.message_formater(data={
            "ip": ip,
            "average_ping": parsed_log.get("average_ping"),
            "lpercentage": round(parsed_log.get("loss") / len(pings) * 100, 3),
        })
        line_notify.send_message(message=message)

    draw_fig(timestamps=timestamps, pings=pings, ip=ip)
    print_path(start_time=timestamps[0], ip=ip)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--logname", help="Target log name", type=str)
    parser.add_argument("-p", "--logpath", help="Position of log storage",
                        type=str, default="./logs")
    args = parser.parse_args()
    export_report(log_name=args.logname, log_path=args.logpath)
