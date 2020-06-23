import socket
import threading
from controller.drone import Drone
import cv2
import time


class TelloController(Drone):
    """
    Interact simply with tello drone
    """

    def __init__(self, drone_ip="192.168.10.1", drone_port=8889, local_ip='0.0.0.0', local_port=5809,
                 command_timeout=30, control_timeout=5):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((local_ip, local_port))
        self.drone_address = (drone_ip, drone_port)
        self.response = None
        self.state = None

        self.receive_thread = threading.Thread(target=self.__thread_handler)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        self.state_recv = threading.Thread(target=self.get_state, daemon=True)
        self.state_recv.start()

        self.command_timeout = command_timeout
        self.control_timeout = control_timeout

        self.error_flag = False

        if not self._connect():
            raise RuntimeError("Drone hasn't returned a response")

    def __thread_handler(self):
        """
        Receive responses from drone and places them in self.response

        Returns: None
        """
        while True:
            try:
                self.response = self.socket.recv(256)
            except Exception:
                break

    def _set_error_flag(self):
        self.error_flag = not self.error_flag

    def send_command(self, command: str, timeout: float) -> bool:
        """
        Send command to Tello and wait for response
        Args:
            timeout (float): Command timeout
            command (bool): Command to send

        Returns:
             (bool): True if command succeeded, False if not
        """
        self.error_flag = False
        timer = threading.Timer(timeout, self._set_error_flag)
        self.socket.sendto(command.encode('utf-8'), self.drone_address)

        timer.start()
        while self.response is None:
            if self.error_flag:
                raise RuntimeError("command timed out")
        timer.cancel()

        response = self.response.decode('utf-8')
        self.response = None
        if response == 'ok':
            return True
        elif response == 'error':
            return False
        return False

    def send_command_without_response(self, command: str):
        """
            Send command to Tello and wait for response
            Args:
                command (bool): Command to send
        """
        self.socket.sendto(command.encode('utf-8'), self.drone_address)


    def _connect(self) -> bool:
        """
        Connect to tello sdk

        Returns(bool): True if connected, False if failed
        """
        return self.send_command("command", self.command_timeout)

    def takeoff(self):
        return self.send_command("takeoff", self.command_timeout)

    def land(self):
        return self.send_command("land", self.command_timeout)

    def emergency(self):
        return self.send_command("emergency", self.command_timeout)

    def stop(self):
        return self.send_command("stop", self.control_timeout)

    def start_stream(self):
        return self.send_command("streamon", self.command_timeout)

    def stop_stream(self):
        return self.send_command("streamoff", self.command_timeout)

    def move(self, direction: str, x: int):
        return self.send_command(f"{direction} {x}", self.control_timeout)

    def rotate_clockwise(self, x: int):
        return self.send_command(f"cw {x}", self.control_timeout)

    def rotate_counter_clockwise(self, x: int):
        return self.send_command(f"ccw {x}", self.control_timeout)

    def go_to(self, x: int, y: int, z: int, speed: int):
        return self.send_command(f"go {x} {y} {z} {speed}", self.control_timeout)

    def go_to_curve(self, x1: int, x2: int, y1: int, y2: int, z1: int, z2: int, speed: int):
        return self.send_command(f"curve {x1} {y1} {z1} {x2} {y2} {z2} {speed}", self.control_timeout)

    def flip(self, direction: str):
        return self.send_command(f"flip {direction}", self.control_timeout)

    def get_state(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', 8890))
        while True:
            state_string = sock.recv(1024).decode('utf-8')
            list_states = state_string.split(';')[:-1]
            self.state = dict([i.split(':') for i in list_states])

    def set_rc(self, x: int, y: int, z: int, yaw: int):
        return self.send_command_without_response(f"rc {x} {y} {z} {yaw}")


class TelloVideoReceiver(cv2.VideoCapture):
    def __init__(self):
        self.address = 'udp://0.0.0.0:11111'
        super().__init__(self.address)

        self.frame = None
        self.status = False

        self.thread = threading.Thread(target=self._thread_handler, daemon=True)
        self.thread.start()

    def read(self, image=None):
        return self.status, self.frame

    def release(self):
        super().release()

    def _thread_handler(self):
        while True:
            if self.isOpened():
                self.status, self.frame = super().read()
            else:
                self.status, self.frame = (False, None)
