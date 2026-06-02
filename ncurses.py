import curses
import time
import threading
import pywifi


def main(stdscr):
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # green for enabled
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)  # red for disabled
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # yellow for highlight

    # control Panel
    control_height = curses.LINES // 3
    control_win = curses.newwin(control_height, curses.COLS, 0, 0)
    control_win.keypad(1)
    control_win.border()

    # data display
    data_win = curses.newwin(
        curses.LINES - control_height, curses.COLS, control_height, 0
    )
    data_win.keypad(1)
    data_win.border()

    # control panel options
    wifi_interfaces = ["wlan0", "wlan1"]
    current_interface = 0
    wifi_enabled = False
    gps_enabled = False
    selected_option = (
        0  # 0: Wifi Interface, 1: Wifi Enabled, 2: GPS Enabled, 3: Start/Pause
    )

    def draw_control_panel():
        control_win.clear()
        control_win.border()

        # Highlight the selected option
        if selected_option == 0:
            attr = curses.color_pair(3)  # Highlight
        else:
            attr = curses.A_NORMAL

        control_win.addstr(
            2, 2, f"Wifi Interface: {wifi_interfaces[current_interface]}", attr
        )

        if selected_option == 1:
            attr = curses.color_pair(3)
        else:
            attr = curses.A_NORMAL
        control_win.addstr(
            4, 2, "Wifi Enabled: " + ("[ ]" if not wifi_enabled else "[X]"), attr
        )

        if selected_option == 2:
            attr = curses.color_pair(3)
        else:
            attr = curses.A_NORMAL
        control_win.addstr(
            6, 2, "GPS Enabled: " + ("[ ]" if not gps_enabled else "[X]"), attr
        )

        if selected_option == 3:
            attr = curses.color_pair(3)
        else:
            attr = curses.A_NORMAL
        control_win.addstr(
            8, 2, "Start/Pause: " + ("[ ]" if not is_running else "[X]"), attr
        )

        control_win.refresh()

    def draw_data_table(ssid, bssid):
        data_win.clear()
        data_win.border()

        # Column headers
        data_win.addstr(1, 2, "SSID".center(20), curses.A_BOLD)
        data_win.addstr(1, 22, "BSSID".center(20), curses.A_BOLD)
        data_win.addstr(1, 42, "Latitude".center(20), curses.A_BOLD)
        data_win.addstr(1, 62, "Longitude".center(20), curses.A_BOLD)

        if is_running:
            data_win.addstr(3, 2, ssid.center(20))
            data_win.addstr(3, 22, mac_address.center(20))
            data_win.addstr(3, 42, latitude.center(20))
            data_win.addstr(3, 62, longitude.center(20))

        data_win.refresh()

    def interface_scan():
        wifi = pywifi.PyWiFi()
        interfaces = wifi.interfaces()

        if not interfaces:
            print("No WiFi interfaces found.")
            return None

        iface = interfaces[0]  # Assume the first interface is the one to use
        iface.scan()
        print("Scanning for networks...")

        results = iface.scan_results()
        return results

    # --- Data Display Logic ---
    data_lock = threading.Lock()
    data = {
        "ssid": "N/A",
        "bssid": "N/A",
        "latitude": "N/A",
        "longitude": "N/A"
    }

    def update_data():
        nonlocal is_running
        while True:
            if is_running:
                try:
                    # In a real scenario, we would call interface_scan and a GPS scan here
                    # For now, keeping the placeholder logic but making it safe
                    wifi = pywifi.PyWiFi()
                    iface = wifi.interfaces()[0]
                    iface.scan()
                    results = iface.scan_results()
                    
                    if results:
                        res = results[0]
                        with data_lock:
                            data["ssid"] = res.ssid
                            data["bssid"] = res.bssid
                            # GPS logic would go here
                except Exception:
                    pass
            time.sleep(2)

    # --- Threading for data collection ---
    is_running = False
    data_thread = threading.Thread(target=update_data, daemon=True)
    data_thread.start()

    # --- Main Loop ---
    while True:
        draw_control_panel()
        with data_lock:
            draw_data_table(data["ssid"], data["bssid"])

        key = control_win.getch()

        if key == curses.KEY_UP:
            selected_option = max(0, selected_option - 1)
        elif key == curses.KEY_DOWN:
            selected_option = min(3, selected_option + 1)
        elif key == ord(" "):  # Spacebar for enabling/disabling options
            if selected_option == 0:
                current_interface = (current_interface + 1) % len(wifi_interfaces)
            elif selected_option == 1:
                wifi_enabled = not wifi_enabled
            elif selected_option == 2:
                gps_enabled = not gps_enabled
            elif selected_option == 3:
                is_running = not is_running
        elif key == ord("q"):
            break


if __name__ == "__main__":
    curses.wrapper(main)
