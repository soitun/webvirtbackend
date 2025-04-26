import random
from ipaddress import IPv4Network, IPv6Network, ip_address

from virtance.models import Virtance

from .models import IPAddress, Network

# First is a gateway and 2 lasts are reserved for broadcast and system needs
SUBNET_V4_RANGE = slice(2, -2)


def assign_free_ipv4_compute(virtance_id):
    virtance = Virtance.objects.get(id=virtance_id)
    virtances = Virtance.objects.filter(compute=virtance.compute, is_deleted=False)
    network = Network.objects.get(
        region=virtance.region, version=Network.IPv4, type=Network.COMPUTE, is_active=True, is_deleted=False
    )
    assigned_ipv4_compute = IPAddress.objects.filter(network=network, virtance__in=virtances)
    ipaddrs = list(IPv4Network(f"{network.cidr}/{network.netmask}"))[SUBNET_V4_RANGE]
    for ipaddr in random.sample(ipaddrs, k=len(ipaddrs)):
        if str(ipaddr) not in [ip.address for ip in assigned_ipv4_compute]:
            ipaddr = IPAddress.objects.create(network=network, address=str(ipaddr), virtance=virtance)
            return ipaddr.id
    return None


def assign_free_ipv4_public(virtance_id, is_float=False):
    virtance = Virtance.objects.get(id=virtance_id)
    networks = Network.objects.filter(
        region=virtance.region, version=Network.IPv4, type=Network.PUBLIC, is_active=True, is_deleted=False
    )
    for net in networks:
        ipaddrs = list(IPv4Network(f"{net.cidr}/{net.netmask}"))[SUBNET_V4_RANGE]
        for ipaddr in random.sample(ipaddrs, k=len(ipaddrs)):
            if not IPAddress.objects.filter(network=net, address=str(ipaddr)).exists():
                ipaddr = IPAddress.objects.create(
                    network=net, address=str(ipaddr), virtance=virtance, is_float=is_float
                )
                return ipaddr.id
    return None


def assign_free_ipv4_private(virtance_id):
    virtance = Virtance.objects.get(id=virtance_id)
    networks = Network.objects.filter(
        region=virtance.region, version=Network.IPv4, type=Network.PRIVATE, is_active=True, is_deleted=False
    )
    for net in networks:
        ipaddrs = list(IPv4Network(f"{net.cidr}/{net.netmask}"))[SUBNET_V4_RANGE]
        for ipaddr in random.sample(ipaddrs, k=len(ipaddrs)):
            if not IPAddress.objects.filter(network=net, address=str(ipaddr)).exists():
                ipaddr = IPAddress.objects.create(network=net, address=str(ipaddr), virtance=virtance)
                return ipaddr.id
    return None


def assign_free_ipv6_public(virtance_id):
    virtance = Virtance.objects.get(id=virtance_id)
    networks = Network.objects.filter(
        region=virtance.region, version=Network.IPv6, type=Network.PUBLIC, is_active=True, is_deleted=False
    )
    for net in networks:
        step = 16
        nums = 2**step
        subnet = IPv6Network(f"{net.cidr}/{net.netmask}")
        start = int(subnet.network_address) + step
        end = int(subnet.broadcast_address) + 1
        limit = nums if nums < end else end - 1  # Check if limit is greater than end
        for i in random.sample(range(start, end, step), k=limit):
            if not IPAddress.objects.filter(network=net, address=str(ip_address(i))).exists():
                ipaddr = IPAddress.objects.create(network=net, address=str(ip_address(i)), virtance=virtance)
                return ipaddr.id
    return None
