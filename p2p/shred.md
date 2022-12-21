# Shred packets

Shred packets are fragments of blocks (transaction data) that facilitate propagation of within peer-to-peer networks.

Data shreds are created by splitting up block data.
Code shreds are created by constructing erasure codes over the vector of data shreds.

All shreds are signed by the block producer.

## Revisions

Multiple revisions of the shred structures exist.
The shred revision is not explicitly encoded.

### v1: Genesis revision

Solana mainnet-beta genesis launched with support for code and data shreds with the legacy authentication mechanism.

### v2: Explicit data sizes

Breaking change to the data shred header adding a new size field at offset `0x56`.

The shred paylod shifts from offset `0x56` to `0x58`.

### v3: Merkle authentication mechanism

Introduction of two additional shred variants with the Merkle authentication scheme.

## Protocol

### Data Layout

Shreds consist of the following sections, in order:

- Common Header
- Code or Data Header
- Shred Payload
- Zero Padding
- Merkle Proof (optional)

Each field is byte-aligned. Integer byte order is little-endian.

### Packet Size

The `SHRED_SZ_MAX` constant is defined as 1228.

Each shred is sized `SHRED_SZ_MAX` bytes when serialized.

This derives from the IPv6 minimum link MTU of 1280 bytes minus 48 bytes reserved for IPv6 and UDP headers.
Additional 4 bytes are reserved for an optional nonce field.

### Common Header

The common header has size `0x53` (83 bytes).

| Offset | Size | Type              | Name            | Purpose                  |
|--------|-----:|-------------------|-----------------|--------------------------|
| `0x00` |  64B | Ed25519 signature | `signature`     | Block producer signature |
| `0x40` |   1B | `u8`              | `variant`       | Shred variant            |
| `0x41` |   8B | `u64`             | `slot`          | Slot number              |
| `0x49` |   4B | `u32`             | `shred_index`   | Shred index              |
| `0x4d` |   2B | `u16`             | `shred_version` | Shred version            |
| `0x4f` |   4B | `u32`             | `fec_set_index` | FEC Set Index            |

#### Field: Block producer signature

The signature authenticates the fact that a Merkle shred originated from the current block producer at that slot.

The block producer public key is sourced externally.

The content of the signed message used to create the signature depends on the authentication scheme used.

#### Field: Shred Variant

The shred variant identifies the shred type (data, code) and authentication mechanism (legacy, merkle).

The field is encoded as two 4-bit unsigned integers.

The high 4-bit field is at bit range `4:8`.
The low 4-bit field is at bit range `0:4`.

| High 4-bit | Low 4-bit | Shred Type | Authentication |
|------------|-----------|------------|----------------|
| `0x5`      | `0xa`     | Code       | Legacy         |
| `0xa`      | `0x5`     | Data       | Legacy         |
| `0x4`      | Any       | Code       | Merkle         |
| `0x8`      | Any       | Data       | Merkle         |

#### Field: Slot number

Set to the slot number of the block that this shred is part of.

#### Field: Shred index

Set to the index into the code- or data-shred vector within a slot.

#### Field: Shred version

Identifies the network fork of the block that this shred is part of.

### Data Shred Header (rev. v2)

The data shred header

Offsets are relative to the start of the common header.

| Offset | Size | Type  | Name           | Purpose                       |
|--------|-----:|-------|----------------|-------------------------------|
| `0x53` |   4B | `u32` | `parent_dist`  | Slot distance to parent block |
| `0x55` |   1B | `u8`  | `data_flags`   | Data Flags                    |
| `0x56` |   2B | `u16` | `size`         | Total Size                    |
| `0x58` |    - | bytes | `data_payload` | Data Payload                  |

The data flags contain the following fields. (LSB 0 numbering)

| Bits  | Type | Name             | Purpose            |
|-------|------|------------------|--------------------|
| `7`   | bool | `block_complete` | Block complete bit |
| `6`   | bool | `batch_complete` | Batch complete bit |
| `0:6` | `u6` | `batch_tick`     | Batch tick number  |

#### Field: Block complete bit

Set to one if this data shred is the last shred for this block.
Otherwise, set to zero.

The batch complete bit must also be set if set to one.

#### Field: Batch complete bit

Set to zero if the next immediate shred is part of the same batch.

Otherwise, set to one to mark the end of the current batch.

### Data Shred Header (rev. v1)

Revision v1 data shreds.

The total size field is hardcoded to 1228 bytes.

| Offset | Size | Type  | Name           |  Purpose                       |
|--------|-----:|-------|----------------|--------------------------------|
| `0x53` |   4B | `u32` | `parent_dist`  |  Slot distance to parent block |
| `0x55` |   1B | `u8`  | `data_flags`   |  Data Flags                    |
| `0x56` |    - | bytes | `data_payload` |  Data Payload                  |

## Code Shreds

## Legacy Authentication

In the legacy authentication scheme, the block producer signs the content of each shred.

The message to be signed begins 64 bytes past the beginning of the common shred header (skipping the signature field) and includes the entire rest of the shred.
The resulting signature is placed into the _block producer signature_ field.

## Merkle Authentication

In the Merkle authentication scheme, the block producer signs the Merkle root over the FEC set of shreds.
Consequently, the signature field carries identical content for all shreds in the same FEC set.

The Merkle node size is truncated to 20 bytes.

## Shred Construction

Block producers create and broadcast shreds to the validator network while active.

This occurs as a streaming process wherein shreds are constructed in the earliest possible opportunity.

The construction of shreds requires the following steps:
1. Block Entry Batching
2. Data Shredding
3. Erasure Coding
4. Signing

## Block Entry Batching

Batching creates sub-groups of block entries, each of which are serialized into one byte array.

The serialization of a batch is the concatenation of all serialized entries, prefixed by the entry count as a `u64` integer (8 bytes).

## Shredding

The shredding procedure converts each seralized batch into a vector of data shreds.

It is described by the following constraints.

Inputs:
- $B :=$ Solana block metadata
- $E :=$ Vector of entry batches

Intermediate results:
- $I :=$ Vector of last shred index of each batch
- $F :=$ Vector of data shred batches

Outputs:
- $S :=$ Vector of data shreds (Output)

Routines:
```rust
fn serialize_entry_batch(entries: Vec<Entry>) -> Vec<u8>

fn make_data_shreds(meta: BlockMetadata, start_index: usize, blob: Vec<u8>) -> Vec<Shred>
```

**Constraints**

$E \neq \emptyset$
<br/> Entry batch vector is not empty

$S \neq \emptyset$
<br/> Data shred vector is not empty

$\lvert E \rvert = \lvert F \rvert = \lvert I \rvert$
<br/> The number of entry batches equals the number of data shred batches

```math
∀E_i ∈ E :
\begin{cases}
  F_i = \text{make\_data\_shreds}\left(
      B, 0,
      \text{serialize\_entry\_batch}(E_i) \right)
    &\text{if }i = 0\\
  F_i = \text{make\_data\_shreds}\left(
      B, I_{i-1} + 1,
      \text{serialize\_entry\_batch}(E_i) \right)
    &\text{if }i > 0\\
\end{cases}
```
```math
∀F_i ∈ F :
I_i = \text{property}\left( \text{last}({F_i}),
                            \text{"shred\_index"} \right)
```
Each data shred batch is the result of splitting up the corresponding serialized entry shred batch, given various block info, and the shred start index.
<br/> The shred start index is zero for the first batch, and one plus the last shred index of the preceding batch for subsequent batches.

```math
∀b ∈ F : ∀x ∈ [0;\lvert b \rvert) : ∀y ∈ [0;\lvert b \rvert) : y-x =
\text{property}\left( b_y,
                      \text{"shred\_index"} \right)-
\text{property}\left( b_x,
                      \text{"shred\_index"} \right)
```
Shred indices within each shred batch are incrementing

$S = \mathbin\Vert_{i=0}^{\lvert F \rvert} F_i$
<br/> Vector of shreds is the concatenation of all shred batch vectors

```math
∀i ∈ [0;\lvert S \rvert) : i = \text{property} \left( {S_i}, \text{"shred\_index"} \right)
```
Shred indices are incrementing, starting at zero

$∀F_i ∈ F : F_i ⊆ S$
<br/> Each data shred batch is a subset of the data shred vector

```math
∀F_i ∈ F : ∀F_j ∈ F :
\begin{cases}
  F_i = F_j             & \text{if } i = j \\
  F_i ⋂ F_j = \emptyset & \text{if } i \neq j
\end{cases}
```
Data shred batches are non-overlapping

$S = \mathbin\Vert_{i=0}^{\lvert F \rvert} F_i$
<br/> Vector of shreds is the concatenation of all shred batch vectors

```math
b = \text{make\_data\_shreds}\left(
      B, x,
      d \right)
\\⇒\\
\begin{align*}

& \text{property}\left( b_0,
  \text{"shred\_index"} \right)
&=&\, x \\

∀b_i ∈ b :
&\,\text{property}\left( b_i,
  \text{"slot"} \right)
&=&\, \text{property}\left( B,
  \text{"slot"} \right)\\

∀b_i ∈ b :
&\,\text{property}\left( b_i,
  \text{"shred\_version"} \right)
&=&\, \text{property}\left( B,
  \text{"shred\_version"} \right)\\

∀b_i ∈ b :
&\,\text{property}\left( b_i,
  \text{"parent\_dist"} \right)
&=&\, \text{property}\left( B,
  \text{"parent\_dist"} \right)

\end{align*}
```

```math
∀b ∈ F : ∀i ∈ [0;\lvert b \rvert-1) :
\text{length}\left(
  \text{property}( b_i,
    \text{"{payload}"} )\right)
= 1228
```
For all but the last shred in each batch, the data shred size must be 1228 bytes (implying a maximally-sized payload with a zero-byte sized zero padding section).

The last data shred of each batch has the "batch complete" bit set. (data flags bit `0x40`)

The last data shred of the block has the "block complete" bit set. (data flags bit `0x80`)

For each batch, the "batch tick number" of all shreds is set to the index of the first entry within the block. (data flags bit field with mask `0x3f`)

The inverse of the shredding process (deshredding) reconstructs serialized batches from a stream of data shreds.
