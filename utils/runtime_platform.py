import subprocess, logging, venv, sys, os


logger = logging.getLogger(__name__)


# i know only about two paths xd
if sys.platform == "linux":
    VENV = [".venv", "bin"]
    _PYTHON = ["python"]

else:
    VENV = [".venv", "Scripts"]
    _PYTHON = ["python.exe"]


PYTHON = VENV + _PYTHON
PATH_TO_PYTHON = os.sep.join(PYTHON)


def in_venv():
    return sys.prefix != sys.base_prefix


def check_platform():
    # if venv not exists then create it
    if not os.path.isfile(PATH_TO_PYTHON):
        print("Creating .venv...")
        venv.create(".venv", with_pip=True)
        install_packages()
        start_venv()
    
    elif not in_venv():
        start_venv()


def install_packages():
    custom_requirements = "requirements.txt"
    command = [PATH_TO_PYTHON, "-m", "pip", "install", "-r", custom_requirements]
    print(f"Starting install packages from {custom_requirements!r}")

    p = subprocess.Popen(command)
    returncode = p.wait()
    if returncode != 0:
        logger.error("idk what happened. write to me, maybe i can do something: https://a1ekzfame.t.me")
        exit(returncode)
    print("Packages installed")
    return


def install_package(package: str) -> bool:
    command = [PATH_TO_PYTHON, "-m", "pip", "install", package]
    print(f"Starting install package {package!r}")

    p = subprocess.Popen(command)
    returncode = p.wait()
    if returncode != 0:
        logger.error("idk what happened. something goes wrong")
        return False
    print("Package installed")
    return True


def start_venv():
    command = [PATH_TO_PYTHON, "main.py", '"IT IS MINECRAFT SERVER CHECK BOT, IF YOU CHECK COMMAND LINE AND SEE THIS!"']
    print(f"Starting main.py with {PATH_TO_PYTHON!r}")
    p = subprocess.Popen(command)
    returncode = p.wait()
    exit(returncode)


check_platform()
