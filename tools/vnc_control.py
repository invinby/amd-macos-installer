"""Read the local QEMU VNC screen and send individual keyboard keys."""
import argparse
import socket
import struct
import time
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "vm/Monterey12-test/persistent/vnc-screen.png"
HOST = "127.0.0.1"
PORT = 5901
KEYS = {
    "up": 0xFF52,
    "down": 0xFF54,
    "left": 0xFF51,
    "right": 0xFF53,
    "tab": 0xFF09,
    "enter": 0xFF0D,
    "escape": 0xFF1B,
    "space": 0x20,
}


def receive(sock, size):
    data = bytearray()
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("QEMU VNC closed the connection")
        data.extend(chunk)
    return bytes(data)


class VNC:
    def __init__(self):
        self.sock = socket.create_connection((HOST, PORT), timeout=5)
        self.sock.settimeout(10)
        version = receive(self.sock, 12)
        if not version.startswith(b"RFB "):
            raise RuntimeError(f"Unexpected VNC greeting: {version!r}")
        self.sock.sendall(version)
        security_count = receive(self.sock, 1)[0]
        security_types = receive(self.sock, security_count)
        if 1 not in security_types:
            raise RuntimeError("Local VNC is not offering no-password access")
        self.sock.sendall(b"\x01")
        if struct.unpack(">I", receive(self.sock, 4))[0] != 0:
            raise RuntimeError("VNC handshake failed")
        self.sock.sendall(b"\x01")
        init = receive(self.sock, 24)
        self.width, self.height = struct.unpack(">HH", init[:4])
        name_length = struct.unpack(">I", init[20:24])[0]
        self.name = receive(self.sock, name_length).decode(errors="replace")

        # Request 32-bit pixels in B,G,R,unused byte order and raw rectangles.
        pixel_format = struct.pack(">BBBBHHHBBBxxx", 32, 24, 0, 1,
                                   255, 255, 255, 16, 8, 0)
        self.sock.sendall(b"\x00\x00\x00\x00" + pixel_format)
        self.sock.sendall(b"\x02\x00\x00\x01" + struct.pack(">i", 0))

    def key(self, name):
        keysym = KEYS.get(name.lower())
        if keysym is None:
            raise ValueError(f"Unsupported key {name!r}; choose from {', '.join(KEYS)}")
        self.sock.sendall(struct.pack(">BBHI", 4, 1, 0, keysym))
        time.sleep(0.08)
        self.sock.sendall(struct.pack(">BBHI", 4, 0, 0, keysym))
        print(f"Sent one {name} key to {self.name} ({self.width}x{self.height})")

    def click(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError(f"Click coordinates must fit the {self.width}x{self.height} screen")
        event = lambda buttons: struct.pack(">BBHH", 5, buttons, x, y)
        self.sock.sendall(event(1))
        time.sleep(0.08)
        self.sock.sendall(event(0))
        print(f"Clicked {x},{y} on {self.name}")

    def screen(self):
        self.sock.sendall(b"\x03\x00" + struct.pack(">HHHH", 0, 0,
                                                        self.width, self.height))
        message = receive(self.sock, 4)
        if message[0] != 0:
            raise RuntimeError(f"Unexpected VNC server message type {message[0]}")
        rectangles = struct.unpack(">H", message[2:4])[0]
        rgb = bytearray(self.width * self.height * 3)
        for _ in range(rectangles):
            x, y, width, height, encoding = struct.unpack(">HHHHi", receive(self.sock, 12))
            if encoding != 0:
                raise RuntimeError(f"Unexpected VNC encoding {encoding}; expected raw pixels")
            raw = receive(self.sock, width * height * 4)
            for row in range(height):
                source = row * width * 4
                target = ((y + row) * self.width + x) * 3
                for column in range(width):
                    blue, green, red, _ = raw[source + column * 4:source + column * 4 + 4]
                    rgb[target + column * 3:target + column * 3 + 3] = bytes((red, green, blue))
        Image.frombytes("RGB", (self.width, self.height), bytes(rgb)).save(OUTPUT)
        print(f"Saved current VM screen to {OUTPUT}")

    def close(self):
        self.sock.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("screen", "key", "click"))
    parser.add_argument("value", nargs="?", help="Key name for key action, or X coordinate for click")
    parser.add_argument("y", nargs="?", type=int, help="Y coordinate for click action")
    args = parser.parse_args()
    client = VNC()
    try:
        if args.action == "screen":
            client.screen()
        elif args.value:
            if args.action == "key":
                client.key(args.value)
            elif args.y is not None:
                client.click(int(args.value), args.y)
            else:
                parser.error("click action needs X and Y coordinates")
        else:
            parser.error("key action needs a key name")
    finally:
        client.close()


if __name__ == "__main__":
    main()
