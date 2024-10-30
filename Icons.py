import struct
import winreg
import os
import ctypes
from ctypes import POINTER, Structure, c_wchar, c_int, sizeof, byref, wintypes
from ctypes.wintypes import BYTE, WORD, DWORD, LPWSTR
import win32api

# Get Icon Positions Part

grid_translator = {0: 0, 16256: 1, 16384: 2,
                   16448: 3, 16512: 4, 16544: 5,
                   16576: 6, 16608: 7, 16640: 8,
                   16656: 9, 16672: 10, 16688: 11,
                   16704: 12, 16720: 13, 16736: 14,
                   16752: 15, 16768: 16}

special_folder_translator = {"::{D20EA4E1-3957-11d2-A40B-0C5020524153}": "Administrative Tools",
                             "::{ED7BA470-8E54-465E-825C-99712043E01C}": "All Tasks"",",
                             "::{21EC2020-3AEA-1069-A2DD-08002b30309d}": "Control Panel",
                             "::{241D7C96-F8BF-4F85-B01F-E2B043341A4B}": "Connections",
                             "::{D20EA4E1-3957-11d2-A40B-0C5020524152}": "Fonts",
                             "::{20D04FE0-3AEA-1069-A2D8-08002B30309D}": "Computer",
                             "::{450D8FBA-AD25-11D0-98A8-0800361B1103}": "Documents",
                             "::{ff393560-c2a7-11cf-bff4-444553540000}": "History",
                             "::{208d2c60-3aea-1069-a2d7-08002b30309d}": "Network Places",
                             "::{2227A280-3AEA-1069-A2DE-08002B30309D}": "Printers and Faxes",
                             "::{7be9d83c-a729-4d97-b5a7-1b7313c39e0a}": "Programs Folder",
                             "::{645FF040-5081-101B-9F08-00AA002F954E}": "Recycle Bin",
                             "::{48e7caab-b918-4e58-a94d-505519c795dc}": "Start Menu",
                             "::{D6277990-4C6A-11CF-8D87-00AA0060F5BF}": "Scheduled Tasks",
                             "::{78F3955E-3B90-4184-BD14-5397C15F1EFC}": "WEI"}


def get_icon_positions(translate_special_folders=True) -> dict:
    with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as aReg:
        with winreg.OpenKey(aReg, r"Software\Microsoft\Windows\Shell\Bags\1\Desktop", winreg.REG_BINARY) as aKey:
            name, value, type_ = winreg.EnumValue(aKey, 9)

    offset = 16
    number_of_items = struct.unpack_from("<I", value[offset:], 8)[0]
    offset += 12

    desktop_items = []

    for x in range(number_of_items):
        uint16_size = struct.unpack_from("<H", value[offset:], 0)[0]
        uint32_filesize = struct.unpack_from("<I", value[offset:], 4)[0]
        fileattr16_ = struct.unpack_from("<H", value[offset:], 12)[0]
        offset += 12
        entry_name = value[offset:(offset + (2 * uint32_filesize - 8))].decode('utf-16-le')
        offset += (2 * uint32_filesize - 4)

        desktop_items.append([x,
                              '{:04x}'.format(uint16_size),
                              0, 0,
                              '{:04x}'.format(fileattr16_),
                              entry_name])

    offset = len(value)

    for x in range(number_of_items):
        offset -= 10
        item_list = [struct.unpack_from("<H", value[offset:], 2)[0],  # column
                     struct.unpack_from("<H", value[offset:], 6)[0],  # row
                     struct.unpack_from("<H", value[offset:], 8)[0]]  # index to desktop_items
        desktop_items[item_list[-1]][2] = int(item_list[0])
        desktop_items[item_list[-1]][3] = int(item_list[1])

    matrix = {}

    for i in desktop_items:
        pos = grid_translator[i[2]], grid_translator[i[3]]

        if translate_special_folders:
            matrix[pos] = special_folder_translator.get(i[-1], i[-1])
        else:
            matrix[pos] = i[-1]

    return matrix


# Set Folder Icon Part

HICON = c_int
LPTSTR = LPWSTR
TCHAR = c_wchar
MAX_PATH = 260
FCSM_ICONFILE = 0x00000010
FCS_FORCEWRITE = 0x00000002
SHGFI_ICONLOCATION = 0x000001000


class GUID(Structure):
    _fields_ = [
        ('Data1', DWORD),
        ('Data2', WORD),
        ('Data3', WORD),
        ('Data4', BYTE * 8)]


class SHFOLDERCUSTOMSETTINGS(Structure):
    _fields_ = [
        ('dwSize', DWORD),
        ('dwMask', DWORD),
        ('pvid', POINTER(GUID)),
        ('pszWebViewTemplate', LPTSTR),
        ('cchWebViewTemplate', DWORD),
        ('pszWebViewTemplateVersion', LPTSTR),
        ('pszInfoTip', LPTSTR),
        ('cchInfoTip', DWORD),
        ('pclsid', POINTER(GUID)),
        ('dwFlags', DWORD),
        ('pszIconFile', LPTSTR),
        ('cchIconFile', DWORD),
        ('iIconIndex', c_int),
        ('pszLogo', LPTSTR),
        ('cchLogo', DWORD)]


class SHFILEINFO(Structure):
    _fields_ = [
        ('hIcon', HICON),
        ('iIcon', c_int),
        ('dwAttributes', DWORD),
        ('szDisplayName', TCHAR * MAX_PATH),
        ('szTypeName', TCHAR * 80)]


def update_folder_icon():
    # !/usr/bin/env python

    # Released to the public domain.
    # http://creativecommons.org/publicdomain/zero/1.0/

    # http://msdn.microsoft.com/en-us/library/ms644950
    SendMessageTimeout = ctypes.windll.user32.SendMessageTimeoutA
    SendMessageTimeout.restype = wintypes.LPARAM  # aka LRESULT
    SendMessageTimeout.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM,
                                   wintypes.UINT, wintypes.UINT, ctypes.c_void_p]

    # http://msdn.microsoft.com/en-us/library/bb762118
    SHChangeNotify = ctypes.windll.shell32.SHChangeNotify
    SHChangeNotify.restype = None
    SHChangeNotify.argtypes = [wintypes.LONG, wintypes.UINT, wintypes.LPCVOID, wintypes.LPCVOID]

    HWND_BROADCAST = 0xFFFF
    WM_SETTINGCHANGE = 0x001A
    SMTO_ABORTIFHUNG = 0x0002
    SHCNE_ASSOCCHANGED = 0x08000000

    SendMessageTimeout(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 0, SMTO_ABORTIFHUNG, 5000, None)
    SHChangeNotify(SHCNE_ASSOCCHANGED, 0, None, None)


def set_folder_icon(folder_path, icon_path):
    if not os.path.isdir(folder_path):
        print("Folder Required To Set The Icon!")
        return

    shell32 = ctypes.windll.shell32

    folder_path = os.path.abspath(folder_path)
    icon_path = os.path.abspath(icon_path)

    fcs = SHFOLDERCUSTOMSETTINGS()
    fcs.dwSize = sizeof(fcs)
    fcs.dwMask = FCSM_ICONFILE
    fcs.pszIconFile = icon_path
    fcs.cchIconFile = 0
    fcs.iIconIndex = 0

    hr = shell32.SHGetSetFolderCustomSettings(byref(fcs), folder_path, FCS_FORCEWRITE)
    if hr:
        raise WindowsError(win32api.FormatMessage(hr))

    sfi = SHFILEINFO()
    hr = shell32.SHGetFileInfoW(folder_path, 0, byref(sfi), sizeof(sfi),
                                SHGFI_ICONLOCATION)

    if hr == 0:
        raise WindowsError(win32api.FormatMessage(hr))

    shell32.SHUpdateImageW(sfi.szDisplayName, sfi.iIcon, 0, 0)


# Example: set_folder_icon("./Graphics", "C:\\Users\\mehme\\OneDrive\\Desktop\\test2.ico")


def remove_folder(folder_path):
    if not os.path.exists(folder_path):
        print(f'The Path - "{folder_path}" - Does Not Exist')
        return

    if not os.path.isdir(folder_path):
        print("Folder Required!")
        return

    folder_contents = os.listdir(folder_path)
    try:
        folder_contents.remove('desktop.ini')
    except ValueError:
        print("No Desktop.ini")

    if folder_contents:
        print("Folder Is Full!")
        return

    try:
        os.system(f'rmdir /S /Q "{folder_path}"')
        update_folder_icon()
    except Exception as e:
        print(e)
