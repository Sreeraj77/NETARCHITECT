from ai.intent_extractor import extract_intent
from ai.network_planner import generate_network_plan


user_input = """
Design a secure college network for 500 users across 5 departments: CSE, ECE, EEE, ME, and CE. The college has 3 buildings. Create separate VLANs for each department, provide Wi-Fi connectivity, CCTV, VoIP, DHCP, DNS, and Internet access. Use OSPF as the routing protocol. Include a firewall for traffic filtering and network security. Provide a scalable three-tier architecture with Core, Distribution, and Access switches.
"""


print("\n===== STEP 1: EXTRACTING INTENT =====\n")

intent = extract_intent(user_input)

print(intent.model_dump_json(indent=4))


print("\n===== STEP 2: GENERATING NETWORK PLAN =====\n")

plan = generate_network_plan(intent)

print("\n===== FINAL NETWORK PLAN =====\n")

print(plan.model_dump_json(indent=4))