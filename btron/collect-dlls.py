#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# collect-dlls.py OBJDUMP SEARCHDIR DESTDIR EXE_OR_DLL...
#   EXE_OR_DLL が依存する DLL を SEARCHDIR (MinGW の sys-root/mingw/bin) から探し、
#   再帰的に DESTDIR にコピーする. SEARCHDIR に無いものは Windows 付属とみなして飛ばす.
#   (scripts/nsis.py の find_deps と同じ考え方)
import os
import shutil
import subprocess
import sys


def deps_of(objdump, path):
    out = subprocess.check_output([objdump, "-p", path], text=True, errors="replace")
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("DLL Name: "):
            yield line.split("DLL Name: ", 1)[1].strip()


def main():
    objdump, search, dest = sys.argv[1:4]
    todo = list(sys.argv[4:])
    seen = set()
    os.makedirs(dest, exist_ok=True)
    while todo:
        f = todo.pop()
        for dll in deps_of(objdump, f):
            key = dll.lower()
            if key in seen:
                continue
            seen.add(key)
            src = os.path.join(search, dll)
            if not os.path.exists(src):
                continue
            shutil.copy2(src, os.path.join(dest, dll))
            print("copy", dll)
            todo.append(src)


if __name__ == "__main__":
    main()
