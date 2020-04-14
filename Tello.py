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
