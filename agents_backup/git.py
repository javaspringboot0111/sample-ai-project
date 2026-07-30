import subprocess

def get_latest_commit():

    return subprocess.check_output(

        ["git","log","-1"]

    ).decode()
