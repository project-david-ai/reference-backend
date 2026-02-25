import json
import os
import sys

from dotenv import load_dotenv
from projectdavid import Entity

# ------------------------------------------------------------------
# 0. SDK Init & Environment Setup
# ------------------------------------------------------------------
load_dotenv()

client = Entity(
    base_url=os.getenv("BASE_URL", "http://localhost:9000/v1"),
    api_key=os.getenv("ENTITIES_API_KEY"),
)

# ------------------------------------------------------------------
# 1. Define the Network Topology — GNS3 Lab (3x Cisco IOS 15.2)
#
# Topology:
#   R1 (192.168.100.1) ── Fa0/0 10.0.12.0/30 ── R2 (192.168.100.2)
#   R1 (192.168.100.1) ── Fa2/0 10.0.13.0/30 ── R3 (192.168.100.3)
#   R2 (192.168.100.2) ── Fa2/0 10.0.23.0/30 ── R3 (192.168.100.3)
#   All routers in OSPF area 0, process 1.
# ------------------------------------------------------------------
network_inventory = [
    {
        "host_name": "R1",
        "ip_address": "localhost",
        "port": 5000,
        "platform": "cisco_ios_telnet",
        "groups": ["core", "lab", "ospf"],
        "site": "GNS3 Lab",
        "role": "Core Router",
        "interfaces": {
            "Loopback0": "192.168.100.1/32",
            "FastEthernet0/0": "10.0.12.1/30",
            "FastEthernet2/0": "10.0.13.1/30",
        },
        "ospf": {
            "process_id": 1,
            "router_id": "192.168.100.1",
            "area": 0,
            "neighbors": ["192.168.100.2", "192.168.100.3"],
        },
    },
    {
        "host_name": "R2",
        "ip_address": "localhost",
        "port": 5001,
        "platform": "cisco_ios_telnet",
        "groups": ["core", "lab", "ospf"],
        "site": "GNS3 Lab",
        "role": "Core Router",
        "interfaces": {
            "Loopback0": "192.168.100.2/32",
            "FastEthernet0/0": "10.0.12.2/30",
            "FastEthernet2/0": "10.0.23.1/30",
        },
        "ospf": {
            "process_id": 1,
            "router_id": "192.168.100.2",
            "area": 0,
            "neighbors": ["192.168.100.1", "192.168.100.3"],
        },
    },
    {
        "host_name": "R3",
        "ip_address": "localhost",
        "port": 5002,
        "platform": "cisco_ios_telnet",
        "groups": ["core", "lab", "ospf"],
        "site": "GNS3 Lab",
        "role": "Core Router",
        "interfaces": {
            "Loopback0": "192.168.100.3/32",
            "FastEthernet0/0": "10.0.13.2/30",
            "FastEthernet2/0": "10.0.23.2/30",
        },
        "ospf": {
            "process_id": 1,
            "router_id": "192.168.100.3",
            "area": 0,
            "neighbors": ["192.168.100.1", "192.168.100.2"],
        },
    },
]


# ------------------------------------------------------------------
# 2. Ingest Inventory
# ------------------------------------------------------------------
def ingest():
    print(f"🚀 Uploading {len(network_inventory)} GNS3 lab devices to The Engineer...")
    try:
        response = client.engineer.ingest_inventory(
            devices=network_inventory,
            clear_existing=True,
        )
        print("\n✅ Inventory uploaded successfully.")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"\n❌ Failed to ingest inventory: {e}")


# ------------------------------------------------------------------
# 3. Manual Device Lookup
# ------------------------------------------------------------------
def lookup_device(hostname: str):
    print(f"\n🔍 Looking up device: '{hostname}'...")
    try:
        result = client.engineer.get_device_info(hostname=hostname)
        if result:
            print("✅ Device found:")
            print(json.dumps(result, indent=2))
        else:
            print(f"⚠️  No device found with hostname '{hostname}'.")
    except Exception as e:
        print(f"❌ Lookup failed: {e}")


# ------------------------------------------------------------------
# 4. Manual Group Search
# ------------------------------------------------------------------
def lookup_group(group: str):
    print(f"\n🔍 Searching inventory for group: '{group}'...")
    try:
        results = client.engineer.search_inventory_by_group(group=group)
        if results:
            print(f"✅ Found {len(results)} device(s) in group '{group}':")
            print(json.dumps(results, indent=2))
        else:
            print(f"⚠️  No devices found in group '{group}'.")
    except Exception as e:
        print(f"❌ Group search failed: {e}")


# ------------------------------------------------------------------
# 5. Entrypoint — CLI dispatch
# ------------------------------------------------------------------
if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] == "ingest":
        ingest()
        lookup_device("R1")
        lookup_device("R2")
        lookup_device("R3")
        lookup_group("core")
        lookup_group("ospf")

    elif args[0] == "device" and len(args) == 2:
        lookup_device(args[1])

    elif args[0] == "group" and len(args) == 2:
        lookup_group(args[1])

    else:
        print("Usage:")
        print(
            "  python script.py ingest                  # Upload GNS3 inventory + run test searches"
        )
        print("  python script.py device <hostname>       # Look up a specific device")
        print("  python script.py group  <group_name>     # Search by group")
