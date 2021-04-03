import socket


class LeaderBoard:
    def __init__(self, addr='cops.tizilogic.com', port=31313):
        self._addr = addr
        self._port = port
        self._lb = []

    def leaderboard(self):
        """If able to connect to the server, returns a list of 10 tuple(name, score)."""
        if not self._lb:
            self._update_lb()
        return self._lb

    def submit(self, name, score):
        """
        Submit a score to the leaderboard. Returns True if communication was successful.
        True does not mean that the score made it into the top 10!!!
        """
        reply = self._send_msg(f'{chr(99)}{name}{score}'.encode())
        self._lb = []  # Force update on next read
        if reply[0] == 1:
            return True
        return False

    def _update_lb(self):
        reply = self._send_msg(chr(31).encode()).decode()
        lb = reply.split(',')
        if len(lb) == 10:
            self._lb = [tuple(i.split('-')) for i in lb]

    def _send_msg(self, msg):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((self._addr, self._port))
            s.sendall(msg)
            data = s.recv(100)
            s.close()
        except (OSError, ConnectionAbortedError, ConnectionError, ConnectionRefusedError) as err:
            print(f'Something went wrong: {err}')
            return b'\0'
        return data
