import multiprocessing as mp
from multiprocessing import Process, Queue
from multiprocessing.synchronize import Event

import time
from typing import Type, Union

import socket

class StaProcess(Process):

    def __init__(self, closeEvent: Event, queueDict: dict[str, Queue]):
        Process.__init__(self)
        self.closeEvent = closeEvent
        self.queueDict = queueDict

    def run(self):
        if not self.closeEvent.is_set(): # No need to run anything when program should already close
            self.setup()

            try:
                while not self.closeEvent.is_set():
                    if self.loop() is not None:
                        break
            except KeyboardInterrupt:
                self.keyboardInterrupt()

            self.cleanUp()
        
    def log(self, output: str):
        print(mp.current_process().name, output)

    def setup(self):
        self.log("setup")

    def loop(self):
        pass

    def cleanUp(self):
        self.log("cleanUp")

    # Only add Interrupt Routine. Cleanup should only happen in cleanUp() will be usually called
    def keyboardInterrupt(self):
        self.log("CTRL-C")
        
class SocketProcess(StaProcess):
    
    # Need to set in subclass
    HOST: Union[str, bytes, bytearray, None] = None
    PORT: Union[int, None] = None
    
    def setup(self):
        super().setup()
        
        if self.HOST is None or self.PORT is None:
            self.log("Host and Port needed for connection!") # Note: Could only be one missing
            self.closeEvent.set()
            return
        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allows a fast restart of the script
        self.s.bind((self.HOST, self.PORT))
        self.s.listen()

        timeout = self.s.gettimeout()
        self.s.settimeout(1)

        while not self.closeEvent.is_set(): # To ensure socket will stop if event is called
            try:
                conn, addr = self.s.accept()
                self.log(f"Connected by {addr}")
                self.conn = conn

                break
            except socket.timeout:
                pass #Retry accept
            except KeyboardInterrupt:
                self.keyboardInterrupt()

        self.s.settimeout(timeout) # Reset Timeout
        
    def cleanUp(self):
        super().cleanUp()
        
        # Need to check if socket was created
        # If setup prevents creation, cleanUp will fail
        if hasattr(self, "s"):
            self.s.shutdown(2)
            self.s.close()
        
        
class ProcessManager():

    def __init__(self, waitTime: float, shutdownTime: float) -> None:
        self.waitTime: float = waitTime
        self.shutdownTime: float = shutdownTime

        self.exitCode: int | None = None

        self.processes: list[StaProcess] = list()
        self.queueDict: dict[str, Queue] = dict()
        
        self.closeEvent: Event = mp.Event()

    def run(self):
        self.closeEvent.clear()

        timeout: float = self.waitTime / len(self.processes)
        
        for proc in self.processes:
            proc.start()

        try:
            while not self.closeEvent.is_set():
                for proc in self.processes:
                    proc.join(timeout)
        except KeyboardInterrupt:
            self.exitCode = -1
        else:
            self.exitCode = 0
        self.closeEvent.set()
        
        # Waiting for all processes to close themselves
        for proc in self.processes:
            proc.join(self.shutdownTime)

        # Checking if all process have exitcode (None if still running)
        # If not terminate
        for proc in self.processes:
            if proc.exitcode is None:
                print(proc.name, "terminated")
                proc.terminate()
            
        # Ensure that all processes are closed correctly after termination
        # Second join seems to fix problems
        for proc in self.processes:
            proc.join(self.shutdownTime)

        for proc in self.processes:
            proc.close()
            self.processes.remove(proc)


    def addProcess(self, processClass: Type[StaProcess]):
        self.processes.append(processClass(self.closeEvent, self.queueDict))
        
    def addQueue(self, queueName: str):
        self.queueDict[queueName] = Queue()