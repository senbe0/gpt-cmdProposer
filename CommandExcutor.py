import subprocess
import threading
import queue
from typing import List

import sys

class CommandExecutor:
    def __init__(self, cmd: List[str]):
        self.cmd = cmd
        self.process = None
        self.q = queue.Queue()
        self.output_lines = []

    def enqueue_output(self):
        for line in iter(self.process.stdout.readline, b''):
            self.q.put(line)
        self.process.stdout.close()

    def output_thread(self):
        t = threading.Thread(target=self.enqueue_output)
        t.daemon = True
        t.start()

        # This will print the output
        while self.process.poll() is None:
            try:
                line = self.q.get(timeout=1)  # adjust timeout as needed
                decorded_line = line.decode().rstrip()
                print(decorded_line)
                self.output_lines.append(decorded_line) 
            except queue.Empty:
                pass

    def input_thread(self):
        while self.process.poll() is None:
            try:
                inp = self.q.get(timeout=0.1).decode().rstrip()
                self.process.stdin.write((inp + '\n').encode())
                self.process.stdin.flush()
            except queue.Empty:
                pass

    def execute(self):
        try:
            self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
            self.output_thread()
            self.input_thread()
            print("Command execution completed!")
            return self.output_lines
            
        except Exception as e:
            error_message = str(e)
            self.output_lines = error_message.split("\n")
            print("!!!An error occurred:", error_message)
            print(f"list?: {self.output_lines}")
            return self.output_lines

# if __name__ == "__main__":
#     command = ["sudo", "docker", "ps"]
#     executor = CommandExecutor(command)
#     output_lines = executor.execute()
#     last_five_lines = output_lines[-5:]
#     print("Output----------")
#     print(last_five_lines)
