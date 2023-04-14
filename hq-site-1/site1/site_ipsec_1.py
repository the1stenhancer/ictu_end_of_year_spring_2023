import time
import netmiko
import environ


# SETTING UP .env file

env = environ.Env()
environ.Env.read_env()


# GLOBAL NAMING CONVENTION

SITE_NUMBER = "1"

GLOBAL_NAME = "HQ-SITE-{}".format(SITE_NUMBER)


# INITIALIZATION PHASE

SITE_EDGE_ROUTER_PRIVATE_IP = env("SITE_EDGE_ROUTER_PRIVATE_IP")

SITE_ISP_EDGE_ROUTER_PUBLIC_IP = env("SITE_ISP_EDGE_ROUTER_PUBLIC_IP")

EXTENDED_ACL_NAME = GLOBAL_NAME

REMOTE_SITE_PRIVATE_SUBNET = env("REMOTE_SITE_PRIVATE_SUBNET")

REMOTE_SITE_PRIVATE_WC_MASK = env("REMOTE_SITE_PRIVATE_WC_MASK")

HQ_PRIVATE_SUBNET = env("HQ_PRIVATE_SUBNET")

HQ_PRIVATE_WC_MASK = env("HQ_PRIVATE_WC_MASK")


# IKE PHASE 1: ISAKMP

ISAKMP_POLICY_NUMBER = SITE_NUMBER

ISAKMP_ENCRYPTION_ALGORITHM = env("ISAKMP_ENCRYPTION_ALGORITHM")

ISAKMP_HASH_ALGORITHM = env("ISAKMP_HASH_ALGORITHM")

ISAKMP_DH_GROUP = env("ISAKMP_DH_GROUP")

ISAKMP_LIFETIME = "86400"

ISAKMP_AUTHENTICATION_METHOD = "pre-share"

ISAKMP_AUTHENTICATION_KEY = env("AUTHENTICATION_PRESHARE_KEY")

ISAKMP_PEER_PUBLIC_IP = env("ISAKMP_PEER_PUBLIC_IP")


# IKE PHASE 2: IPSEC

IPSEC_TRANSFORM_SET_NAME = GLOBAL_NAME

IPSEC_ENCRYPTION_ALGORITHM = env("IPSEC_ENCRYPTION_ALGORITHM")

IPSEC_KEYED_HASH_ALGORITHM = env("IPSEC_KEYED_HASH_ALGORITHM")


# CRYPTO MAP

MAP_NAME = GLOBAL_NAME

MAP_NUMBER = SITE_NUMBER

SITE_EDGE_ROUTER_PUBLIC_INTERFACE = env("SITE_EDGE_ROUTER_PUBLIC_INTERFACE")


# NAT

ACL_LIST_NUMBER = 100


# PING TEST

PING_SOURCE_ADDRESS = env("PING_SOURCE_ADDRESS")

PING_DESTINATION_ADDRESS = env("PING_DESTINATION_ADDRESS")


# SSH PARAMETERS

SITE_PARAMETERS = {
    'device_type': 'cisco_ios',
    'ip': SITE_EDGE_ROUTER_PRIVATE_IP,
    'username': env("USERNAME"),
    'password': env("PASSWORD"),
    'port': 22,
    'secret': env("ENABLE_SECRET"),
}

if __name__ == "__main__":

    # INITIALIZATION

    print("[ + ] Initialization starting...")
    time.sleep(1)
    print("[ + ] Creating SSH connection on port 22 to SITE {} internet edge router...".format(SITE_NUMBER))
    time.sleep(1)
    connection = netmiko.ConnectHandler(**SITE_PARAMETERS)
    
    print("[ + ] Connection established.")
    time.sleep(1)
    print("[ + ] Entering enable mode...")
    time.sleep(1)
    connection.enable()

    time.sleep(1)
    print("[ + ] In enable mode")

    time.sleep(1)
    print("\n[ + ] INITIALIZATION PHASE")
    time.sleep(1)
    print("[ + ] Entering global configuration mode...")
    time.sleep(1)
    print("[ + ] In global configuration mode.")
    time.sleep(1)
    print("[ + ] Setting default route for outbound packets...")
    time.sleep(1)
    connection.send_config_set("ip route 0.0.0.0 0.0.0.0 {}".format(SITE_ISP_EDGE_ROUTER_PUBLIC_IP))
    time.sleep(1)

    print("[ + ] Done")
    time.sleep(1)
    print("[ + ] Setting up extended ACL for interesting traffic...")
    time.sleep(1)
    acl = [
        "ip access-list extended {}".format(EXTENDED_ACL_NAME),
        "permit ip {} {} {} {}".format(
            REMOTE_SITE_PRIVATE_SUBNET,
            REMOTE_SITE_PRIVATE_WC_MASK,
            HQ_PRIVATE_SUBNET,
            HQ_PRIVATE_WC_MASK
        )
    ]
    
    connection.send_config_set(acl)
    time.sleep(1)
    print("[ + ] Done")
    time.sleep(1)

    # adding NAT settings to see

    print("[ + ] Setting up extended ACL for NAT...")
    nat = [
        "ip nat inside source list {} interface {} overload".format(
            ACL_LIST_NUMBER,
            SITE_EDGE_ROUTER_PUBLIC_INTERFACE
        ),
        "access-list {} deny ip {} {} {} {}".format(
            ACL_LIST_NUMBER,
            REMOTE_SITE_PRIVATE_SUBNET,
            REMOTE_SITE_PRIVATE_WC_MASK,
            HQ_PRIVATE_SUBNET,
            HQ_PRIVATE_WC_MASK
        ),
        "access-list {} permit {} {} any".format(
            ACL_LIST_NUMBER,
            REMOTE_SITE_PRIVATE_SUBNET,
            REMOTE_SITE_PRIVATE_WC_MASK
        )
    ]

    connection.send_config_set(nat)
    time.sleep(1)

    print("[ + ] Done")
    time.sleep(1)
    print("[ + ] INITIALIZATION PHASE complete!")
    time.sleep(1)

    # PHASE 1

    print("\n[ + ] IKE PHASE 1 (ISAKMP) starting...")
    time.sleep(1)
    print("[ + ] Creating ISAKMP POLICY for IPSEC VPN establishment with HQ...")
    time.sleep(1)
    print("[ + ] Setting IKE PHASE 1 encryption algorithm for exchanging keying material...")
    time.sleep(1)
    print("[ + ] Setting IKE PHASE 1 hash algorithm for exchanging keying material...")
    time.sleep(1)
    print("[ + ] Setting IKE PHASE 1 Diffie-Hellman group for exchanging keying material...")
    time.sleep(1)
    print("[ + ] Setting IKE PHASE 1 authentication method for exchanging keying material...")
    time.sleep(1)
    print("[ + ] Setting IKE PHASE 1 lifetime for security association...")
    phase_1 = [
        "crypto isakmp policy {}".format(ISAKMP_POLICY_NUMBER),
        "encryption {}".format(ISAKMP_ENCRYPTION_ALGORITHM),
        "hash {}".format(ISAKMP_HASH_ALGORITHM),
        "group {}".format(ISAKMP_DH_GROUP),
        "authentication {}".format(ISAKMP_AUTHENTICATION_METHOD),
        "lifetime {}".format(ISAKMP_LIFETIME)
    ]

    connection.send_config_set(phase_1)
    time.sleep(1)

    print("[ + ] Setting authentication key to use to authenticate HQ peer...")
    connection.send_config_set("crypto isakmp key {} address {}".format(
        ISAKMP_AUTHENTICATION_KEY,
        ISAKMP_PEER_PUBLIC_IP
    ))
    time.sleep(1)
    print("[ + ] Done")
    time.sleep(1)
    print("[ + ] IKE PHASE 1 complete!")
    time.sleep(1)

    # PHASE 2

    print("\n[ + ] IKE PHASE 2 (IPSEC) starting...")
    time.sleep(1)
    print("[ + ] Setting transform-set to use for exchanging data...")
    time.sleep(1)
    connection.send_config_set("crypto ipsec transform-set {} {} {}".format(
        IPSEC_TRANSFORM_SET_NAME,
        IPSEC_ENCRYPTION_ALGORITHM,
        IPSEC_KEYED_HASH_ALGORITHM
    ))
    print("[ + ] Done")
    time.sleep(1)
    print("[ + ] IKE PHASE 2 complete!")
    time.sleep(1)

    # PHASE 3

    print("\n[ + ] Linking IKE PHASE 1 and PHASE 2 starting...")
    time.sleep(1)
    print("[ + ] Creating crypto map ipsec-isakmp...")
    time.sleep(1)
    print("[ + ] Setting peer...")
    time.sleep(1)
    print("[ + ] Setting pfs...")
    time.sleep(1)
    print("[ + ] Setting security-association lifetime...")
    time.sleep(1)
    print("[ + ] Setting transform-set...")
    time.sleep(1)
    print("[ + ] Setting extended ACL to use...")
    time.sleep(1)

    map = [
        "crypto map {} {} ipsec-isakmp".format(
            MAP_NAME,
            MAP_NUMBER
        ),
        "set peer {}".format(ISAKMP_PEER_PUBLIC_IP),
        "set pfs {}".format(ISAKMP_DH_GROUP),
        "set security-association lifetime seconds {}".format(ISAKMP_LIFETIME),
        "set transform-set {}".format(IPSEC_TRANSFORM_SET_NAME),
        "match address {}".format(EXTENDED_ACL_NAME)
    ]
    connection.send_config_set(map)

    print("[ + ] LINKING IKE PHASE 1 and PHASE 2 done.")
    time.sleep(1)

    # ADDING MAP TO HQ EDGE ROUTER'S PUBLIC INTERFACE

    print("[ + ] Attaching crypto map to HQ Edge router public interface...")
    attach_map = [
        "interface {}".format(SITE_EDGE_ROUTER_PUBLIC_INTERFACE),
        "crypto map {}".format(MAP_NAME)
    ]
    connection.send_config_set(attach_map)
    time.sleep(2)
    print("\n[ + ] IPSEC VPN configurations successfully added to SITE {} edge router.".format(SITE_NUMBER))

    time.sleep(1)
    print("\n[ - ] Test IPSEC VPN connection with HQ using PING")
    time.sleep(1)
    print("[ - ] Running ping...")

    ping_result = connection.send_command(
        command_string="ping ip {} source {}".format(
            PING_DESTINATION_ADDRESS,
            PING_SOURCE_ADDRESS
        ),
        read_timeout=60
    )
    print("\nPING RESULT:\n{}\n".format(ping_result))

