import sys
import os
import platform

def get_environment_report() -> dict:
    """
    Returns a dictionary containing minimal environment information.
    """
    return {
        "python_version": sys.version,
        "python_version_info": {
            "major": sys.version_info.major,
            "minor": sys.version_info.minor,
            "micro": sys.version_info.micro,
        },
        "os_name": os.name,
        "platform": platform.platform(),
    }

if __name__ == "__main__":
    report = get_environment_report()
    for key, value in report.items():
        print(f"{key}: {value}")
