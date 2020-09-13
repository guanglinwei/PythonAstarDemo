import subprocess
import sys
import get_pip
import os
import importlib
import contextlib

def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

required = ["pygame", "tk"]
failed = []

if len(required) > 0:
    msg = "You are about to install the following packages:\n"
    for p in required:
        msg += p + "\n"
    print(msg)
    print("Proceed (y/n)?", end = " ")
    ans = input()

    if ans.lower() == "y":
        for p in required:
            try:
                with contextlib.redirect_stdout(None):
                    __import__(p)

            except ImportError:
                print("-- ", p, "not installed")

                try:
                    print("-- Trying to install", p, "with pip")

                    try:
                        import pip

                    except:
                        print("[WARNING] Pip is not installed")
                        print("-- Installing pip")
                        get_pip.main()
                        print("-- Pip has been installed")

                    print("-- Installing", p)
                    install(p)
                    with contextlib.redirect_stdout(None):
                        __import__(p)

                    print("-- ", p, "has been installed")
                except Exception as e:
                    print("[ERROR] Could not install", p, "-", e)
                    failed.append(p)

    else:
        print("Operation terminated by user.")
else:
    print("-- No packages to install")

if len(failed) > 0:
    print("[FAILED]", len(failed), "package(s) could not be installed:", end=" ")
    for x, p in enumerate(failed):
        print(p)
