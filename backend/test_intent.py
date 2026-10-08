from ai.intent_extractor import extract_intent


user_input = """
Design a network for a college with 500 users.
There are 5 departments.
The network should provide WiFi, CCTV, VoIP and Internet.
Use VLANs and a firewall.
"""


intent = extract_intent(user_input)


print("\n===== AI GENERATED NETWORK INTENT =====\n")

print(intent.model_dump_json(indent=4))