"""Local QEMU lifecycle: persistent disks, explicit checkpoints, and isolated WHPX probe."""
import argparse
import json
import socket
import subprocess
import time
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VM = ROOT / "vm/Monterey12-test"
RUNTIME = VM / "persistent"
BIN = ROOT / "downloads/third-party/qemu-windows-11.1.0/installed"
PORT = 45572


class QMP:
    def __init__(self, port=PORT, timeout=15):
        self.sock = socket.create_connection(("127.0.0.1", port), timeout)
        self.sock.settimeout(timeout)
        self.file = self.sock.makefile("rwb", buffering=0)
        self.read()
        self.command("qmp_capabilities")

    def read(self):
        line = self.file.readline()
        if not line:
            raise ConnectionError("QEMU closed QMP")
        return json.loads(line)

    def command(self, name, arguments=None):
        request = {"execute": name, "id": name}
        if arguments is not None:
            request["arguments"] = arguments
        self.file.write((json.dumps(request) + "\n").encode())
        while True:
            response = self.read()
            if response.get("id") != name:
                continue
            if "error" in response:
                raise RuntimeError(response["error"])
            return response.get("return")

    def hmp(self, command):
        return self.command("human-monitor-command", {"command-line": command})

    def close(self):
        self.file.close()
        self.sock.close()


def image(*args):
    subprocess.run([str(BIN / "qemu-img.exe"), *map(str, args)], check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def prepare():
    RUNTIME.mkdir(exist_ok=True)
    # QCOW2 bases allow QEMU VM snapshots; VMDK-backed overlays do not.
    for name, source in (("recovery", "qemu-recovery.vmdk"), ("target", "monterey.vmdk")):
        base = RUNTIME / f"base-{name}.qcow2"
        destination = RUNTIME / f"{name}.qcow2"
        if not base.exists():
            image("convert", "-p", "-f", "vmdk", "-O", "qcow2", "-S", "4k", VM / source, base)
        if not destination.exists():
            image("create", "-f", "qcow2", "-F", "qcow2", "-b", base.as_posix(), destination)
    if not (RUNTIME / "opencore.qcow2").exists():
        image("convert", "-f", "raw", "-O", "qcow2",
              "fat:" + (VM / "qemu-efi-verbose").as_posix(), RUNTIME / "opencore.qcow2")
    if not (RUNTIME / "vars.qcow2").exists():
        image("convert", "-f", "raw", "-O", "qcow2", VM / "qemu-vars-verbose-input.fd", RUNTIME / "vars.qcow2")
    print("Persistent disk images prepared.")


def running():
    try:
        qmp = QMP(timeout=2)
    except (OSError, ConnectionError):
        return False
    else:
        qmp.close()
        return True


def vm_args():
    args = ["-name", "Monterey-Persistent-TCG", "-machine", "q35",
            "-accel", "tcg,thread=multi", "-cpu", "EPYC", "-smp", "4", "-m", "8G",
            "-smbios", "type=1,manufacturer=Apple Inc.,serial=C02C18Y6JWDW",
            "-smbios", "type=2,manufacturer=Apple Inc.,product=Mac-63001698E7A34814,serial=C02953104GUKGQGAD",
            "-drive", f"if=pflash,format=raw,readonly=on,file={(BIN / 'share/edk2-x86_64-code.fd').as_posix()}",
            "-drive", f"if=pflash,format=qcow2,file={(RUNTIME / 'vars.qcow2').as_posix()}"]
    args.extend(["-drive", f"if=none,id=opencore,format=qcow2,file={(RUNTIME / 'opencore.qcow2').as_posix()}",
                 "-device", "ide-hd,drive=opencore,bus=ide.0"])
    for bus, disk in ((1, "recovery"), (2, "target")):
        args.extend(["-drive", f"if=none,id={disk},format=qcow2,file={(RUNTIME / (disk + '.qcow2')).as_posix()}",
                     "-device", f"ide-hd,drive={disk},bus=ide.{bus}"])
    args.extend(["-device", "qemu-xhci,id=xhci", "-device", "usb-kbd,id=kbd,bus=xhci.0,display=video0",
                 "-device", "usb-tablet,id=tablet,bus=xhci.0,display=video0", "-netdev", "user,id=net0",
                 "-device", "e1000-82545em,netdev=net0", "-device", "vmware-svga,id=video0",
                 "-serial", f"file:{(RUNTIME / 'serial.log').as_posix()}",
                 "-qmp", f"tcp:127.0.0.1:{PORT},server,nowait", "-display", "sdl",
                 "-vnc", "127.0.0.1:1"])
    return args


def start(cold=False):
    if running():
        print("VM is already running; no second instance started.")
        return
    prepare()
    args = vm_args()
    restore = (RUNTIME / "checkpoint.json").exists() and not cold
    if restore:
        args += ["-loadvm", "resume"]
    out = (RUNTIME / "stdout.log").open("ab")
    err = (RUNTIME / "stderr.log").open("ab")
    proc = subprocess.Popen([str(BIN / "qemu-system-x86_64.exe"), *args], cwd=VM,
                            stdout=out, stderr=err, creationflags=subprocess.CREATE_NO_WINDOW)
    out.close()
    err.close()
    (RUNTIME / "process.json").write_text(json.dumps({"pid": proc.pid, "restored": restore,
                                                    "args": args}, indent=2))
    deadline = time.monotonic() + 25
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError((RUNTIME / "stderr.log").read_text(errors="replace")[-3000:])
        if running():
            print(json.dumps({"pid": proc.pid, "restored": restore, "qmp_port": PORT}))
            return
        time.sleep(.3)
    raise TimeoutError("VM launched but QMP did not become ready")


def save(suspend=False):
    qmp = QMP(timeout=180)
    try:
        qmp.command("stop")
        result = qmp.hmp("savevm resume")
        if result.strip():
            raise RuntimeError("QEMU snapshot result: " + result)
        snapshots = qmp.hmp("info snapshots")
        if "resume" not in snapshots:
            raise RuntimeError("QEMU did not report the saved checkpoint")
        (RUNTIME / "checkpoint.json").write_text(json.dumps({"name": "resume", "saved_at": time.time(),
                                                            "qemu": "11.1.0", "memory_gib": 8}, indent=2))
        print(snapshots)
        if suspend:
            qmp.command("quit")
        else:
            qmp.command("cont")
    except Exception:
        try:
            qmp.command("cont")
        except Exception:
            pass
        raise
    finally:
        qmp.close()


def probe():
    """Run firmware only; do not attach any guest installation or user disk."""
    RUNTIME.mkdir(exist_ok=True)
    results = []
    for cpu, machine in (("EPYC", "q35"), ("max", "q35"), ("max", "q35,kernel-irqchip=off")):
        port = 45582
        log = RUNTIME / ("whpx-" + str(len(results)) + ".log")
        probe_vars = RUNTIME / "whpx-probe-vars.fd"
        shutil.copyfile(VM / "qemu-vars-clean.fd", probe_vars)
        with log.open("wb") as err:
            args = [str(BIN / "qemu-system-x86_64.exe"), "-machine", machine, "-accel", "whpx",
                    "-cpu", cpu, "-smp", "2", "-m", "512", "-nodefaults", "-display", "none",
                    "-drive", f"if=pflash,format=raw,readonly=on,file={(BIN / 'share/edk2-x86_64-code.fd').as_posix()}",
                    "-drive", f"if=pflash,format=raw,file={probe_vars.as_posix()}",
                    "-qmp", f"tcp:127.0.0.1:{port},server,nowait"]
            p = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=err,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
            qmp = None
            status = None
            try:
                for _ in range(12):
                    if p.poll() is not None:
                        break
                    time.sleep(.3)
                    try:
                        qmp = QMP(port, timeout=2)
                        break
                    except (OSError, ConnectionError):
                        continue
                if qmp:
                    time.sleep(2)
                    if p.poll() is None:
                        status = qmp.command("query-status")
                        qmp.command("quit")
                p.wait(timeout=5)
            except Exception as exc:
                status = {"probe_error": str(exc)}
            finally:
                if qmp:
                    qmp.close()
                if p.poll() is None:
                    p.kill()
                    p.wait()
        results.append({"cpu": cpu, "machine": machine, "exit": p.returncode, "status": status,
                        "stderr": log.read_text(errors="replace")})
    (RUNTIME / "whpx-probe.json").write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


def probe_guest():
    """Boot the real OpenCore/Recovery path ephemerally under WHPX."""
    prepare()
    results = []
    profiles = (("EPYC", "q35"), ("max", "q35"),
                ("max", "q35,kernel-irqchip=off"))
    for index, (cpu, machine) in enumerate(profiles):
        port = 45590 + index
        log = RUNTIME / f"whpx-guest-{index}.log"
        serial = RUNTIME / f"whpx-guest-{index}-serial.log"
        screen = RUNTIME / f"whpx-guest-{index}.ppm"
        probe_vars = RUNTIME / f"whpx-guest-{index}-vars.fd"
        shutil.copyfile(VM / "qemu-vars-verbose-input.fd", probe_vars)
        args = [str(BIN / "qemu-system-x86_64.exe"),
                "-name", f"Monterey-WHPX-Probe-{index}",
                "-machine", machine, "-accel", "whpx", "-cpu", cpu,
                "-smp", "4", "-m", "8G", "-snapshot",
                "-smbios", "type=1,manufacturer=Apple Inc.,serial=C02C18Y6JWDW",
                "-smbios", "type=2,manufacturer=Apple Inc.,product=Mac-63001698E7A34814,serial=C02953104GUKGQGAD",
                "-drive", f"if=pflash,format=raw,readonly=on,file={(BIN / 'share/edk2-x86_64-code.fd').as_posix()}",
                "-drive", f"if=pflash,format=raw,file={probe_vars.as_posix()}"]
        args.extend(["-drive", f"if=none,id=opencore,format=raw,file=fat:{(VM / 'qemu-efi-verbose').as_posix()}",
                     "-device", "ide-hd,drive=opencore,bus=ide.0"])
        for bus, disk in ((1, "recovery"), (2, "target")):
            args.extend(["-drive", f"if=none,id={disk},format=qcow2,file={(RUNTIME / (disk + '.qcow2')).as_posix()}",
                         "-device", f"ide-hd,drive={disk},bus=ide.{bus}"])
        args.extend(["-device", "qemu-xhci,id=xhci",
                     "-device", "usb-kbd,id=kbd,bus=xhci.0,display=video0",
                     "-device", "usb-tablet,id=tablet,bus=xhci.0,display=video0",
                     "-netdev", "user,id=net0", "-device", "e1000-82545em,netdev=net0",
                     "-device", "vmware-svga,id=video0",
                     "-serial", f"file:{serial.as_posix()}",
                     "-qmp", f"tcp:127.0.0.1:{port},server,nowait", "-display", "none"])
        with log.open("wb") as err:
            process = subprocess.Popen(args, cwd=VM, stdout=subprocess.DEVNULL, stderr=err,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
        qmp = None
        state = {"alive_after_seconds": 0}
        try:
            deadline = time.monotonic() + 25
            while time.monotonic() < deadline and process.poll() is None:
                if qmp is None:
                    try:
                        qmp = QMP(port, timeout=3)
                    except (OSError, ConnectionError):
                        time.sleep(.2)
                        continue
                time.sleep(.5)
            state["alive_after_seconds"] = 25 if process.poll() is None else 0
            if qmp is not None and process.poll() is None:
                state["qmp"] = qmp.command("query-status")
                qmp.command("screendump", {"filename": str(screen)})
                qmp.command("quit")
            process.wait(timeout=8)
        except Exception as exc:
            state["probe_error"] = str(exc)
        finally:
            if qmp is not None:
                try:
                    qmp.close()
                except Exception:
                    pass
            if process.poll() is None:
                process.kill()
                process.wait()
        if screen.exists():
            try:
                from PIL import Image
                Image.open(screen).save(screen.with_suffix(".png"))
                state["screen"] = str(screen.with_suffix(".png"))
            except Exception as exc:
                state["screen_error"] = str(exc)
        results.append({"cpu": cpu, "machine": machine, "exit": process.returncode,
                        "state": state, "stderr": log.read_text(errors="replace"),
                        "serial_tail": serial.read_text(errors="replace")[-4000:] if serial.exists() else ""})
    report = RUNTIME / "whpx-guest-probe.json"
    report.write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "start", "cold-start", "save", "suspend", "status", "screen", "probe-whpx", "probe-whpx-guest"])
    arg = parser.parse_args().action
    if arg == "prepare": prepare()
    elif arg in ("start", "cold-start"): start(cold=arg == "cold-start")
    elif arg in ("save", "suspend"): save(suspend=arg == "suspend")
    elif arg == "probe-whpx": probe()
    elif arg == "probe-whpx-guest": probe_guest()
    else:
        qmp = QMP()
        try:
            if arg == "status":
                print(json.dumps(qmp.command("query-status")))
                print(qmp.hmp("info snapshots"))
            else:
                path = RUNTIME / "screen.ppm"
                qmp.command("screendump", {"filename": str(path)})
                from PIL import Image
                Image.open(path).save(path.with_suffix(".png"))
                print(path.with_suffix(".png"))
        finally:
            qmp.close()


if __name__ == "__main__":
    main()
