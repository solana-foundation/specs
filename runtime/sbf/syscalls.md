# Syscalls

Syscalls are VM hardcoded subroutines extending the functionality of the virtual machine.
They generally belong to one of two categories:

- *Runtime syscalls* provide access to external facilities (e.g. logging)
- *Convenience syscalls* provide efficient replacements for functionality that could be implemented without syscalls (e.g. SHA-256 hashing)

## Usage

A syscall is invoked using a [`call` instruction](./isa.md#call) with `dst=0`, `src=0`, `off=0`, and `imm` set to the hash in reverse byte order.

Equivalent bytecode: `concat([0x85, 0x00, 0x00, 0x00], bswap32(hash))`

The `r0` register is always clobbered upon return, in addition to the memory- and CU side effects.
Registers `r1`, `r2`, `r3`, `r4`, `r5` serve as input parameters.

## Index

Each syscall has a symbol name (useful for C linkage) and a 32-bit hash identifier.

The hash function is [murmur3](https://en.wikipedia.org/wiki/MurmurHash#MurmurHash3) in 32-bit mode
using the symbol name as an input (ASCII, no delimiter).

## Reference

### `abort`

Terminates the program with a fatal error.

### `sol_panic_`

Terminates the program with a user-supplied error message.

**Arguments**
- `r1`: pointer to file name string (`char *`)
- `r2`: length of file name string (`uint64_t`)
- `r3`: line number of panic (`uint64_t`)
- `r4`: column of panic (`uint64_t`)

**Routine**
- Consume `r2` compute units
- Perform [string load](#string-load) with `(r1, r2)`
- Raise fatal program error

### `sol_log_`

Writes a message to the logging facility.

**Arguments**
- `r1`: pointer to string
- `r2`: length of string

**Routine**
- Consume `max(syscall_base_cost, r2)` compute units
- Perform [string load](#string-load) with `(r1, r2)`
- Write message to log
- Set `r0` to zero

### `sol_log_64_`

Writes five 64-bit integers to the logging facility.

**Arguments**
- `r1`: argument 1
- `r2`: argument 2
- `r3`: argument 3
- `r4`: argument 4
- `r5`: argument 5

**Routine**
- Consume `log_64_units` compute units
- Write message to log

## Subroutines

### Memory translation

Syscalls are typically implemented in the host context, i.e. the native architecture of the physical machine.
The addresses of pointers and data alignment requirements differ between the VM context and host context.
Passing pointers to VM memory to a syscall requires memory translation.

Unlike the SBF VM memory operations, syscalls memory accesses also require additional alignment checks.
This mainly comes from alignment assumptions made by the host compiler with which the program runtime was built.

- Implicit params: Alignment (`size_t`), access mode (load/store)
- Input params: VM-context pointer (`uint64_t`), memory length (`size_t`)
- Return value: Host-context slice pointer (`void *`)

Aborts the program on error.

**Routine**
- If BPF loader of program is newer than v1 (see [builtins](../builtins/)), then
  - Assert that pointer is aligned
- Perform VM memory access check (depending on load/store mode)
- Translate pointer to host buffers

### Primitive access

A primitive access translates a pointer to a single, statically-sized type from VM context to host context.

Performs a [memory translation](#memory-translation) aligned by the type's size.

### Slice access

A slice access translates a contiguous array of elements from VM context to host context without copies.
The array is assumed densley packed (zero stride).

- Implicit params: Element size (`size_t`)
- Input params: VM-context slice pointer (`uint64_t`), slice element count (`uint64_t`)
- Return value: Host-context slice pointer (`void *`)

Aborts the program on error.

**Routine**
- Assert that total slice length (element count multiplied by element size) is less or equal to `INT64_MAX`
- Perform [memory translation](#memory-translation) aligned by element size

### String load

Performs an unaligned [slice load](#slice-access) and validates the content against UTF-8 encoding rules.

The validation algorithm is Rust's `core::str::validations::run_utf8_validation`
which checks the UTF-8 stream against the ABNF syntax definiton in [RFC 3629, Section 4](https://www.rfc-editor.org/rfc/rfc3629.html#section-4).

Aborts the program on slice load error or UTF-8 validation error.
