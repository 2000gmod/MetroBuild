#!/usr/bin/python3

from asyncio import subprocess
from genericpath import exists

from pathlib import Path
import datetime as d
import sys
import os
import time

from colorama import Fore, Style, Back

from util import *
from loader import Loader


def openConfigFile():
    try:
        with open("metrofile", "r") as metrofile:
            keys = {}
            for line in metrofile:
                stripped = line.strip()
                if (len(stripped) == 0 or stripped[0] == "#"):
                    continue
                k, v = stripped.split("=")
                keys[k.strip()] = v.strip()
            return keys
    except FileNotFoundError:
        print(f"{Style.BRIGHT} {Fore.RED}Fatal error:{Fore.RESET} No metrofile provided \n (Run 'metro init' to"
                        f" create a metrofile in interactive mode){Style.RESET_ALL}")
        exit(1)

def main():
    
    args = sys.argv
    if len(args) > 2 or len(args) == 1:
        print(f"{Style.BRIGHT} {Fore.RED}Error:{Fore.RESET} Invalid number of arguments{Style.RESET_ALL}")
        exit(1)
    
    option = args[1]
    p = Path(".")
    greeter()

    if option == "init":
        init(p)
        return
    

    
    keys = openConfigFile()

    
    
    if option == "build":
        build(p, keys)
    elif option == "clean":
        clean(p, keys)
    elif option == "rebuild":
        clean(p, keys)
        build(p, keys)
    elif option == "run" or option == "r":
        build(p, keys)
        run(p, keys)
    else:
        print(f"{Style.BRIGHT}\n {Fore.RED}Fatal error:{Fore.RESET}\n Invalid option: [{option}]{Style.RESET_ALL}")


def build(p: Path, keys: dict):
    start = time.time()
    print(f"{Fore.GREEN}{Style.BRIGHT}Starting build... {Style.RESET_ALL}")
    worker = Loader()


    objdir = p / Path(f"{keys['OBJDIR']}")
    if not objdir.exists():
        objdir.mkdir()
    
    

    sources = [path for path in p.glob(f"./{keys['SRCDIR']}/**/*.cpp")]
    
    objectNames = [f"./{keys['OBJDIR']}/" + str(src).replace("/", "_").replace(".cpp", ".o") for src in sources]
    objectFiles = [Path(name) for name in objectNames]
    dependencyFiles = [Path(name.replace(".o", ".d")) for name in objectNames]

    print(f"{Style.BRIGHT}\tFound {len(sources)} source files{Style.RESET_ALL}")

    for i in range(0, len(sources)):
        srcName = str(sources[i])
        objName = str(objectFiles[i])

        if needsRebuild(objectFiles[i], dependencyFiles[i]):
            worker.run(f"{keys['CC']} -MMD {keys['CFLAGS']} -c {srcName} -o {objName}", f"\tCompiling {srcName}... ")
    
    allObj = ""
    for obj in objectNames:
        allObj += obj + " "

    outdir = p / Path(f"{keys['OUTDIR']}")
    if not outdir.exists():
        outdir.mkdir()
    target = outdir / Path(f"{keys['TARGET']}")

    linkFlag = needsLink(target, objectFiles)
    if linkFlag:
        worker.run(f"{keys['CC']} {keys['LFLAGS']} -o {str(target)} {allObj}", "\tLinking to target... ")
    
    end = time.time()
    tTime = "{:.3f}".format(end - start)

    if linkFlag:
        print(f"\n{Fore.GREEN}{Style.BRIGHT}Build finished in {tTime}[s] {Style.RESET_ALL}")
    else:
        print(f"\n{Fore.GREEN}{Style.BRIGHT}Build is up to date {Style.RESET_ALL}")

def needsLink(tgt: Path, deps: list[Path]) -> bool:
    if not tgt.exists():
        return True
    
    for obj in deps:
        if obj.stat().st_mtime_ns > tgt.stat().st_mtime_ns:
            return True
    
    return False

def needsRebuild(objf: Path, depf: Path) -> bool:
    if (not objf.exists()) or (not depf.exists()):
        return True
    
    deps = getDependencies(depf)
    for dep in deps:
        if dep.stat().st_mtime_ns > objf.stat().st_mtime_ns:
            return True
    return False


def getDependencies(depf: Path) -> list[Path]:
    filestr = ""
    with open(depf, "r") as f:
        for line in f:
            filestr += line

    filestr = filestr.split(":")[1].strip()
    filestr = filestr.replace("\\", "")
    depstrList = [name.strip() for name in filestr.split()]
    depPaths = [Path(name) for name in depstrList]
    return depPaths

import shutil

def clean(p: Path, keys: dict):
    print(f"{Fore.GREEN}{Style.BRIGHT}Deleting output directories... {Style.RESET_ALL}")
    outdir = p / Path(f"{keys['OUTDIR']}")
    objdir = p / Path(f"{keys['OBJDIR']}")
    
    if outdir.exists():
        shutil.rmtree(outdir)
    if objdir.exists():
        shutil.rmtree(objdir)

def run(p: Path, keys: dict):
    print(f"{Fore.GREEN}{Style.BRIGHT}Running {keys['TARGET']} with args = '{keys['MAINARGS']}' {Style.RESET_ALL}")
    target = p / Path(f"{keys['OUTDIR']}") / Path(f"{keys['TARGET']}")
    os.system(str(target) + f" {keys['MAINARGS']}")

def init(p: Path):
    print(f"{Fore.GREEN}{Style.BRIGHT}Interactive metrofile creation mode {Style.RESET_ALL}")
    with open(p / "metrofile", "w") as f:
        cc = input("Compiler to use: ")
        tgt = input("Executable name: ")
        out = input("Executable directory: ")
        obj = input("Generated object file directory: ")
        src = input("Source code directory: ")


        f.write(f"CC = {cc}\n")
        f.write(f"CFLAGS = -Wall -Wextra -Wpedantic\n")
        f.write(f"LFLAGS = \n\n")
        f.write(f"MAINARGS = \n\n")
        f.write(f"TARGET = {tgt}\n")
        f.write(f"OUTDIR = {out}\n")
        f.write(f"OBJDIR = {obj}\n")
        f.write(f"SRCDIR = {src}\n")

    print(f"{Fore.GREEN}{Style.BRIGHT}Successfully created metrofile, remember to open the file to see further options {Style.RESET_ALL}")