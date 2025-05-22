#!/usr/bin/env python3
import os
import json
import time
import socket
from pathlib import Path

def read_first(path):
    try:
        return Path(path).read_text().strip()
    except Exception:
        return None

def parse_cgroup_stat(path, key):
    try:
        with open(path) as f:
            for line in f:
                if line.startswith(f"{key} "):
                    return int(line.split()[1])
    except Exception:
        pass
    return 0

def sum_io_stat(path, key):
    total = 0
    devices = {}
    try:
        with open(path) as f:
            for line in f:
                parts = dict(kv.split('=') for kv in line.strip().split()[1:] if '=' in kv)
                dev = line.split()[0]
                value = int(parts.get(key, 0))
                total += value
                devices[dev] = value
    except Exception:
        pass
    return total, devices

def main():
    cwd = Path.cwd()
    instance = cwd.name
    cgroup_path = Path(f"/sys/fs/cgroup/system.slice/gha-runner@{instance}.service")

    cpu_usec = parse_cgroup_stat(cgroup_path / "cpu.stat", "usage_usec")
    mem_peak = int(read_first(cgroup_path / "memory.peak") or 0)
    read_bytes, read_devs = sum_io_stat(cgroup_path / "io.stat", "rbytes")
    write_bytes, write_devs = sum_io_stat(cgroup_path / "io.stat", "wbytes")

    start_pre_file = Path(f"/tmp/{instance}-start-pre")
    pre_start_ms = 0
    if start_pre_file.exists():
        try:
            t0 = int(start_pre_file.read_text().strip())
            t1 = int(time.time() * 1000)
            pre_start_ms = t1 - t0
        except Exception:
            pass
    post_start_ms = int(time.time() * 1000)
    time.sleep(0.1)
    post_stop_ms = int(time.time() * 1000) - post_start_ms

    metadata = {}
    meta_file = cwd / ".job_metadata.json"
    if meta_file.exists():
        try:
            metadata = json.loads(meta_file.read_text())
        except Exception:
            pass

    output = {
        "job": instance,
        "host": socket.gethostname(),
        "cpu_usec": cpu_usec,
        "mem_peak_bytes": mem_peak,
        "io_read_bytes": read_bytes,
        "io_write_bytes": write_bytes,
        "io_read_devices": read_devs,
        "io_write_devices": write_devs,
        "pre_start_ms": pre_start_ms,
        "post_stop_ms": post_stop_ms
    }
    output.update(metadata)

    out_dir = Path("/var/log/github-runner-metrics")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{instance}-{int(time.time())}.json"
    with open(out_file, "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
