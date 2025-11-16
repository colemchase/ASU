from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import EventMixin
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr, IPAddr
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.arp import arp
from pox.lib import packet as pkt

log = core.getLogger()


class L3Firewall(EventMixin):

    def __init__(self):
        self.listenTo(core.openflow)

        # Only allow these four MAC addresses (h1 to h4)
        self.allowed_macs = set([
            EthAddr("00:00:00:00:00:01"),
            EthAddr("00:00:00:00:00:02"),
            EthAddr("00:00:00:00:00:03"),
            EthAddr("00:00:00:00:00:04"),
        ])

        # Port table from pseudocode
        # key is MAC string, value is IP string
        self.port_table = {}

        # Keep track of MACs we already blocked
        self.blocked_macs = set()

        self.drop_priority = 60000

        log.info("Port security L3 firewall loaded")

    def _handle_ConnectionUp(self, event):
        log.info("Switch %s connected", dpidToStr(event.dpid))

    def install_drop(self, event, mac):
        if mac in self.blocked_macs:
            return

        self.blocked_macs.add(mac)
        log.warn("Installing drop rule for MAC %s", mac)

        msg = of.ofp_flow_mod()
        msg.priority = self.drop_priority
        match = of.ofp_match()
        match.dl_src = mac
        msg.match = match
        # no actions means drop
        event.connection.send(msg)

    def handle_port_security(self, event, mac, ip):
        # Block anything that is not one of the four lab hosts
        if mac not in self.allowed_macs:
            log.warn("Unknown MAC %s seen block it", mac)
            self.install_drop(event, mac)
            return False

        mac_s = str(mac)
        ip_s = str(ip)

        # New MAC (first time)
        if mac_s not in self.port_table:
            self.port_table[mac_s] = ip_s
            log.info("Learned binding MAC %s with IP %s", mac_s, ip_s)
            return True

        # Seen before with same IP
        if self.port_table[mac_s] == ip_s:
            return True

        # Spoofing: same MAC now using different IP
        expected = self.port_table[mac_s]
        log.warn("IP spoof from MAC %s using IP %s expected %s",
                 mac_s, ip_s, expected)
        self.install_drop(event, mac)
        return False

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet:
            return

        src_mac = packet.src
        src_ip = None

        # ARP packet
        if packet.type == ethernet.ARP_TYPE and isinstance(packet.payload, arp):
            src_ip = packet.payload.protosrc

        # IPv4 packet
        elif packet.type == ethernet.IP_TYPE and isinstance(packet.next, pkt.ipv4):
            src_ip = packet.next.srcip

        else:
            # ignore other protocols for this lab
            return

        # Apply port security rules
        if not self.handle_port_security(event, src_mac, src_ip):
            # spoof or unknown MAC do not forward this packet
            return

        # Legit packet: just flood it out, do not install NORMAL flow
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        event.connection.send(msg)


def launch():
    core.registerNew(L3Firewall)



