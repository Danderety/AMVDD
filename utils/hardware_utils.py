import platform
import socket
import psutil
import wmi
from PyQt6.QtWidgets import QMessageBox, QInputDialog, QPushButton
def get_os_info():
    edition = platform.win32_edition() if hasattr(platform, "win32_edition") else ""
    arch = platform.architecture()[0]
    arch_str = "64-битная" if "64" in arch else "32-битная"
    name = platform.system()
    version = platform.release()
    return name, f"{version} {edition}".strip(), arch_str

def get_ip_info():
    info = []
    interfaces = psutil.net_if_addrs()
    for name, addresses in interfaces.items():
        ip = mac = mask = ""
        for addr in addresses:
            if addr.family == socket.AF_INET:
                ip = addr.address
                mask = addr.netmask
            elif addr.family == psutil.AF_LINK:
                mac = addr.address.replace("-", ":").upper()
        if ip and mac and not mac[0] == "0":
            info.append((name, ip, mac, mask))

    # приоритет: 192., потом 10., потом всё остальное кроме 25.
    preferred = [entry for entry in info if entry[1].startswith("192.") or entry[1].startswith("10.")]
    fallback = [entry for entry in info if not entry[1].startswith("25.")]
    return preferred or fallback or info












def get_disks():
    c = wmi.WMI()
    logical = {
        ld.DeviceID: ld.VolumeName or ld.DeviceID
        for ld in c.Win32_LogicalDisk()
        if ld.DriveType == 3
    }
    disks = []
    for p in c.Win32_DiskDrive():
        # Надёжная фильтрация: исключаем только флешки и USB
        interface = (p.InterfaceType or "").upper()
        media_type = (p.MediaType or "").upper()
        if "USB" in interface or "REMOVABLE" in media_type or "FLASH" in media_type:
            continue

        model = p.Model.strip() if hasattr(p, "Model") else p.DeviceID
        for partition in p.associators("Win32_DiskDriveToDiskPartition"):
            for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                label = logical.get(logical_disk.DeviceID, logical_disk.DeviceID)
                serial = ""
                try:
                    media = c.query(f"SELECT * FROM Win32_PhysicalMedia WHERE Tag = '{p.DeviceID}'")
                    if media and hasattr(media[0], "SerialNumber"):
                        serial = media[0].SerialNumber.strip()
                except Exception:
                    serial = ""
                disks.append({
                    "name": model,
                    "serial": serial,
                    "size": int(p.Size),
                    "label": label
                })
    return disks



