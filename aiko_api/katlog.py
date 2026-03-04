#!/usr/bin/env python3
# katlog_ludicrous.py – zero-deps, zero-chill, zero-copy(ish) logger
# logs so fast it makes `dmesg` feel insecure
from __future__ import annotations
import os, sys, time, threading, atexit

# ---- colour only if worthy ----
_COLOR = {} if os.getenv("NO_COLOR") else {
    b"TRACE": b"\033[90m",
    b"DEBUG": b"\033[36m",
    b"INFO":  b"\033[32m",
    b"WARN":  b"\033[33m",
    b"ERROR": b"\033[31m",
}
_RESET = b"\033[0m" if _COLOR else b""

# ---- nanosecond wall-clock ----
def _ts() -> bytes:
    t = time.time_ns()
    hh = (t // 3_600_000_000_000) % 24
    mm = (t // 60_000_000_000) % 60
    ss = (t // 1_000_000_000) % 60
    return b"%02d:%02d:%02d" % (hh, mm, ss)

# ---- lock-free fast path ----
_Q = []
_LOCK = threading.Lock()
_EVT = threading.Event()
_WORKER: threading.Thread | None = None

def _writer():
    global _Q
    while not _EVT.is_set():
        _EVT.wait(0.05)  # 20 Hz batch flush
        with _LOCK:
            batch, _Q = _Q, []
        if not batch: continue
        for chunk in batch:
            sys.stdout.buffer.write(chunk)
        sys.stdout.buffer.flush()

def _push(chunk: bytes):
    global _WORKER
    with _LOCK:
        _Q.append(chunk)
    if _WORKER is None:
        _WORKER = threading.Thread(target=_writer, daemon=True)
        _WORKER.start()

# ---- logger that skips leg day ----
_LVL_MAP = {b"TRACE": 0, b"DEBUG": 1, b"INFO": 2, b"WARN": 3, b"ERROR": 4}

class Logger:
    __slots__ = ("_lvl_val", "_file", "_name", "_lvl")
    def __init__(self, name: str, file: bool = False, level: bytes = b"INFO"):
        self._lvl = level
        self._lvl_val = _LVL_MAP.get(level, 2)
        self._name = name.encode()
        self._file = None
        if file:
            os.makedirs("logs", exist_ok=True)
            self._file = open(f"logs/{name}.log", "ab", buffering=0)
    def log(self, lvl: bytes, msg: str):
        if _LVL_MAP.get(lvl, 2) < self._lvl_val: return
        ts = _ts()
        head = b"[ " + ts + b" ] > [ " + _COLOR.get(lvl, b"") + lvl + _RESET + b" ] : "
        body = msg.encode("utf-8", "replace") + b"\n"
        _push(head + body)
        if self._file:
            self._file.write(head + body)
    def trace(self, m: str): self.log(b"TRACE", m)
    def debug(self, m: str): self.log(b"DEBUG", m)
    def info(self, m: str):  self.log(b"INFO", m)
    def warn(self, m: str):  self.log(b"WARN", m)
    def error(self, m: str): self.log(b"ERROR", m)
    def close(self):
        if self._file: self._file.close()

_LOGGERS: dict[str, Logger] = {}
def get_logger(name="system", *, file=False, level="INFO"):
    lvl = level.upper().encode()
    return _LOGGERS.setdefault(name, Logger(name, file, lvl))

def _shutdown():
    _EVT.set()
    if _WORKER: _WORKER.join(timeout=0.5)
    for l in _LOGGERS.values(): l.close()
atexit.register(_shutdown)
