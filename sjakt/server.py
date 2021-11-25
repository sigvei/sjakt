import asyncio
from asyncinotify import Inotify, Mask
import glob
import json
import logging
from pathlib import Path
import websockets
from websockets.server import WebSocketServerProtocol

connected = set()
games = list()
filenames = set()


def addfile(filename):
    filenames.add(filename)


async def send_file(websocket, filename: Path):
    try:
        with open(filename, "r") as f:
            data = {"game": filename.name, "pgn": f.read()}
            await websocket.send(json.dumps(data))
    except FileNotFoundError:
        filenames.remove(filename)


async def await_file_changes(dirname: Path):
    for f in dirname.glob("*.pgn"):
        logging.info("Found file: %s", f)
        filenames.add(f)

    with Inotify() as inotify:
        inotify.add_watch(dirname, Mask.CREATE | Mask.MODIFY)

        async for event in inotify:
            if event.path.suffix == ".pgn":
                logging.info("New file event %s: %s", event.path, event.mask)
                filenames.add(event.path)
                for socket in connected:
                    await send_file(socket, event.path)


async def handler(websocket: WebSocketServerProtocol):
    logging.info("New connection %s, from %s", websocket.id, websocket.remote_address)
    try:
        connected.add(websocket)
        for fname in filenames:
            await send_file(websocket, fname)
        while True:
            await websocket.recv()
    except:
        pass
    finally:
        connected.remove(websocket)
        logging.info("Connection %s lost", websocket.id)


async def serve():
    await websockets.serve(handler, "", 8000)


async def start():
    await asyncio.gather(serve(), await_file_changes(Path.cwd()))


def main():
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start())


if __name__ == "__main__":
    asyncio.run(main())
