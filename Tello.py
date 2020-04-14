import socket
import threading
from Drone import Drone


class TelloController(Drone):
    """
    Interact simply with tello drone
    """

    def __init__(self, drone_ip, drone_port, local_ip='127.0.0.1', local_port=5809, command_timeout=.3):
        self.command_timeout = command_timeout
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((local_ip, local_port))
        self.drone_address = (drone_ip, drone_port)
        self.response = None

        self.receive_thread = threading.Thread(target=self._thread_handler)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        if not self.connect:
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

    def __send_command(self, command: str):  # TODO make sure the command arrives
        """
        Send command to Tello and wait for response
        Args:
            command (str): The command in Tello sdk style

        Returns:
            Command Response

        """
        error_flag = False
        timer = threading.Timer(self.command_timeout, error_flag)
        self.socket.sendto(command.encode('utf-8'), self.drone_address)

        timer.start()
        if self.response is None:
            if error_flag:
                raise RuntimeError("command timed out")
        timer.cancel()

        response = self.response
        self.response = None
        return response

    def connect(self):
        """
        Connect to tello sdk

        Returns(str): error or ok
        """
        return self.__send_command("Command")

    def takeoff(self):
        return self.__send_command("takeoff")

    def land(self):
        return self.__send_command("land")

    def emergency(self):
        return self.__send_command("emergency")

    def stop(self):
        return self.__send_command("stop")

    def move(self, direction: str, x: int):
        return self.__send_command(f"{direction} {x}")

    def rotate_clockwise(self, x: int):
        return self.__send_command(f"cw {x}")

    def rotate_counter_clockwise(self, x: int):
        return self.__send_command(f"ccw {x}")

    def go_to(self, x: int, y: int, z: int, speed: int):
        return self.__send_command(f"go {x} {y} {z} {speed}")

    def go_to_curve(self, x1: int, x2: int, y1: int, y2: int, z1: int, z2: int, speed: int):
        return self.__send_command(f"curve {x1} {y1} {z1} {x2} {y2} {z2} {speed}")

    def flip(self, direction: str):
        return self.__send_command(f"flip {direction}")



