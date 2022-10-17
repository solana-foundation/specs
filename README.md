# Solana protocol specs

This repository hosts protocol specifications of the Solana network, maintained by various protocol teams.

## Organization

|       Section | Description                             |
|--------------:|-----------------------------------------|
|      *[core]* | Basic concepts and data structures      |
| *[consensus]* | Blockchain consensus rules              |
|   *[runtime]* | On-chain runtime environment (Sealevel) |
|       *[p2p]* | Validator network protocols             |
|       *[api]* | Client-facing node APIs (e.g. JSON-RPC) |

  [core]: ./core/index.md
  [consensus]: ./consensus/index.md
  [runtime]: ./runtime/index.md
  [p2p]: ./p2p/index.md
  [api]: ./api/index.md

## Community

This repo exists to define a single source of truth for consensus-critical sections of the protocol,
such as verification and state transition rules.

The first long-term objective of the specification effort is to produce a complete and unambiguous reference for implementing a Solana validator.

Other documentation regarding widely adopted protocols may be added at the discretion of the Solana Foundation.
