# Bincode Serde codec

Bincode is a compact binary codec for the [Serde](./serde.md) data model.

For any given schema, it implements a bijective mapping between the set of valid Serde object and their binary serializations.
This implies that the serialization of any object is deterministic,
and that only this one serialization reconstructs the object when deserialized.

[![Crates.io](https://img.shields.io/crates/v/bincode)](https://crates.io/crates/bincode)

## Modes

This spec documents the following codec modes.

Data must only be deserialized using the same codec mode as originally serialized with.
The codec mode is not self-describing.

- `bincode-fixedint-le`: Fixed-width integers, little-endian scalar order
- `bincode-fixedint-be`: Fixed-width integers, big-endian scalar order

## Rules (fixedint)

- Bincode serialization is not self-describing.
- Byte endianness depends on mode.
- Bit order is most significant bit (MSB) first.
- Every token of serialized data is byte-aligned (8 bits).

### Scalar types

- `unit`: Length 0 bytes
- `u8`, `u16`, `u32`, `u64`: Length 1, 2, 4, 8 bytes respectively.
- `i8`, `i16`, `i32`, `i64` serialized as their `u8`, `u16`, `u32`, `u64` counterparts with two's complement representation.
- `f32`, `f64` serialized as their `u32`, `u64` counterparts with IEEE 754 representation.
- `bool` serialized as `u8`; `0x00` for `false`, `0x01` for `true`.
- `option_tag` serialized as `u8`; `0x00` for `none`, `0x01` for `some`.
- `enum_variant_tag` serialized as `u32`.
- `seq_length` serialized as `u64`.

### Composite types

Options, arrays, sequences, and enums serialize each of their tokens with determinsitic order and without padding.

Key order in maps must be preserved.
The deserializer must raise an error if key order is violated.

### Flags

Flags redefine the serialization of specific types.
They are part of the schema.

#### `short_u16` Flag

Represents an integer value using a variable-length format optimized for short values.

It can represent any 16-bit integer and uses between 1 to 3 bytes doing so.

Encoding rules.
- `0x0000 <= v <= 0x007f`
  - byte 0: `v`
- `0x0080 <= v <= 0x3fff`:
  - byte 0: `0x80 | (v & 0x7f)`
  - byte 1: `v >> 7`
- `0x3fff <= v <= 0xffff`:
  - byte 0: `0x80 | (v & 0x7f)`
  - byte 1: `0x80 | ((v >> 7) & 0x7f)`
  - byte 2: `v >> 14`

Note that `short_u16` byte order is the same regardless of byte endianness.

Applicable on the following data types:
- `u8`, `u16`, `u32`, `u64`, `i8`, `i16`, `i32`, `i64`
- `seq` (applies to `seq_length`)

Although it is possible to represent values greater than `0xFFFF` using the 3 byte format,
deserializers must report these out-of-bounds values as an error.

## Test Fixtures

### `bincode-fixedint-le`

<table>
  <tr>
    <th>Schema</th>
    <th>Expression</th>
    <th>Hex</th>
  </tr>
  <tr>
    <td><code>bool</code></td>
    <td><code>false</code></td>
    <td><code>0x00</code></td>
  </tr>
  <tr>
    <td><code>bool</code></td>
    <td><code>true</code></td>
    <td><code>0x01</code></td>
  </tr>
  <tr>
    <td><code>u8</code></td>
    <td><code>3</code></td>
    <td><code>0x03</code></td>
  </tr>
  <tr>
    <td><code>i8</code></td>
    <td><code>-2</code></td>
    <td><code>0xfe</code></td>
  </tr>
  <tr>
    <td><code>u16</code></td>
    <td><code>4660</code></td>
    <td><code>0x3412</code></td>
  </tr>
  <tr>
    <td><code>i16</code></td>
    <td><code>-4660</code></td>
    <td><code>0xcced</code></td>
  </tr>
  <tr>
    <td><code>u32</code></td>
    <td><code>305419896</code></td>
    <td><code>0x78563412</code></td>
  </tr>
  <tr>
    <td><code>i32</code></td>
    <td><code>-305419896</code></td>
    <td><code>0x88a9cbed</code></td>
  </tr>
  <tr>
    <td><code>u64</code></td>
    <td><code>1311768467750121216</code></td>
    <td><code>0x00efcdab78563412</code></td>
  </tr>
  <tr>
    <td><code>i64</code></td>
    <td><code>-1311768467750121216</code></td>
    <td><code>0x0011325487a9cbed</code></td>
  </tr>
  <tr>
    <td><code>Option&lt;()&gt;</code></td>
    <td><code>None</code></td>
    <td><code>0x00</code></td>
  </tr>
  <tr>
    <td><code>Option&lt;()&gt;</code></td>
    <td><code>Some(())</code></td>
    <td><code>0x01</code></td>
  </tr>
  <tr>
    <td><code>Option&lt;i64&gt;</code></td>
    <td><code>None</code></td>
    <td><code>0x00</code></td>
  </tr>
  <tr>
    <td><code>Option&lt;i64&gt;</code></td>
    <td><code>Some(42)</code></td>
    <td><code>0x012a00000000000000</code></td>
  </tr>
  <tr>
    <td><code>enum Pet { Cat, Dog }</code></td>
    <td><code>Pet::Cat</code></td>
    <td><code>0x00000000</code></td>
  </tr>
  <tr>
    <td><code>enum Pet { Cat, Dog }</code></td>
    <td><code>Pet::Dog</code></td>
    <td><code>0x01000000</code></td>
  </tr>
  <tr>
    <td><code>enum V { A(i64), B(u8) }</code></td>
    <td><code>V::B(0x42)</code></td>
    <td><code>0x0100000042</code></td>
  </tr>
  <tr>
    <td><code>&[u8]</code></td>
    <td><code>&[]</code></td>
    <td><code>0x0000000000000000</code></td>
  </tr>
  <tr>
    <td><code>&str</code></td>
    <td><code>""</code></td>
    <td><code>0x0000000000000000</code></td>
  </tr>
  <tr>
    <td><code>&[u8]</code></td>
    <td><code>&[1, 2, 3]</code></td>
    <td><code>0x0300000000000000010203</code></td>
  </tr>
  <tr>
    <td><code>&str</code></td>
    <td><code>"hellö"</code></td>
    <td><code>0x060000000000000068656c6cc3b6</code></td>
  </tr>
  <tr>
    <td><code>[u16; 2]</code></td>
    <td><code>[0, 9]</code></td>
    <td><code>0x00000900</code></td>
  </tr>
  <tr>
    <td><code>#[short_u16] u16</code></td>
    <td><code>0x0000</code></td>
    <td><code>0x00</code></td>
  </tr>
  <tr>
    <td><code>#[short_u16] u16</code></td>
    <td><code>0x007f</code></td>
    <td><code>0x7f</code></td>
  </tr>
  <tr>
    <td><code>#[short_u16] u16</code></td>
    <td><code>0x0080</code></td>
    <td><code>0x8001</code></td>
  </tr>
  <tr>
    <td><code>#[short_u16] u16</code></td>
    <td><code>0x00ff</code></td>
    <td><code>0xff01</code></td>
  </tr>
  <tr>
    <td><code>#[short_u16] u16</code></td>
    <td><code>0x0100</code></td>
    <td><code>0x8002</code></td>
  </tr>
  <tr>
    <td><code>#[short_u16] u16</code></td>
    <td><code>0x07ff</code></td>
    <td><code>0xff0f</code></td>
  </tr>
  <tr>
    <td><code>#[short_u16] u16</code></td>
    <td><code>0x3fff</code></td>
    <td><code>0xff7f</code></td>
  </tr>
  <tr>
    <td><code>#[short_u16] u16</code></td>
    <td><code>0x4000</code></td>
    <td><code>0x808001</code></td>
  </tr>
  <tr>
    <td><code>#[short_u16] u16</code></td>
    <td><code>0xffff</code></td>
    <td><code>0xffff03</code></td>
  </tr>
  <tr>
    <td><code>#[short_u16] &[u8]</code></td>
    <td><code>[4, 5]</code></td>
    <td><code>0x020405</code></td>
  </tr>
</table>
