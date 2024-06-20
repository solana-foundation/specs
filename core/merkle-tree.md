# Binary Merkle Tree

## Usage

The binary hash tree facilitates equality checks over a list of arbitrary data blobs.

Each tree anchors in a 32 byte *root hash* which is constructed by recursively hashing pairs of two tree nodes into one.

Merkle proofs, which equate arbitrary data against entries in the tree, are of succinct size irrespective of the input data.

## Structure

- Each tree node is identified by a SHA-256 hash.
- Two types of nodes exist: *Leaf* and *intermediate* nodes.
  - The pre-image of a *leaf node* is the byte `0x00` followed by an arbitrary amount of data.
  - The pre-image of an *intermediate node* is the byte `0x01` followed by two 32 byte hashes, each referring to a node.
- Each node has one or zero parent intermediate nodes.
  - Referring to the same node twice in the same intermediate node is permitted.
- The graph of nodes represents a binary tree, thus is acyclic and has one *root node*.

## Algorithms

### Leaf Order

The *leaf order* of a tree is defined by depth-first search traversal starting at the root,
counting only leaf nodes.

**Example**

The leaf order of the tree in _figure 1_ is `[Lβ, Lα, Lδ]`.

<a id="figure_1"></a>

```
Figure 1: Non-canonical tree with three leaf nodes and two intermediate nodes

     Iε
    /  \
   Iγ  Lδ
  /  \
 Lβ  Lα
```

### Level Order

The *level order* of a tree is defined by depth-first search starting at the root,
counting only nodes with a given level.

**Example**

The tree in [_figure 1_](#figure_1) has the following level orders:
 - `0: [Iε]`
 - `1: [Iγ, Lδ]`
 - `2: [Lβ, Lα]`

### Canonical Construction

The construction algorithm deterministically creates a tree structure over a list of items.

Determinism ensures that independently constructed trees over the same items are identical.
This is required for equality and membership checks.

The *canonical* tree layout for any arbitrary list of items is defined by the following invariants:
- Each list item corresponds to one leaf node.
- The ordering of list items matches the order of leaf nodes.
- Each leaf node is in the deepest tree level.
- For any level `l` with number of nodes `n(l)`, if `n(l) % 2 == 1 and n(l) > 1`,
  then the last node in level `l-1` is an intermediate node that contains the hash of the last node in `l` twice.

**Example**

_Figure 2_ shows the canonical construction of items `[L0, L1, L2, L3, L4]`.

<a id="figure_2"></a>

```
Figure 2: Canonical tree with 5 items

          Iζ
         /  \
        /    \
       Iδ     Iε
      /  \     \\
     /    \     \\
   Iα      Iβ    Iγ
  /  \    /  \   ||
 L0  L1  L2  L3  L4
```

Contents of nodes:

- `L0 := sha256(concat(0x00, data[0]))`
- `L1 := sha256(concat(0x00, data[1]))`
- `L2 := sha256(concat(0x00, data[2]))`
- `L3 := sha256(concat(0x00, data[3]))`
- `L4 := sha256(concat(0x00, data[4]))`
- `Iα := sha256(concat(0x01, L0, L1))`
- `Iβ := sha256(concat(0x01, L2, L3))`
- `Iγ := sha256(concat(0x01, L4, L4))`
- `Iδ := sha256(concat(0x01, Iα, Iβ))`
- `Iε := sha256(concat(0x01, Iγ, Iγ))`
- `Iζ := sha256(concat(0x01, Iδ, Iε))`

### List Equality Check

Checking the equality of two merkle trees is trivial: Comparing the hash of the roots of either tree.

## Security

No practical collision attacks against SHA-256 are known as of Oct 2022.

Collision resistance is vital to ensure that the graph of nodes remains acyclic and that each hash unambiguously refers to one logical node.

## Test Vectors

<table>
  <caption>Canonical root test vectors</caption>
  <thead>
    <tr>
      <th>Items (UTF-8)</th>
      <th>Root Hash (Hex)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>['test']</code></td>
      <td><code>dbebd10e61bc8c28591273feafbbef95d544f874693301d8f7f8e54c6e30058e</code></td>
    </tr>
    <tr>
      <td><code>['my', 'very', 'eager', 'mother', 'just, 'served', 'us', 'nine', 'pizzas', 'make', 'prime']</code></td>
      <td><code>b40c847546fdceea166f927fc46c5ca33c3638236a36275c1346d3dffb84e1bc</code></td>
    </tr>
  </tbody>
</table>
