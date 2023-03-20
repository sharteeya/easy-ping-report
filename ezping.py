"""
Ping ip.
"""
import subprocess
import ipaddress
import argparse
import logging
import signal
import time
import sys
import re
import os
from util import parse_duration, get_log_name
from log_parser import export_report

def print_log_path():
    """
    Print save path.
    """
    print(f"""\033[1;33m
         _____________________________________________________
        |                                                     |
        |    LOG SAVED IN {log_name_with_path} <<
        |_____________________________________________________|\033[1;37m\n"""
    )

# pylint: disable-next=unused-argument
def signal_handler(signum, frame):
    """
    Show interrupt message when press Ctrl-C.
    """
    # pylint: disable-next=no-member
    if signum == signal.SIGINT.value:
        print("\n")
        logger.info("Program terminated by keyboard interrupt.")
        sys.exit()

def ping(host: str, pkt_loss: int, pkt_recv: int,
         ping_sum:int, pktsize: int = -1):
    """
    Ping target ip.
    """
    result = subprocess.getoutput(f"ping {host} -c 1 {f'-s {pktsize}' if pktsize != -1 else ''}")
    ping_ms = re.search(string=result, pattern=r"\d. bytes from .*time=(\d*\.\d*) ms")
    if ping_ms is not None:
        pkt_recv += 1
        ping_sum += float(ping_ms.group(1))
        avg_ping = round(ping_sum / pkt_recv, 3)

        logger.info(
            "%s > %s ms. | Packet received: %d, loss: %d | Average: %.3fms",
            host,
            ping_ms.group(1),
            pkt_recv,
            pkt_loss,
            avg_ping,
        )
        return pkt_loss, pkt_recv, ping_sum

    loss = re.search(string=result, pattern=r".*(\d{3})% packet loss.*")
    if loss is not None and loss.group(1) == "100":
        logger.warning("%s has no response.", host)
        pkt_loss += 1
    else:
        logger.critical("Program error on parsing ping response.")

    return pkt_loss, pkt_recv, ping_sum

if __name__ == "__main__":
    if not sys.platform.startswith('linux'):
        print("Unsupport platform. Program terminated.")
        sys.exit()

    parser = argparse.ArgumentParser()
    parser.add_argument("ip", help="Target IP",
                        type=str, default=None)
    parser.add_argument("-i", "--interval", help="Interval between pings. Default=1",
                        type=float, default=1)
    parser.add_argument("-s", "--pktsize", help="Packet size",
                        type=int, default=-1)
    parser.add_argument("-l", "--logpath", help="Log save path. Default=\"./logs\"",
                        type=str, default="./logs")
    parser.add_argument("-d", "--duration", help="Execute time. Format: 1d2h3m4s",
                        type=str, default=None)
    parser.add_argument("-t", "--till", help="Execute till the time. Format: YYYY/MM/DD_hh:mm:ss",
                        type=str, default=None)
    parser.add_argument("-o", "--output", help="Generate html report. Default: True",
                        type=bool, default=True)
    parser.add_argument("-n", "--notify",
                        help="Send brief notify to client. Enable html report is needed",
                        type=str, choices=["", "line_notify"], default="")

    args = parser.parse_args()
    if args.ip is None:
        print("Insufficient argument. Program terminated.")
        sys.exit()

    log_path = f"{args.logpath}/{args.ip}"
    os.makedirs(args.logpath, exist_ok=True)
    os.makedirs(log_path, exist_ok=True)
    log_name, log_name_with_path = get_log_name(
        log_path=log_path, log_name=time.strftime("%Y_%m_%d")
    )

    logger = logging.getLogger(name='ezping')
    logger.setLevel(logging.INFO)
    dev_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(log_name_with_path, "a")
    dev_formatter = logging.Formatter("[%(asctime)s] %(levelname)s | %(name)s > %(message)s")
    dev_handler.setFormatter(dev_formatter)
    file_handler.setFormatter(dev_formatter)
    logger.addHandler(dev_handler)
    logger.addHandler(file_handler)

    try:
        ipaddress.ip_address(args.ip)
        logger.info("%s is a valid IP. Start ping.", args.ip)
        print_log_path()
    except ValueError:
        logger.error("%s is not a valid IP. Program terminated.", args.ip)
        sys.exit()

    signal.signal(signal.SIGINT, signal_handler)

    ploss = 0
    precv = 0
    psum = 0.0

    if args.duration is not None:
        end_time = time.time() + parse_duration(args.duration)
        while time.time() <= end_time:
            ploss, precv, psum = ping(
                host=args.ip, pktsize=args.pktsize, pkt_loss=ploss,
                pkt_recv=precv, ping_sum=psum
            )
            time.sleep(args.interval)

    if args.till is not None:
        end_time = time.strptime(args.till, "%Y/%m/%d_%H:%M:%S")
        while time.localtime() <= end_time:
            ploss, precv, psum = ping(
                host=args.ip, pktsize=args.pktsize, pkt_loss=ploss,
                pkt_recv=precv, ping_sum=psum
            )
            time.sleep(args.interval)

    if args.duration is None and args.till is None:
        while True:
            ploss, precv, psum = ping(
                host=args.ip, pktsize=args.pktsize, pkt_loss=ploss,
                pkt_recv=precv, ping_sum=psum
            )
            time.sleep(args.interval)

    logger.info("Ping finish. Program terminated.")

    if args.output:
        export_report(log_name=log_name, log_path=log_path, notify=args.notify)

    print("\033[0m")
