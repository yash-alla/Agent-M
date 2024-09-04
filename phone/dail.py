def dial_number(extension):
    import subprocess
    import os
    extension = str(extension)
    PBX_IP = "192.168.5.150"
    PBX_PORT = 5060
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    MICROSIP_PATH = os.path.join(SCRIPT_DIR, "MicroSIP", "microsip.exe")
    # Verify if the MicroSIP executable exists
    if not os.path.exists(MICROSIP_PATH):
        print(f"MicroSIP executable not found at {MICROSIP_PATH}")
        return

    # Command to dial a number using MicroSIP
    sip_uri = f"sip:{extension}@{PBX_IP}:{PBX_PORT}"
    command = f'"{MICROSIP_PATH}" {sip_uri}'
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Dialing {sip_uri}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while dialing: {e}")

    return

