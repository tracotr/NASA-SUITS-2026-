
import socket
import time
import struct
import json

DEFAULT_IP = "192.168.95.154"
DEFAULT_PORT = 14141

HEADER_SIZE = 8
PACKET_SIZE = 8192

class TSSUpdater:
    def __init__(self, ip =  DEFAULT_IP, port = DEFAULT_PORT):
        self.tss_ip = ip
        self.tss_port = port
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.settimeout(2.0)

    def close(self):
        """
        Close the underlying UDP socket.
        """
        if self.udp_socket is not None:
            try:
                self.udp_socket.close()
            finally:
                self.udp_socket = None

    def __enter__(self):
        """
        Allow use of TSSUpdater as a context manager.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Ensure the UDP socket is closed when leaving a context manager block.
        """
        self.close()

    def __del__(self):
        """
        Best-effort cleanup in case close() was not called explicitly.
        """
        # Suppress any exceptions during garbage collection.
        try:
            self.close()
        except Exception:
            pass
    
    def fetch_data(self, command):
        '''
        Sends a command to the connected TSS server and returns the appropriate JSON data

        :param command: The number for the command
        '''
        timestamp = int(time.time())
        packet = struct.pack(">II", timestamp, command)
        
        try:
            self.udp_socket.sendto(packet, (self.tss_ip, self.tss_port))
            data, _ = self.udp_socket.recvfrom(PACKET_SIZE)

            json_data = json.loads(data[HEADER_SIZE:].strip(b'\x00').decode('utf-8'))
            return json_data
        
        except socket.timeout:
            raise TimeoutError("Error: request timed out.")
        except socket.error as err:
            raise ConnectionError(f"Error: socket error. {err}")
        except json.JSONDecodeError as err:
            raise ValueError(f"Error: json error. {err}")
