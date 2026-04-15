from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.arp import arp

log = core.getLogger()

# MAC learning table
mac_to_port = {}

# Broadcast counter per switch
broadcast_count = {}

# Threshold after which broadcast will be blocked
BROADCAST_THRESHOLD = 10


def install_flow(connection, in_port, dst_mac, out_port):
    msg = of.ofp_flow_mod()
    msg.match.in_port = in_port
    msg.match.dl_dst = dst_mac
    msg.actions.append(of.ofp_action_output(port=out_port))
    connection.send(msg)


def install_drop_broadcast(connection):
    msg = of.ofp_flow_mod()
    msg.priority = 100
    msg.match.dl_dst = ethernet.BROADCAST
    # No actions = drop
    connection.send(msg)
    log.info("Installed broadcast DROP rule on switch %s", connection.dpid)


def _handle_PacketIn(event):
    packet = event.parsed
    connection = event.connection
    dpid = connection.dpid
    in_port = event.port

    if dpid not in mac_to_port:
        mac_to_port[dpid] = {}

    if dpid not in broadcast_count:
        broadcast_count[dpid] = 0

    # Learn source MAC
    mac_to_port[dpid][packet.src] = in_port

    # Detect broadcast packets
    if str(packet.dst) == "ff:ff:ff:ff:ff:ff":
        broadcast_count[dpid] += 1
        log.info("Broadcast packet detected on switch %s from %s count=%d",
                 dpid, packet.src, broadcast_count[dpid])

        if broadcast_count[dpid] > BROADCAST_THRESHOLD:
            install_drop_broadcast(connection)
            return

        # Flood normal initial broadcast packets
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        connection.send(msg)
        return

    # Unicast forwarding
    if packet.dst in mac_to_port[dpid]:
        out_port = mac_to_port[dpid][packet.dst]

        # Install flow rule
        install_flow(connection, in_port, packet.dst, out_port)

        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=out_port))
        connection.send(msg)
    else:
        # Unknown destination: flood
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        connection.send(msg)


def launch():
    log.info("Starting Broadcast Traffic Control POX Controller")
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
