import ldap3
import socket

# LDAP Configuration
LDAP_SERVER = '10.1.0.4'
LDAP_PORT = 389
LDAPS_PORT = 636  # Standard SSL port for LDAP
BASE_DN = 'dc=baylor,dc=local'
LDAP_TIMEOUT = 5

BIND_DN = "Baylor\\forms"  # Using 'forms' as the BIND_DN
BIND_PASSWORD = "GeroWhat12345!"  # In production, use environment variables


def test_network_connectivity(port):
    try:
        socket.create_connection((LDAP_SERVER, port), timeout=LDAP_TIMEOUT)
        print(f"Successfully connected to {LDAP_SERVER}:{port}")
        return True
    except Exception as e:
        print(f"Failed to connect to {LDAP_SERVER}:{port}. Error: {e}")
        return False


def test_ldap_connection(search_attribute, search_value, use_ssl=False):
    port = LDAPS_PORT if use_ssl else LDAP_PORT
    if not test_network_connectivity(port):
        return False

    server = ldap3.Server(LDAP_SERVER, port=port,
                          use_ssl=use_ssl, get_info=ldap3.ALL)
    try:
        conn = ldap3.Connection(server, user=BIND_DN,
                                password=BIND_PASSWORD, auto_bind=True)
        print(
            f"Successfully connected to the LDAP server {'with SSL' if use_ssl else 'without SSL'}")

        # Create the search filter based on the attribute and value provided
        search_filter = f"({search_attribute}={search_value})"
        conn.search(BASE_DN, search_filter, attributes=['cn', 'sn', 'mail'])

        if len(conn.entries) > 0:
            print(f"Successfully retrieved {len(conn.entries)} entries.")
            print("First entry details:")
            print(conn.entries[0])
        else:
            print(
                "No entries found. This could be due to search permissions or an empty result set.")

        conn.unbind()
        return True
    except ldap3.core.exceptions.LDAPException as e:
        print(
            f"Failed to connect {'with SSL' if use_ssl else 'without SSL'}. Error: {e}")
        return False


if __name__ == "__main__":
    search_attribute = input(
        "Enter the attribute to search by (sAMAccountName or mail): ")
    search_value = input(f"Enter the value for {search_attribute}: ")

    print("Attempting non-SSL connection:")
    if not test_ldap_connection(search_attribute, search_value):
        print("\nAttempting SSL connection:")
        test_ldap_connection(search_attribute, search_value, use_ssl=True)
