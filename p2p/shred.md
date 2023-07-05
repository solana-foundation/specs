# Shred packets

Shred packets are fragments of blocks (transaction data) that facilitate propagation within peer-to-peer networks.

Data shreds are created by splitting up block data.
Code shreds are created by constructing erasure codes over data shreds grouped into Forward Error Correction (FEC) sets.

All shreds are signed by the block producer.

## Revisions

Multiple revisions of the shred structures exist.
The shred revision is not explicitly encoded.

### v1: Genesis revision

Solana mainnet-beta genesis launched with support for code and data shreds with the legacy authentication mechanism.

### v2: Explicit data sizes

Breaking change to the data shred header adding a new size field at offset `0x56`.

The shred payload shifts from offset `0x56` to `0x58`.

### v3: Merkle authentication mechanism

Introduction of two additional shred variants with the Merkle authentication scheme.

## Protocol

### Data Layout

Shreds consist of the following sections, in order:

- [Common Header](#common-header)
- [Data Header](#data-shred-header-rev-v2) or [Code Header](#code-shred-header)
- [Shred Payload](#shred-payload-construction)
- [Zero Padding](#zero-padding) (if any)
- [Merkle Proof](#merkle-proof) (if any)

Each field is byte-aligned. Integer byte order is little-endian.

### Packet Size

The `SHRED_SZ_MAX` constant is defined as 1228.

If using Legacy authentication,
each shred occupies `SHRED_SZ_MAX` bytes when serialized.
If using Merkle authentication, coding shreds occupy `SHRED_SZ_MAX` bytes,
and data shreds occupy 1203 bytes.

This derives from the IPv6 minimum link MTU of 1280 bytes minus 48 bytes reserved for IPv6 and UDP headers.
An additional 4 bytes are reserved for an optional nonce field.

## Common Header

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

The signature authenticates the fact that a shred originated from the current block producer at that slot.

The block producer's public key is sourced externally.

The content of the signed message used to create the signature depends on the authentication scheme used:

* In the legacy authentication scheme, the block producer signs the content of each shred.
The message to be signed begins 64 bytes past the beginning of the common shred header (i.e. skipping the signature field) and spans the entire rest of the shred, including any zero padding.
The resulting signature is placed into the _block producer signature_ field.

* In the Merkle authentication scheme, the block producer signs the Merkle root over the FEC set of shreds. See [Merkle Proof](#merkle-proof) for more details.
Consequently, the signature field carries identical content for all shreds in the same FEC set.
The Merkle node size is truncated to 20 bytes.

#### Field: Shred Variant

The shred variant identifies the shred type (data, code) and authentication mechanism (legacy, Merkle).

The field is encoded as two 4-bit unsigned integers.

The high 4-bit field is at bit range `4:8`.
The low 4-bit field is at bit range `0:4`.

| High 4-bit | Low 4-bit | Shred Type | Authentication |
|------------|-----------|------------|----------------|
| `0x5`      | `0xa`     | Code       | Legacy         |
| `0xa`      | `0x5`     | Data       | Legacy         |
| `0x4`      | Any       | Code       | Merkle         |
| `0x8`      | Any       | Data       | Merkle         |

When using Merkle authentication,
the low 4 bits indicate the height of the Merkle tree.
This number is defined below as $h$.

#### Field: Slot number

Set to the slot number of the block that this shred is part of.

#### Field: Shred index
For data shreds, set to the index of this shred among all data shreds within a slot.
For coding shreds, set to the index of this shred among all coding shreds within a slot.

#### Field: Shred version

Identifies the network fork of the block that this shred is part of.

#### Field: FEC Set Index

Set to the shred index of the first shred in the same FEC set as this shred.
All shreds with the same FEC Set Index are part of the same FEC set.

## Data Shred Header (rev. v2)

The data shred header

Offsets are relative to the start of the common header.

| Offset | Size | Type  | Name           | Purpose                       |
|--------|-----:|-------|----------------|-------------------------------|
| `0x53` |   2B | `u16` | `parent_offset`| Slot distance to parent block |
| `0x55` |   1B | `u8`  | `data_flags`   | Data Flags                    |
| `0x56` |   2B | `u16` | `size`         | Total Size                    |

The data payload begins at offset `0x58` from the start of the common header.

The data flags contain the following fields. (LSB 0 numbering)

| Bits  | Type | Name             | Purpose            |
|-------|------|------------------|--------------------|
| `7`   | bool | `block_complete` | Block complete bit |
| `6`   | bool | `batch_complete` | Batch complete bit |
| `0:6` | `u6` | `batch_tick`     | Batch tick number  |

#### Field: Block complete bit

Set to one if this data shred is the last shred for this block.
Otherwise, set to zero.

The final shred in a block is also the final shred in its respective batch,
so the batch complete bit must also be set to one if the block complete bit is set to one.

#### Field: Batch complete bit
Set to one if this data shred is the last shred for this entry batch.
Otherwise, set to zero to indicate that the next data shred is part of the same entry batch.


#### Field: Total size
The size of this packet including the common shred header, the data shred header, and the data payload.
The size excludes the zero-padding (if any)
and the Merkle proof (if using Merkle authentication).

### Data Shred Header (rev. v1)

Revision v1 data shreds.

The total size field is assumed to be 1228 bytes and thus not included in the packet.

| Offset | Size | Type  | Name           |  Purpose                       |
|--------|-----:|-------|----------------|--------------------------------|
| `0x53` |   2B | `u16` | `parent_offset`|  Slot distance to parent block |
| `0x55` |   1B | `u8`  | `data_flags`   |  Data Flags                    |

The data payload begins at offset `0x56` from the start of the common header.


## Code Shred Header


| Offset | Size | Type  | Name               |  Purpose                       |
|--------|-----:|-------|--------------------|--------------------------------|
| `0x53` |   2B | `u16` | `num_data_shreds`  |  Number of data shreds         |
| `0x55` |   2B | `u16` | `num_coding_shreds`|  Number of coding shreds       |
| `0x57` |   2B | `u16` | `position`         |  Position of this shred in FEC set |

The Reed-Solomon coding payload begins at  offset `0x59` from the start of the common header.


#### Field: Number of data shreds
Set to the number of data shreds in the FEC set to which this packet belongs.
Every coding shred in a set must have the same value in this field.

#### Field: Number of coding shreds
Set to the number of coding shreds in the FEC set to which this packet belongs.
Every coding shred in a set must have the same value in this field.

#### Field: FEC set position
Identifies which Reed-Solomon shard this packet contains.
Must be in the range $[0, \texttt{num}\textunderscore\texttt{coding}\textunderscore\texttt{shreds})$.
This field was not present and set to 0 prior to https://github.com/solana-labs/solana/pull/27136.
Every coding shred in a set must have a unique value in this field.

## Shred Payload Construction

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

The shredding procedure converts a serialized entry batch into a vector of data shreds.
In this section, the serialized entry batch is split into fixed-size pieces which form the payload of each data shred,
and the associated metadata is computed.

First, we must compute $S$, the size of the payload of each data shred.
* For shreds using the Legacy authentication scheme, $S$ has a hardcoded value of 1051.
This is small enough to ensure that they payload of a code shred can cover the data shred's headers while still fitting in 1228 bytes.
* For shreds using the Merkle authentication scheme, $S = 1095 - 20 \lceil \log_2 (N+K) \rceil$,
where $N+K$ is the total number of data and code shreds in the FEC set
(see next section for details.
Unfortunately, this means the definition is somewhat circular,
and $S$ is only constant for a specific FEC set,
not for the entire entry batch.
This implies that when using Merkle authentication,
the shredding and erasure coding steps are not entirely independent.
In order to preserve clarity of presentation, we will describe them separately.)

Let $\ell$ be the length in bytes of the serialized entry batch and
$x_0, x_1, \ldots,  x_{\ell-1}$ be the serialized entry batch bytes.

Then the payload of the $i$ th data shred is $x_{iS}, x_{iS+1}, \ldots, x_{(i+1)S-1}$
for $0\le i < \lfloor{\ell/S}\rfloor$.
If $\ell$ is not divisible by $S$, then the final payload is 0-padded to $S$ bytes, i.e.
$x_{\lfloor{\ell/S}\rfloor S}, x_{\lfloor{\ell/S}\rfloor S+1}, \ldots, x_{\ell-1}, \underbrace{0, 0, \; \ldots\;, 0}_{\ell-S\lfloor{\ell/S}\rfloor bytes}$.


The shred index of the first shred of the first batch in the block is 0.
The shred index of each subsequent shred is one larger than the shred index of the previous shred.
The shred index of the first shred in a subsequent batch is one larger than the shred index of the last shred in the previous batch.
That is, shred indices increase monotonically without resetting at each batch.


The last data shred of each batch has the "batch complete" bit set.
This field can be extracted using data flags bit `0x40`.

The last data shred of the block has the "block complete" bit set.
This field can be extracted using data flags bit `0x80`.
Since a block contains an integral number of entry batches,
the last data shred of the block must also be the last data shred of a batch.

The "batch tick number" of all shreds in a batch is set to the
number of PoH ticks that have passed since the beginning of the slot
for the first entry in the batch.
Since Solana has 64 ticks per slot, this field cannot overflow.
This field can be extracted using data flags bit field with mask `0x3f`.
When the "block complete" flag is set to 1, "batch tick number" may be set to 0.



The inverse of the shredding process (deshredding) reconstructs serialized batches from a stream of data shreds.

## Erasure Coding
Data shreds are grouped together to form forward error correction (FEC) sets.
The block producer may choose $N$,
the number of contiguous data shreds to include in the FEC set.
However, an FEC set must have at least 1 and no more than 67 data shreds,
and $N=32$ is recommended.


Given the chosen value of $N$,
a compliant block producer must produce $K$ code shreds as given by the following table:

| $N$ | $K$ | Total shreds ($N+K$) |  | | $N$ | $K$ | Total shreds ($N+K$) |
|-----|-----|----------------------|--|--|-----|-----|---------------------|
|	1	  |	17	|	18	|	|	|	17	|	26	|	43	|
|	2 	|	18	|	20	|	|	|	18	|	27	|	45	|
|	3 	|	19	|	22	|	|	|	19	|	27	|	46	|
|	4 	|	19	|	23	|	|	|	20	|	28	|	48	|
|	5 	|	20	|	25	|	|	|	21	|	28	|	49	|
|	6 	|	21	|	27	|	|	|	22	|	29	|	51	|
|	7 	|	21	|	28	|	|	|	23	|	29	|	52	|
|	8 	|	22	|	30	|	|	|	24	|	29	|	53	|
|	9 	|	23	|	32	|	|	|	25	|	30	|	55	|
|	10	|	23	|	33	|	|	|	26	|	30	|	56	|
|	11	|	24	|	35	|	|	|	27	|	31	|	58	|
|	12	|	24	|	36	|	|	|	28	|	31	|	59	|
|	13	|	25	|	38	|	|	|	29	|	31	|	60	|
|	14	|	25	|	39	|	|	|	30	|	32	|	62	|
|	15	|	26	|	41	|	|	|	31	|	32	|	63	|
|	16	|	26	|	42	|	|	|	32	|	32	|	64	|

For $N>32$, use $K=N$.

However, a compliant implementation may also accept FEC sets with a different number of code shreds as long as $1\le K, N \le 67$.

Code shreds are produced from the data shreds using Reed-Solomon encoding.
When using legacy authentication,
the interpretation of "data shred" used for erasure coding
starts with the first byte of the common header of the data shreds
and includes the signature field.
When using Merkle authentication,
the interpretation of "data shred" used for erasure coding begins immediately after the signature field
and ends immediately before the Merkle proof section.

Let $x_{i,b}$ be the $b$-th byte of the $i$-th data shred of the FEC set (numbered $0, 1, \ldots, N-1$) interpreted as an element of the finite field $GF(2^8)$ (i.e. 
 $\mathbb{F}_2[\gamma] / (\gamma^8 + \gamma^4 + \gamma^3 + \gamma^2 + 1)$

Taking one $b$ at a time, define the polynomial $P_b(x)$ of order less than $N$ such that $P_b(i) = x_i$ for all $0\le i < N$ (interpreting the byte value of $i$ as an element of $GF(2^8)$).
This polynomial is unique.

Then the $b$-th byte of each code shred comes from evaluating $P_b$ as subsequent points.
More precisely, let $y_{j,b}$ be the $b$-th byte of the $j$-th code shred for $0\le j < K$.
Then $y_{j,b} = P_b(N+j)$, where $N+j$ is computed as an integer and then interpreted as an element of $GF(2^8)$.

Equivalently, this is a linear operation, so it can also be described as a matrix-vector product over $GF(2^8)$:
$$
M \left( \begin{array}{c}
x_{0,b} \\
x_{1,b} \\
\vdots \\
x_{N-1,b}  \end{array} \right) = \left( \begin{array}{c}
y_{0,b} \\
y_{1,b} \\
\vdots \\
y_{K-1,b}  \end{array} \right)
$$
![image](https://github.com/solana-foundation/specs/assets/88841339/88db191a-8e0d-400e-88bc-f8b2ff2c3644)



The matrix $M$ depends only on $N$ and $K$.
There are various ways to compute $M$, but one description is

$$
M = \left( \begin{array}{c}
N^0 & N^1 & \cdots & N^{N-1} \\
(N+1)^0 & (N+1)^1 & \cdots & (N+1)^{N-1} \\
\vdots & \vdots  & \ddots & \vdots  \\
(N+K-1)^0 & (N+K-1)^1 & \cdots & (N+K-1)^{N-1}  \end{array} \right) *
\left( \begin{array}{ccccc}
1 & 0 & 0 & \cdots & 0 \\
1^0 & 1^1 & 1^2 & \cdots & 1^{N-1} \\
2^0 & 2^1 & 2^2 & \cdots & 2^{N-1} \\
\vdots & \vdots &  \vdots & \ddots & \vdots  \\
(N-1)^0 & (N-1)^1 & (N-1)^2 &  \cdots & (N-1)^{N-1}  \end{array} \right)^{-1}
$$

where the base and exponent computations are integer arithmetic,
but the exponentiation, matrix inverse, and matrix multiplication are finite field operations.
That is, $M$ is the product of a portion of a Vandermonde matrix with the inverse of another Vandermonde matrix.

## Zero Padding

When the data produced by the shredding process
does not fill the payload field,
additional zero bytes must be inserted after the shred data.
This ensures all data shreds are the same length.

The Reed-Solomon encoding process naturally produces coding shreds of the same size,
so coding shreds do not need zero-padding.

## Signing

### Legacy
When using the legacy authentication method,
the block producer populates the signature field of data shreds and code shreds with the Ed25519 signature of the bytes in the packet that follow the signature field,
including any zero padding.


### Merkle

When using the Merkle authentication method,
the block producer constructs the [canonical Merkle tree](core/merkle-tree.md) from each shred in an FEC set,
with the data shreds in sequence followed by the coding shreds in sequence.
The leaf nodes for both shred types are the bytes
from immediately after the signature field
to immediately before the Merkle proof section.
All hashes are truncated to 20 bytes,
and the last 12 bytes of each SHA256 hash are immediately discarded.

The block producer computes the Ed25519 signature of the root of the Merkle tree
and stores the signature in the signature field of the common header.
Since all packets in the FEC set are part of the same Merkle tree
and thus have the same Merkle root,
all shreds (code and data) in the same FEC set have the same signature in this scheme.

## Merkle Proof

When using Merkle authentication,
the last bytes of the packet contain a Merkle proof that the payload belongs to the Merkle tree covered by the signature field.

Let $h=\lceil \log_2 (N+K) \rceil$ be the height of the Merkle tree for an FEC set
(including the leaf nodes but not the root).
The Merkle proof section is composed of the following:

| Offset        | Size | Type                  | Description                  |
|---------------|-----:|-----------------------|------------------------------|
| end-$20h$-20     | 20B  | Truncated Merkle hash | Root hash of the Merkle tree |
| end-$20h$  | 20B  | Truncated Merkle hash | Merkle hash of sibling leaf node     |
| end-$20h$+20  | 20B  | Truncated Merkle hash | Merkle hash of sibling of parent of leaf node     |
| ... |  ... |  ... |  ... |
| end-20        | 20B  | Truncated Merkle hash | Merkle hash of child of root |

The Merkle proof contains the other information needed to compute the full branch from the leaf in the packet to the root.
For example, in [canonical Merkle tree Figure 2](core/merkle-tree.md#figure_2),
the proof for `L0` contains `Iζ` (root hash) followed by the hash `L1` (sibling leaf node),
`Iβ` and `Iε`.
It does not include `Iα` or `Iδ` as those can be computed from the included information.
The proof for `L3` contains `Iζ`, `L2`, `Iα`, and `Iε`.

Notice that the root hash is treated separately from the rest of the tree and comes first instead of last,
even though the other entries in the proof go from leaf to root.

As described previously, the leaf nodes for both shred types are the bytes
from immediately after the signature field
to immediately before the Merkle proof section.

A compliant implementation must validate that
the signature is a valid signature of the root hash
and that the Merkle tree is consistent among all shreds in the FEC set.
