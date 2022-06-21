from threading import Thread
from itertools import cycle
import time
import sys
from subprocess import CalledProcessError, check_output
from asyncio import subprocess
from colorama import Fore, Style, Back

class Loader:
    done = False
    symbols = cycle(["|------|", "|=-----|", "|-=----|", "|--=---|", "|---=--|", "|----=-|", "|-----=|"])

    def __init__(self):
        pass

    def animate(self):
        start = time.time()
        sys.stdout.write(f"{Style.BRIGHT}")
        for c in self.symbols:
            if self.done:
                break
            
            end = time.time()
            tTime = end - start

            anim = "" + c + " {:.1f} [s]".format(tTime)
            self.animSize = len(anim)

            sys.stdout.write("\r" + self.workMsg + anim)
            sys.stdout.flush()
            time.sleep(0.1)
        backs = '\b' * self.animSize
        sys.stdout.write(f"{backs}{Fore.GREEN}{self.endMsg}{' ' * self.animSize}{Style.RESET_ALL}")

    def run(self, command, workMsg = "Working... ", endMsg = "Done"):
        self.done = False
        self.workMsg = workMsg
        self.endMsg = endMsg

        t = Thread(target = self.animate)
        t.daemon = True
        try:
            com = command.split()
            t.start()
            out = check_output(com, stderr=subprocess.STDOUT)
            self.done = True
            t.join()
            print()
            out = out.decode('utf-8')
        except CalledProcessError as e:
            self.done = True
            t.join()
            out = e.output.decode('utf-8')
            backs = "\b" * (self.animSize + len(endMsg))
            print(f"{backs}{Style.BRIGHT}{Back.RED}Failed:{Style.RESET_ALL}")
            print(out)
            exit(1)
        if out != "":
            backs = "\b" * (self.animSize + len(endMsg))
            print(f"{backs}{Style.BRIGHT}{Fore.MAGENTA}Had warnigns:{Style.RESET_ALL}")
            print(out)