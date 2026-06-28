"""
Memory offsets for Deltarune Chapter 5 (June 2026).
"""
from dataclasses import dataclass

@dataclass
class Offsets:
    base_address: int = 0x02A4B3F0
    hp_current: int = 0x1C8
    hp_max: int = 0x1CC
    atk: int = 0x1D0
    def_: int = 0x1D4
    magic: int = 0x1D8
    gold: int = 0x1F0
    inventory_ptr: int = 0x210
    battle_flag: int = 0x248
    timer: int = 0x260
    items_base: int = 0x02A4B4E0

CURRENT_OFFSETS = Offsets()
