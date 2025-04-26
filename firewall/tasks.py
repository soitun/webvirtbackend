from compute.webvirt import WebVirtCompute
from network.models import IPAddress, Network
from virtance.models import Virtance
from virtance.utils import virtance_error
from webvirtcloud.celery import app

from .models import Cidr, Firewall, FirewallVirtance, Rule
from .utils import firewall_error


@app.task
def firewall_attach(firewall_id, virtance_id, virtance_reset_event=True):
    inbound_rules = []
    outbound_rules = []
    virtance = Virtance.objects.get(id=virtance_id)
    firewall = Firewall.objects.get(id=firewall_id)
    firewall_rules = Rule.objects.filter(firewall=firewall)
    ipv4_public = IPAddress.objects.filter(virtance=virtance, network__type=Network.PUBLIC, is_float=False).first()
    ipv4_private = IPAddress.objects.filter(virtance=virtance, network__type=Network.PRIVATE).first()

    for rule in firewall_rules:
        cidrs = Cidr.objects.filter(rule=rule)
        if rule.direction == Rule.INBOUND:
            inbound_rules.append(
                {
                    "protocol": rule.protocol,
                    "action": rule.action,
                    "ports": rule.ports,
                    "addresses": [f"{i.address}/{i.prefix}" for i in cidrs],
                }
            )
        if rule.direction == Rule.OUTBOUND:
            outbound_rules.append(
                {
                    "protocol": rule.protocol,
                    "action": rule.action,
                    "ports": rule.ports,
                    "addresses": [f"{i.address}/{i.prefix}" for i in cidrs],
                }
            )

    wvcomp = WebVirtCompute(virtance.compute.token, virtance.compute.hostname)
    res = wvcomp.firewall_attach(firewall.id, ipv4_public.address, ipv4_private.address, inbound_rules, outbound_rules)
    if isinstance(res, dict) and res.get("detail"):
        firewall_error(firewall_id, res.get("detail"), "firewall_attach")
        virtance_error(virtance_id, res.get("detail"), "firewall_attach")
    else:
        if virtance_reset_event is True:
            virtance.reset_event()
        firewall.reset_event()


@app.task
def firewall_detach(firewall_id, virtance_id, virtance_reset_event=True, unlink_db=True):
    virtance = Virtance.objects.get(id=virtance_id)
    firewall = Firewall.objects.get(id=firewall_id)
    ipv4_public = IPAddress.objects.filter(virtance=virtance, network__type=Network.PUBLIC, is_float=False).first()
    ipv4_private = IPAddress.objects.filter(virtance=virtance, network__type=Network.PRIVATE).first()

    wvcomp = WebVirtCompute(virtance.compute.token, virtance.compute.hostname)
    res = wvcomp.firewall_detach(firewall.id, ipv4_public.address, ipv4_private.address)
    if isinstance(res, dict) and res.get("detail"):
        firewall_error(firewall_id, res.get("detail"), "firewall_detach")
        virtance_error(virtance_id, res.get("detail"), "firewall_detach")
    else:
        if unlink_db is True:
            FirewallVirtance.objects.filter(firewall=firewall, virtance=virtance).delete()
        if virtance_reset_event is True:
            virtance.reset_event()
        firewall.reset_event()


@app.task
def firewall_update(firewall_id, virtance_id):
    # Detach firewall first
    firewall_detach(firewall_id, virtance_id, virtance_reset_event=False, unlink_db=False)

    # Attach firewall with new rules
    firewall_attach(firewall_id, virtance_id)
