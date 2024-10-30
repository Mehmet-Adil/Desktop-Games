import os
from shutil import rmtree

import ctypes
import winreg

import pyautogui
import win32gui
from win32.lib import win32con


def set_background(image_path: str):
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 0)


def get_background():
    import ctypes as ct
    from ctypes import wintypes as w

    SPI_GETDESKWALLPAPER = 0x0073

    dll = ct.WinDLL('user32')
    dll.SystemParametersInfoW.argtypes = w.UINT, w.UINT, w.LPVOID, w.UINT
    dll.SystemParametersInfoW.restype = w.BOOL

    path = ct.create_unicode_buffer(260)
    dll.SystemParametersInfoW(SPI_GETDESKWALLPAPER, ct.sizeof(path), path, 0)

    return path.value


def get_screen_size(multiplier=1):
    user32 = ctypes.windll.user32
    window_size = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

    return window_size[0] * multiplier, window_size[1] * multiplier


def minimize_all_windows():
    def win_enum_handler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

    win32gui.EnumWindows(win_enum_handler, None)


def minimize_window(window_name):
    def enum_handler(hwnd, _):
        if window_name in win32gui.GetWindowText(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

    win32gui.EnumWindows(enum_handler, None)


def set_view(size: str = "LARGE"):
    minimize_all_windows()

    size = size.upper()
    if size == "LARGE":
        size = "2"
    elif size == "MEDIUM":
        size = "3"
    elif size == "SMALL":
        size = "4"
    else:
        size = "2"  # Default is Large

    pyautogui.hotkey('ctrl', 'shift', size)


def get_view():
    with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as aReg:
        with winreg.OpenKey(aReg, r"Software\Microsoft\Windows\Shell\Bags\1\Desktop", winreg.REG_BINARY) as aKey:
            name, value, type_ = winreg.EnumValue(aKey, 3)
    if value == 256:
        return "EXTRA LARGE"
    elif value == 96:
        return "LARGE"
    elif value == 48:
        return "MEDIUM"
    elif value == 32:
        return "SMALL"
    else:
        raise ValueError("Unknown icon sizes!")


def refresh():
    pyautogui.press("F5")


def remove_folder_contents(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                rmtree(file_path)
        except PermissionError:
            try:
                os.system(f'rmdir /S /Q "{file_path}"')
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
