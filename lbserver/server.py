import asyncio
import os
import pickle
import time


class Server:
    def __init__(self, port=31313):
        self._port = port
        self._lb = [('AAA', 0) for i in range(10)]
        self._read_leaderboard()

    def _read_leaderboard(self):
        if os.path.exists('leaderboard.db'):
            with open('leaderboard.db', 'rb') as f:
                try:
                    self._lb = pickle.load(f)
                except pickle.UnpicklingError as err:
                    print(f'Encountered an error while unpickling: {err}')

    def _update_lb(self, name, score):
        write = False
        for i in range(10):
            if score > self._lb[i][1]:
                self._lb.insert(i, (name, score))
                write = True
                break
        self._lb = self._lb[:10]
        if write:
            with open('leaderboard.db', 'wb') as f:
                try:
                    pickle.dump(self._lb, f)
                except (pickle.PickleError, pickle.PicklingError) as err:
                    print(f'Encountered an error while pickling: {err}')

    async def handle_request(self, reader, writer):
        data = await reader.read(100)
        addr = writer.get_extra_info('peername')
        print(f'New connection from: {addr!r}')

        reply = b'\0'
        if data[0] == 31:   # Get the leader board
            reply = ','.join([f'{self._lb[i][0]}-{self._lb[i][1]}' for i in range(10)]).encode()
        elif data[0] == 99: # Submit to the leader board
            reply = chr(1).encode()
            score = 0
            if len(data) < 5:
                reply = b'\0'
            else:
                name = data[1:4].decode()
                try:
                    score = int(data[4:])
                except ValueError:
                    print(f'Did not get an int')
                    reply = b'\0'
                self._update_lb(name, score)

        writer.write(reply)
        await writer.drain()

        print(f'Closing connection from: {addr!r}')
        writer.close()


async def main():
    s = Server()
    server = await asyncio.start_server(s.handle_request, '', 31313)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    pid = os.fork()
    if pid:
        print(f'Forked into PID={pid}, waiting a bit...')
        time.sleep(5)
        print('Main thread exiting')
    else:
        print('Start asyncio server')
        asyncio.run(main())
