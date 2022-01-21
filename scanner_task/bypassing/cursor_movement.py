# cursor_movement.py
# python
import threading
import json
# external
import mouse
from mouse._mouse_event import MoveEvent


class MoveCursorTask:
    """
    Simulates cursor movements to trick browser fingerprinting
    """
    def __init__(self):
        self._running = True
        with open('scanner_task/bypassing/mousemovements.json') as fp:
            self._mousepath = json.load(fp)
            self._mousepath = [MoveEvent(x, y, time) for (x, y, time) in self._mousepath]

    def terminate(self):
        self._running = False

    def run(self):
        # Radius
        R = 300
        X, Y = (1288, 497)
        mouse.move(X+R, Y)

        while self._running:
            mouse.play(self._mousepath)


def start_cursor_thread() -> MoveCursorTask:
    cursor_task = MoveCursorTask()
    th = threading.Thread(target=cursor_task.run)
    th.start()

    return cursor_task


def kill_task(ct: MoveCursorTask) -> None:
    ct.terminate()
