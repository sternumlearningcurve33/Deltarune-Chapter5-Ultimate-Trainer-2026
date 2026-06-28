"""
Advanced memory manager with pattern scanning, pointer resolution, and caching.
"""
import pymem
import pymem.process
import psutil
import numpy as np
import time
from typing import Optional, List, Tuple
import logging
from .offsets import Offsets

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, process_name: str = "DELTARUNE.exe"):
        self.process_name = process_name
        self.pm: Optional[pymem.Pymem] = None
        self.process_id: Optional[int] = None
        self.module_base: Optional[int] = None
        self.pointer_cache = {}

    def attach(self) -> bool:
        """Attach to the game process."""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and proc.info['name'].lower() == self.process_name.lower():
                    self.process_id = proc.info['pid']
                    break
            if not self.process_id:
                raise Exception("Process not found")
            self.pm = pymem.Pymem(self.process_id)
            module = pymem.process.module_from_name(self.pm.process_handle, self.process_name)
            self.module_base = module.lpBaseOfDll
            logger.info(f"Attached to {self.process_name} (PID: {self.process_id}, base: {hex(self.module_base)})")
            return True
        except Exception as e:
            logger.error(f"Failed to attach: {e}")
            return False

    def is_attached(self) -> bool:
        try:
            if self.pm and self.process_id:
                psutil.Process(self.process_id).status()
                return True
        except:
            pass
        return False

    def read_int(self, address: int) -> int:
        return self.pm.read_int(address)

    def write_int(self, address: int, value: int):
        self.pm.write_int(address, value)

    def pattern_scan(self, pattern: bytes, mask: str) -> Optional[int]:
        """Scan memory for a byte pattern using numpy for speed."""
        if not self.is_attached():
            return None
        try:
            module_end = self.module_base + 0x5000000
            raw_bytes = self.pm.read_bytes(self.module_base, module_end - self.module_base)
            arr = np.frombuffer(raw_bytes, dtype=np.uint8)
            pattern_arr = np.frombuffer(pattern, dtype=np.uint8)
            for i in range(len(arr) - len(pattern)):
                match = True
                for j in range(len(pattern)):
                    if mask[j] == 'x' and arr[i+j] != pattern_arr[j]:
                        match = False
                        break
                if match:
                    return self.module_base + i
            return None
        except Exception as e:
            logger.error(f"Pattern scan failed: {e}")
            return None

    def resolve_pointer(self, base: int, offsets: List[int]) -> Optional[int]:
        """Resolve a multi-level pointer with caching."""
        cache_key = (base, tuple(offsets))
        if cache_key in self.pointer_cache:
            addr = self.pointer_cache[cache_key]
            try:
                self.read_int(addr)
                return addr
            except:
                del self.pointer_cache[cache_key]
        addr = base
        for i, offset in enumerate(offsets):
            try:
                addr = self.read_int(addr + offset)
            except:
                return None
        self.pointer_cache[cache_key] = addr
        return addr

    def close(self):
        if self.pm:
            self.pm.close_process()
