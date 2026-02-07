def shell_ping_server(args=None, context=None):
    import subprocess
    result = subprocess.run(
        ["ping", "192.168.50.102"],
        capture_output=True,
        text=True,
        timeout=40
    )
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    return_code = result.returncode
    if "Request timed out" in stdout:


