import socket

class UDPHandler:
    def __init__(self, esp_ip, port=12345):
        self.esp_ip = esp_ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data):
        try:
            self.sock.sendto(data, (self.esp_ip, self.port))
            return True
        except Exception as e:
            print(f"UDP send failed: {e}")
            return False

    def close(self):
        self.sock.close()