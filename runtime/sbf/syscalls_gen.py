"""
Authoritative list of syscalls available in Solana Bytecode Format.
"""

# pylint: disable=invalid-name

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

SYSCALLS_ABIV1 = [
    "abort",
    "sol_panic_",
    "sol_log_",
    "sol_log_64_",
    "sol_log_compute_units_",
    "sol_log_pubkey",
    "sol_create_program_address",
    "sol_try_find_program_address",
    "sol_sha256",
    "sol_keccak256",
    "sol_secp256k1_recover",
    "sol_blake3",
    "sol_curve_validate_point",
    "sol_curve_group_op",
    "sol_get_clock_sysvar",
    "sol_get_epoch_schedule_sysvar",
    "sol_get_fees_sysvar",
    "sol_get_rent_sysvar",
    "sol_memcpy_",
    "sol_memmove_",
    "sol_memcmp_",
    "sol_memset_",
    "sol_invoke_signed_c",
    "sol_invoke_signed_rust",
    "sol_alloc_free_",
    "sol_set_return_data",
    "sol_get_return_data",
    "sol_log_data",
    "sol_get_processed_sibling_instruction",
    "sol_get_stack_height",
]

SYSCALLS_ABIV2 = [
    "abort",
    "sol_panic_",
    "sol_log_",
    "sol_log_64_",
    "sol_log_compute_units_",
    "sol_log_pubkey",
    "sol_create_program_address",
    "sol_try_find_program_address",
    "sol_sha256",
    "sol_keccak256",
    "sol_secp256k1_recover",
    "sol_blake3",
    "sol_curve_validate_point",
    "sol_curve_group_op",
    "sol_get_clock_sysvar",
    "sol_get_epoch_schedule_sysvar",
    "sol_get_fees_sysvar",
    "sol_get_rent_sysvar",
    "sol_memcpy_",
    "sol_memmove_",
    "sol_memcmp_",
    "sol_memset_",
    "sol_log_data",
    "sol_set_account_attributes",
]


def murmur3_32(data: bytes) -> int:
    """
    Python implementation of MurmurHash3.
    Uses 32-bit words in little-endian order and a zero seed.

    See https://en.wikipedia.org/wiki/MurmurHash
    """

    h = 0
    k = 0

    for i in range(0, len(data), 4):
        if i + 4 <= len(data):
            word = data[i : i + 4]
        else:
            word = data[i:] + bytes([0x00] * (4 - (len(data) % 4)))

        k = (word[3] << 24) | (word[2] << 16) | (word[1] << 8) | (word[0])

        k *= 0xCC9E2D51
        k &= 0xFFFFFFFF
        k = (k << 15) | (k >> 17)
        k &= 0xFFFFFFFF
        k *= 0x1B873593
        k &= 0xFFFFFFFF

        h ^= k
        if i + 4 <= len(data):
            h = (h << 13) | (h >> 19)
            h = h * 5 + 0xE6546B64
            h &= 0xFFFFFFFF

    h ^= len(data)

    h ^= h >> 16
    h *= 0x85EBCA6B
    h &= 0xFFFFFFFF
    h ^= h >> 13
    h *= 0xC2B2AE35
    h &= 0xFFFFFFFF
    h ^= h >> 16

    return h


def test_murmur3_32():
    """
    Test vectors for MurmurHash3-32.
    Source: https://stackoverflow.com/a/31929528
    """

    assert 0x76293B50 == murmur3_32(b"\xff\xff\xff\xff")
    assert 0xF55B516B == murmur3_32(b"\x21\x43\x65\x87")
    assert 0x7E4A8634 == murmur3_32(b"\x21\x43\x65")
    assert 0xA0F7B07A == murmur3_32(b"\x21\x43")
    assert 0x72661CF4 == murmur3_32(b"\x21")
    assert 0x2362F9DE == murmur3_32(b"\x00\x00\x00\x00")
    assert 0x85F0B427 == murmur3_32(b"\x00\x00\x00")
    assert 0x30F4C306 == murmur3_32(b"\x00\x00")
    assert 0x514E28B7 == murmur3_32(b"\x00")
    assert 0x00000000 == murmur3_32(b"")
    assert 0xB6FC1A11 == murmur3_32(b"abort")
    assert 0xADB8EFC8 == murmur3_32(b"sol_get_processed_sibling_instruction")


@dataclass
class SyscallObj:
    """Entry in syscalls.csv"""

    name: str
    hash: int = 0
    abiv1: bool = False
    abiv2: bool = False

    def __post_init__(self):
        self.hash = murmur3_32(self.name.encode("utf-8"))

    def __lt__(self, other):
        return self.name < other.name


def get_syscalls() -> Iterable[SyscallObj]:
    """Generates a sorted list of syscalls."""
    syscalls = {}

    def set_syscall(name, attr):
        obj = syscalls.setdefault(name, SyscallObj(name))
        setattr(obj, attr, True)

    for name in SYSCALLS_ABIV1:
        set_syscall(name, "abiv1")
    for name in SYSCALLS_ABIV2:
        set_syscall(name, "abiv2")

    return list(sorted(syscalls.values()))


def generate(out):
    """Generates the syscalls.csv file."""
    writer = csv.DictWriter(out, fieldnames=["hash", "name", "abiv1", "abiv2"])
    writer.writeheader()
    for s in get_syscalls():
        writer.writerow(
            {
                "hash": "%08x" % (s.hash),
                "name": s.name,
                "abiv1": int(s.abiv1),
                "abiv2": int(s.abiv2),
            }
        )


def _main():
    path = Path(__file__).parent / "syscalls.csv"
    with open(path, "w", encoding="utf-8") as out:
        generate(out)


if __name__ == "__main__":
    _main()
