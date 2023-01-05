# Repair Service

# Usage

The repair service is used when the primary method of delivering shreds fails to deliver enough shreds to the validator to reconstruct the block. It requests the missing shreds from either a whitelisted set of validators or from all validators in the network.

# Structure

Repair has two parts, the serve repair service and the request repair service.

Serve repair contains the cluster info, bank forks and repair whitelist. A validator can only request shreds for a complete slot which is retrieved from EpochSlots.
EpochSlots contains the stash, a list of all the completed slots for the current epoch. The validator can only request shreds for a slot in the stash.
Every validator open a repair channel and listens for packets using the listen method. The run_listen method conducts some safety checks that include, validating the packet signature, contact info and whitelist. Once it retrives the stake of the request validator from the epoch schedule it decodes the request.
The handle_repair method serializes the request into it's type using the RepairProtocol enum. Based on the shred and slot index it retrieves the shred from the blockstore in the method repair_response_packet and uses the channel to send it back to the validator.
If the validator wants to repair an orphan slot then they send a request for the same and RequestProtocol segregates it into orphan slot repair.

In both types of requests repairs are prioritized by leader fork weight.

The Request repair service is part of the TVU in the shred fetch stage.
