#!/usr/bin/env python3
"""
restart.sh equivalent for Windows — clean-stop + start the Neural Memory App server.

Usage:
    python restart.py [port]

Does:
    1. Kill any process holding the DB file or listening on the target port
    2. Remove the stale DB so the server starts fresh
    3. Start server.py on the given port (default 8080)
    4. Poll /health until the server is ready
"""

import os
import sys
import time
import socket
import subprocess
import urllib.request
import json

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_DIR, "data", "memories.db")
SERVER_SCRIPT = os.path.join(PROJECT_DIR, "server.py")


def port_in_use(port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.bind(("0.0.0.0", port))
        s.close()
        return False
    except OSError:
        s.close()
        return True


def kill_python_servers(target_port=None):
    """Kill stale server.py processes and anything holding target_port.
    Uses powershell (wmic is removed on Win11 24H2). Only kills python processes
    whose command line contains 'server.py' to avoid killing hermes/gateway.
    """
    killed = set()
    # 1) Kill by port owner if target_port given
    if target_port is not None:
        try:
            out = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 f"Get-NetTCPConnection -LocalPort {target_port} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess"],
                capture_output=True, text=True, timeout=10,
            )
            for line in out.stdout.splitlines():
                line = line.strip()
                if line.isdigit():
                    pid = int(line)
                    if pid == 0: continue
                    if pid not in killed:
                        subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
                        print(f"  Killed PID {pid} holding port {target_port}")
                        killed.add(pid)
        except Exception as e:
            print(f"  (port kill failed: {e})")

    # 2) Kill stale server.py python processes via powershell
    try:
        ps_cmd = "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -like '*server.py*' } | Select-Object -ExpandProperty ProcessId"
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=10,
        )
        for line in out.stdout.splitlines():
            line = line.strip().strip('"')
            if line.isdigit():
                pid = int(line)
                if pid not in killed:
                    subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
                    print(f"  Killed stale server PID {pid}")
                    killed.add(pid)
        if not killed:
            print("  No stale server.py processes found (or already stopped)")
    except Exception as e:
        print(f"  (process scan failed: {e})")
        # Fallback: taskkill by image but filtered - last resort
        try:
            subprocess.run(["taskkill", "/F", "/FI", "WINDOWTITLE eq server.py*"], capture_output=True)
        except Exception:
            pass
    return killed


def remove_db():
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print(f"  Removed stale DB: {DB_PATH}")
        except PermissionError:
            print(f"  WARNING: Could not remove DB (in use): {DB_PATH}")
            print("  You may need to manually delete it after this script ends.")
        except Exception as e:
            print(f"  WARNING: Could not remove DB: {e}")


def wait_for_server(port: int, timeout: int = 30) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://localhost:{port}/health", timeout=2) as r:
                data = json.loads(r.read())
                if data.get("status") == "ok":
                    print(f"  Server ready: facts={data.get('facts_count')}, "
                          f"embeddings={data.get('embeddings')}")
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

    print(f"\n=== Neural Memory App — Clean Restart ===")
    print(f"  Target port: {port}")
    print(f"  Project dir: {PROJECT_DIR}")

    print("\n[1/3] Killing stale Python processes...")
    kill_python_servers(target_port=port)
    time.sleep(2)

    print("\n[2/3] Clearing stale DB...")
    remove_db()

    print("\n[3/3] Starting server on port " + str(port) + "...")
    proc = subprocess.Popen(
        [sys.executable, SERVER_SCRIPT, str(port)],
        cwd=PROJECT_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if wait_for_server(port):
        print(f"\n✓ Server running at http://localhost:{port}")
        print(f"  (restart.py exiting — server stays alive in background)\n")
        sys.exit(0)
    else:
        print(f"\n✗ Server did not start within 30s")
        proc.terminate()
        sys.exit(1)


if __name__ == "__main__":
    main()
