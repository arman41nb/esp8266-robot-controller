import websocket
import threading
import time

class WebSocketHandler:
    def __init__(self, url):
        self.url = url
        self.ws = None
        self.connected = False
        self.reconnect_thread = None
        self.stop_reconnect = False

    def connect(self):
        try:
            self.ws = websocket.create_connection(self.url, timeout=5)
            self.connected = True
            print("Connected to ESP")
        except Exception as e:
            print(f"Connection failed: {e}")
            self.connected = False
            self.start_reconnect()

    def start_reconnect(self):
        if self.reconnect_thread is None or not self.reconnect_thread.is_alive():
            self.stop_reconnect = False
            self.reconnect_thread = threading.Thread(target=self._reconnect_loop)
            self.reconnect_thread.daemon = True
            self.reconnect_thread.start()

    def _reconnect_loop(self):
        while not self.stop_reconnect:
            time.sleep(5)  # Try reconnect every 5 seconds
            if not self.connected:
                try:
                    self.ws = websocket.create_connection(self.url, timeout=5)
                    self.connected = True
                    print("Reconnected to ESP")
                except:
                    pass

    def send(self, msg):
        if self.ws and self.connected:
            try:
                self.ws.send(msg)
                return True
            except Exception as e:
                print(f"Send failed: {e}")
                self.connected = False
                self.start_reconnect()
                return False
        else:
            print("Not connected")
            return False

    def close(self):
        self.stop_reconnect = True
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
        self.connected = False