# Solana protocol specs

This repository hosts protocol specifications of the Solana network, maintained by various protocol teams.

## Organization

|       Section | Description                             |
|--------------:|-----------------------------------------|
|      *[core]* | Basic concepts and data structures      |
|    *[gossip]* | Protocol for network communication      |
| *[consensus]* | Blockchain consensus rules              |
|   *[runtime]* | On-chain runtime environment (Sealevel) |
|       *[p2p]* | Validator network protocols             |
|       *[api]* | Client-facing node APIs (e.g. JSON-RPC) |

  [core]: ./core/
  [consensus]: ./consensus/
  [runtime]: ./runtime/
  [p2p]: ./p2p/
  [api]: ./api/
  [gossip]: ./gossip/

## Community

This repo exists to define a single source of truth for consensus-critical sections of the protocol,
such as verification and state transition rules.

The first long-term objective of the specification effort is to produce a complete and unambiguous reference for implementing a Solana validator.

Other documentation regarding widely adopted protocols may be added at the discretion of the Solana Foundation.

## Reference Code

The `solana_specs` module contains Python 3.10 implementations of various specs.

Each unit is runnable as a test, like so:

```
python3.10 -m solana_specs.consensus.leader_schedule
```

The reference code is formatted using [black](https://black.readthedocs.io/en/stable/).

Certain tests depend on test fixtures which are hosted on [Git LFS](https://git-lfs.com/).
To download test fixtures, run:

```shell
git lfs pull
```
