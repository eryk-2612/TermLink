# AI Code as I was too lazy to bother - works for my setup
import json
import subprocess

class FloppyManager:
    def __init__(self):
        self._inserted = False
        self._device = None
        self._mountpoint = None
        self._missed_scans = 0
        self._removal_scan_threshold = 3
        self._last_scan_valid = False

    @property
    def last_scan_valid(self):
        """Whether the most recent device scan returned usable lsblk data."""
        return self._last_scan_valid

    @property
    def inserted(self):
        return self._inserted

    @property
    def device(self):
        return self._device

    @property
    def mountpoint(self):
        return self._mountpoint

    def scan(self):
        data = self._run_lsblk()

        if data is None:
            self._last_scan_valid = False
            # A transient command failure is not evidence that the disk was removed.
            return None

        self._last_scan_valid = True

        floppy = self._find_floppy(data)

        if floppy is None:
            if self._inserted:
                self._missed_scans += 1
                if self._missed_scans < self._removal_scan_threshold:
                    # Keep the last device while lsblk settles after insertion or mount.
                    return True
            self._clear_state()
            return False

        self._missed_scans = 0
        self._inserted = True
        self._device = floppy["device"]
        self._mountpoint = floppy["mountpoint"]
        return True

    def update(self):
        old_inserted = self._inserted
        old_device = self._device

        scan_result = self.scan()
        if scan_result is None:
            return "unchanged"

        if not old_inserted and self._inserted:
            return "inserted"

        if old_inserted and not self._inserted:
            return "removed"

        if (
            old_inserted
            and self._inserted
            and old_device != self._device
        ):
            return "inserted"

        return "unchanged"

    def mount(self):
        scan_result = self.scan()
        if scan_result is False:
            return None

        # Bereits gemountet
        if self._mountpoint:
            return self._mountpoint

        if not self._device:
            return None

        mountpoint = self._mount_device(self._device)

        if mountpoint is None:
            return None

        # Zustand nach dem Mount aktualisieren
        self.scan()

        # Falls lsblk den Mountpoint bereits kennt
        if self._mountpoint:
            return self._mountpoint

        # Fallback: UDisks2 hat einen Mountpoint geliefert
        self._mountpoint = mountpoint

        return mountpoint

    def unmount(self):
        if not self._device:
            return False

        try:
            subprocess.run(
                [
                    "udisksctl",
                    "unmount",
                    "-b",
                    self._device
                ],
                capture_output=True,
                text=True,
                timeout=5,
                check=True
            )

        except (
            subprocess.SubprocessError,
            FileNotFoundError
        ):
            return False

        self._mountpoint = None

        return True

    def _run_lsblk(self):
        command = [
            "lsblk",
            "-J",
            "-o",
            "NAME,TRAN,RM,SIZE,FSTYPE,LABEL,MOUNTPOINTS"
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=2,
                check=True
            )

            return json.loads(result.stdout)

        except (
            subprocess.SubprocessError,
            json.JSONDecodeError,
            FileNotFoundError
        ):
            return None

    def _find_floppy(self, data):
        devices = data.get("blockdevices", [])

        for device in devices:
            floppy = self._find_floppy_partition(device)
            if floppy:
                return floppy

        return None

    def _find_floppy_partition(self, device, removable_usb_parent=False):
        is_removable_usb = removable_usb_parent or self._is_removable_usb_device(device)
        mountpoint = self._get_mountpoint(device)
        if is_removable_usb and device.get("fstype") and not self._is_zero_size(device.get("size")):
            return {"device": "/dev/" + device["name"], "mountpoint": mountpoint}

        for child in device.get("children") or []:
            floppy = self._find_floppy_partition(child, is_removable_usb)
            if floppy:
                return floppy
        return None

    def _is_removable_usb_device(self, device):
        return (
            device.get("tran") == "usb"
            and self._is_removable(device.get("rm"))
        )

    def _is_floppy_device(self, device):
        return self._is_removable_usb_device(device) and bool(device.get("fstype"))

    def _mount_device(self, device):
        try:
            result = subprocess.run(
                [
                    "udisksctl",
                    "mount",
                    "-b",
                    device
                ],
                capture_output=True,
                text=True,
                timeout=10,
                check=True
            )

        except subprocess.CalledProcessError as error:
#            print("Floppy could not be mounted:")
#            print(error.stderr.strip())

            return None

        except (
            subprocess.TimeoutExpired,
            FileNotFoundError
        ):
            return None

        return self._parse_mountpoint(result.stdout)

    def _parse_mountpoint(self, output):
        marker = " at "

        if marker not in output:
            return None

        mountpoint = output.split(marker, 1)[1].strip()

        if mountpoint.endswith("."):
            mountpoint = mountpoint[:-1]

        return mountpoint

    def _get_mountpoint(self, device):
        mountpoints = device.get("mountpoints")

        if not mountpoints:
            return None

        for mountpoint in mountpoints:
            if mountpoint:
                return mountpoint

        return None

    def _is_removable(self, value):
        return value in (
            True,
            1,
            "1",
            "true",
            "True"
        )

    def _is_zero_size(self, size):
        if not size:
            return True

        size = str(size).strip().upper()

        return size == "0B"

    def _clear_state(self):
        self._inserted = False
        self._device = None
        self._mountpoint = None
        self._missed_scans = 0

