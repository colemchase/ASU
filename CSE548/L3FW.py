from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr, IPAddr
import pox.lib.packet as pkt
from pox.lib.packet.arp import arp
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.ethernet import ethernet

log = core.getLogger()


class L3Firewall(EventMixin):

    def __init__(self):
        self.listenTo(core.openflow)

        # Port security tables
        self.mac_ip_table = {}      # MAC to IP
        self.mac_port_table = {}    # MAC to switch port
        self.ip_mac_table = {}      # IP to MAC

        self.drop_priority = 60000

        log.info("Enhanced L3 Firewall with Port Security Loaded.")

    # -------------------------
    # ARP reply
    # -------------------------
    def replyToARP(self, packet, match, event):
        r = arp()
        r.opcode = arp.REPLY
        r.hwdst = match.dl_src
        r.hwsrc = match.dl_dst
        r.protosrc = match.nw_dst
        r.protodst = match.nw_src

        e = ethernet(type=packet.ARP_TYPE, src=r.hwsrc, dst=r.hwdst)
        e.set_payload(r)

        msg = of.ofp_packet_out()
        msg.data = e.pack()
        msg.actions.append(of.ofp_action_output(port=event.port))
        msg.in_port = event.port
        event.connection.send(msg)

    # -------------------------
    # Allow normal traffic
    # -------------------------
    def allowOther(self, event):
        msg = of.ofp_flow_mod()
        msg.priority = 1
        msg.actions.append(of.ofp_action_output(port=of.OFPP_NORMAL))
        event.connection.send(msg)

    # -------------------------
    # Drop a spoofing MAC
    # -------------------------
    def block_mac(self, event, mac):
        log.warn("Installing DROP rule for MAC %s (spoofing detected)", mac)

        msg = of.ofp_flow_mod()
        msg.priority = self.drop_priority
        msg.match = of.ofp_match(dl_src=EthAddr(mac))
        # empty actions = drop
        event.connection.send(msg)

    # -------------------------
    # PacketIn Handler
    # -------------------------
    def _handle_PacketIn(self, event):
        packet = event.parsed
        match = of.ofp_match.from_packet(packet)
        inport = event.port

        # ---------------- ARP ----------------
        if match.dl_type == packet.ARP_TYPE and packet.payload.opcode == arp.REQUEST:
            self.replyToARP(packet, match, event)
            return

        # ---------------- IP ----------------
        if match.dl_type == packet.IP_TYPE:
            src_mac = str(match.dl_src)
            src_ip = str(match.nw_src)

            # 1. MAC must stay on the same port (MAC spoof or MAC move)
            if src_mac not in self.mac_port_table:
                self.mac_port_table[src_mac] = inport
            elif self.mac_port_table[src_mac] != inport:
                log.warn("MAC MOVE DETECTED: MAC %s on port %d (expected %d)",
                         src_mac, inport, self.mac_port_table[src_mac])
                self.block_mac(event, src_mac)
                return

            # 2. MAC must not change its IP (IP spoofing)
            if src_mac not in self.mac_ip_table:
                self.mac_ip_table[src_mac] = src_ip
            elif self.mac_ip_table[src_mac] != src_ip:
                exp_ip = self.mac_ip_table[src_mac]
                log.warn("IP SPOOF DETECTED: MAC %s sent %s (expected %s)",
                         src_mac, src_ip, exp_ip)
                self.block_mac(event, src_mac)
                return

            # 3. IP must not change its MAC (MAC spoofing)
            if src_ip not in self.ip_mac_table:
                self.ip_mac_table[src_ip] = src_mac
            elif self.ip_mac_table[src_ip] != src_mac:
                exp_mac = self.ip_mac_table[src_ip]
                log.warn("MAC SPOOF DETECTED: IP %s from MAC %s (expected %s)",
                         src_ip, src_mac, exp_mac)
                self.block_mac(event, src_mac)
                return

        # Allow other traffic
        self.allowOther(event)

    # -------------------------
    # Switch Up
    # -------------------------
    def _handle_ConnectionUp(self, event):
        log.info("Switch %s connected. Enhanced L3 Firewall Active.",
                 dpidToStr(event.dpid))


def launch():
    core.registerNew(L3Firewall)



