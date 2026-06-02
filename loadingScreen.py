import curses
import time


def display_banner(stdscr, y_offset):
    """Display the ASCII banner."""

    banner = [
        "          oooo  oooo                                         ",
        "          `888  `888                                         ",
        " .oooo.    888   888   .ooooo.   .oooo.   oooo d8b  .oooo.o  ",
        "P  )88b   888   888  d88' `88b `P  )88b  `888V\"8P d88(  L8 ",
        " .oPa888   888   888  888ooo888  .oP_888   888     ` Y88b.   ",
        "d8(  888   888   888  888    .o d8(  888   888     o.  )88b  ",
        "`Y888aaa8o o888o o888o Y8bod8P `Y888&^^8o d888b    8&&888P' ",
    ]

    height, width = stdscr.getmaxyx()
    for i, line in enumerate(banner):
        x = max(0, (width - len(line)) // 2)
        y = y_offset + i
        if y < height:
            stdscr.addstr(y, x, line)


def display_gif_and_progress(stdscr, tasks):
    curses.curs_set(0)  # Hide cursor
    height, width = stdscr.getmaxyx()

    frame_delay = 0.1  # Adjust as needed
    bar_width = width - 10

    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)

    for i, (task_name, duration) in enumerate(tasks):
        start_time = time.time()
        elapsed = 0
        while elapsed < duration:
            stdscr.clear()
            stdscr.bkgd(" ", curses.color_pair(1))

            # Display banner
            display_banner(stdscr, max(0, height // 2 - 5))

            # Display loading bar
            # Calculate overall progress: (completed_tasks + current_task_progress) / total_tasks
            current_task_progress = elapsed / duration
            overall_progress = (i + current_task_progress) / len(tasks)
            
            progress_chars = int(overall_progress * bar_width)
            bar = "=" * progress_chars + " " * (bar_width - progress_chars)
            
            try:
                stdscr.addstr(
                    height - 4, 2, f"[{bar}] {int(overall_progress * 100)}%", curses.color_pair(1)
                )
                stdscr.addstr(
                    height - 3, 2, f" Task {i + 1}/{len(tasks)}: {task_name}", curses.color_pair(1)
                )
            except curses.error:
                pass

            # Refresh screen
            stdscr.refresh()
            time.sleep(frame_delay)

            # Update time
            elapsed = time.time() - start_time

    try:
        stdscr.addstr(height - 2, 2, "(Setup Complete. Press any key to start...)", curses.color_pair(1))
        stdscr.refresh()
        stdscr.nodelay(False)
        stdscr.getch()
    except curses.error:
        pass


def loading(stdscr):
    """Main function to run the curses interface."""

    # Tasks for the loading bar
    tasks = [
        ("Initializing modules", 1),
        ("Loading resources", 2),
        ("Finalizing setup", 1.5),
    ]

    # Display GIF, banner, and progress bar simultaneously
    display_gif_and_progress(stdscr, tasks)
    return 0


if __name__ == "__main__":
    curses.wrapper(loading)
