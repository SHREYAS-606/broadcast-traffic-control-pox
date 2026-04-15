# Broadcast Traffic Control using SDN, Mininet, and POX

## Problem Statement
This project implements Broadcast Traffic Control in an SDN-based network using Mininet and the POX controller. The objective is to detect excessive broadcast packets, limit flooding, and install selective flow rules to improve network behavior.

## Objective
- Demonstrate controller-switch interaction
- Handle PacketIn events
- Implement explicit OpenFlow flow rules
- Detect broadcast traffic
- Block excessive broadcast traffic
- Observe network behavior using ping, iperf, and flow tables

## Tools Used
- WSL Ubuntu
- Mininet
- Open vSwitch
- POX Controller
- GitHub

## Topology
- 1 switch: s1
- 3 hosts: h1, h2, h3

## Files
- `broadcast_control.py` : POX controller logic
- `topo.py` : custom Mininet topology
- `README.md` : documentation

## Setup Steps

### Start POX
```bash
cd ~/pox
python3 pox.py log.level --DEBUG openflow.of_01 forwarding.broadcast_control
