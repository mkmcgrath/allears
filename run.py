import os
import sys
import sqlite3
import json
import pywifi
from datetime import datetime
from time import sleep
from gpsScan import scan_gps
from loadingScreen import loading
import curses


def ensure_root():  # Make sure user has root
    if os.geteuid() != 0:
        print("This script must be run as root. Attempting to re-run with sudo...")
        os.execvp("sudo", ["sudo", sys.executable] + sys.argv)


def setup_database(db_name="wifi_networks.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS networks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ssid TEXT,
            bssid TEXT,
            signal INTEGER,
            frequency INTEGER,
            auth INTEGER,
            akm INTEGER,
            cipher INTEGER,
            timestamp TEXT,
            longitude FLOAT,
            latitude FLOAT,
            altitude FLOAT
        )
    """)
    conn.commit()
    return conn


def interface_scan():
    wifi = pywifi.PyWiFi()
    interfaces = wifi.interfaces()

    if not interfaces:
        print("\nERROR: No WiFi interfaces found.")
        print("This usually happens on Linux if wpa_supplicant is not configured with a control interface.")
        print("Ensure 'ctrl_interface=/var/run/wpa_supplicant' is in your /etc/wpa_supplicant/wpa_supplicant.conf")
        return None

    iface = interfaces[0]
    iface.scan()
    print(f"Scanning for networks on {iface.name()}...")

    results = iface.scan_results()
    return results


def save_to_database(cursor, networks, gpsdata):
    for network in networks:
        akm_serialized = json.dumps(network.akm)  # Serialize the AKM list
        cursor.execute(
            """
            INSERT INTO networks (ssid, bssid, signal, frequency, auth, akm, cipher, timestamp, longitude, latitude, altitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                network.ssid,
                network.bssid,
                network.signal,
                network.freq,
                network.auth,
                akm_serialized,  # Store the serialized list
                network.cipher,
                datetime.now().isoformat(),
                gpsdata[1], # longitude
                gpsdata[0], # latitude
                gpsdata[2], # altitude
            ),
        )


def display_networks(networks, gpsdata):
    # Get terminal dimensions
    try:
        rows, columns = os.get_terminal_size()
    except OSError:
        rows, columns = 80, 24

    # Define column widths based on content and terminal size
    column_widths = [
        max(10, columns // 10),  # SSID
        17,  # BSSID
        8,   # Signal
        10,  # Frequency
        6,   # Auth
        10,  # AKM
        8,   # Cipher
        15,  # Longitude
        15,  # Latitude
        10,  # Altitude
    ]

    print("\nTO EXIT, PRESS CTRL+C\n")
    
    header_fmt = "| {:^{}} | {:^{}} | {:^{}} | {:^{}} | {:^{}} | {:^{}} | {:^{}} | {:^{}} | {:^{}} | {:^{}} |"
    header = header_fmt.format(
        "SSID", column_widths[0],
        "BSSID", column_widths[1],
        "Signal", column_widths[2],
        "Freq", column_widths[3],
        "Auth", column_widths[4],
        "AKM", column_widths[5],
        "Cipher", column_widths[6],
        "Longitude", column_widths[7],
        "Latitude", column_widths[8],
        "Altitude", column_widths[9]
    )
    separator = "-" * len(header)

    print(separator)
    print(header)
    print(separator)

    # Print network data rows
    row_fmt = "| {:<{}} | {:<{}} | {:>{}} | {:>{}} | {:<{}} | {:<{}} | {:<{}} | {:>{}} | {:>{}} | {:>{}} |"
    for network in networks:
        akm_string = network.akm
        if isinstance(network.akm, list):
            akm_string = ", ".join(str(x) for x in network.akm)

        print(
            row_fmt.format(
                str(network.ssid)[:column_widths[0]], column_widths[0],
                str(network.bssid), column_widths[1],
                str(network.signal), column_widths[2],
                str(network.freq), column_widths[3],
                str(network.auth), column_widths[4],
                str(akm_string)[:column_widths[5]], column_widths[5],
                str(network.cipher), column_widths[6],
                f"{gpsdata[1]:.5f}" if gpsdata else "N/A", column_widths[7],
                f"{gpsdata[0]:.5f}" if gpsdata else "N/A", column_widths[8],
                f"{gpsdata[2]:.1f}" if gpsdata else "N/A", column_widths[9]
            )
        )
    print(separator)


def main():
    ensure_root()
    curses.wrapper(loading)
    conn = setup_database()
    cursor = conn.cursor()

    networks = []
    gpsdata = None

    try:
        while True:
            networks = interface_scan()
            gpsdata = scan_gps()

            if networks:
                os.system("clear")  # Clear the screen
                display_networks(networks, gpsdata)
                save_to_database(cursor, networks, gpsdata if gpsdata else [0, 0, 0])
                conn.commit()
            else:
                print("No networks found.")

            sleep(3)  # Introduce a short delay

    except KeyboardInterrupt:
        print("\nScanning stopped by user (Ctrl+C).")

    finally:
        conn.close()
        print("Wi-Fi scan complete.")


if __name__ == "__main__":
    main()
