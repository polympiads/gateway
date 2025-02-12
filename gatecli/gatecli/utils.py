from scapy.all import conf, get_if_hwaddr


def find_mac_addresses ():
    default_iface = conf.iface

    return get_if_hwaddr( default_iface )