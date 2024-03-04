# Proof-of-History delay function

## Usage

Proof-of-History (PoH) is a recursive SHA-256 hash chain.

## Structure

The state of PoH is sized 256 bits.
The initial state is set to the *seed* value.

The *append* operation sets the state to the SHA-256 hash of itself.

The *mixin* operation sets the state to the SHA-256 hash of the concatenation of itself and an arbitrary 32 byte external input.

## Pseudocode

[poh.py](./poh.py) is a functional Python 3 implementation of PoH.

## Test Vectors

### Solana mainnet block 0

<table>
  <tr>
    <td><strong>Pre State</strong></td>
    <td><code>45296998a6f8e2a784db5d9f95e18fc23f70441a1039446801089879b08c7ef0</code></td>
  </tr>
  <tr>
    <td>Append</td>
    <td>800000x</td>
  </tr>
  <tr>
    <td><strong>Post State</strong></td>
    <td><code>3973e330c29b831f3fcb0e49374ed8d0388f410a23e4ebf23328505036efbd03</code></td>
  </tr>
</table>

### Solana mainnet block 1

<table>
  <tr>
    <td><strong>Pre State</strong></td>
    <td><code>3973e330c29b831f3fcb0e49374ed8d0388f410a23e4ebf23328505036efbd03</code></td>
  </tr>
  <tr>
    <td>Append</td>
    <td>14612x</td>
  </tr>
  <tr>
    <td>Mixin</td>
    <td><code>c95f2f13a9a77f32b1437976c4cffe3029298a49bf37007f8e45d793a520f30b</code></td>
  </tr>
  <tr>
    <td>Append</td>
    <td>210347x</td>
  </tr>
  <tr>
    <td>Mixin</td>
    <td><code>1aaeeb36611f484d984683a3db9269f2292dd9bb81bdab82b28c45625d9abd59</code></td>
  </tr>
  <tr>
    <td>Append</td>
    <td>428775x</td>
  </tr>
  <tr>
    <td>Mixin</td>
    <td><code>db31e861b310f44954403e345b6beeb3ded34084b90694bccaa2345306d366e1</code></td>
  </tr>
  <tr>
    <td>Append</td>
    <td>146263x</td>
  </tr>
  <tr>
    <td><strong>Post State</strong></td>
    <td><code>8ee20607dcf1d9393cf5a2f2c9f7babe167dbdd267491b513c73d2cbf87413f5</code></td>
  </tr>
</table>
