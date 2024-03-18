
import ctypes

STD_OUTPUT_HANDLE = -11
BLACK = 0x00
DEFAULT = 0x0007
RED = 0x0004
GREEN = 0x0002
BLUE = 0x0001
INTENSITY = 0x0008
WHITE = DEFAULT | INTENSITY
GRAY = BLACK | INTENSITY
YELLOW = RED | GREEN
LIGHT_BLUE = BLUE | INTENSITY
LIGHT_YELLOW = YELLOW | INTENSITY
std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
def set_console_text_color(color):
    """Set the color of the console text."""
    ctypes.windll.kernel32.SetConsoleTextAttribute(std_out_handle, color)


def printc(text, color, r=False):
    """Print text in the console with the specified color."""
    set_console_text_color(color)
    if r:
        print(text, end='')
    else:
        print(text)
    set_console_text_color(RED | GREEN | BLUE)


def show_progress(block_num, block_size, total_size):
    downloaded = block_num * block_size
    progress = min(int(50 * downloaded / total_size), 50)
    progress_bar = "\r[%s%s] %d%%" % ('■' * progress, ' ' * (50 - progress), int(100 * downloaded / total_size))
    print(progress_bar, end='')
    if downloaded >= total_size:
        print()
