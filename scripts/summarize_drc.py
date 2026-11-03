with open('Pi4_Robot_Carrier_1Layer-drc.rpt', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's count violation types
import re
violations = re.findall(r'\[([a-zA-Z0-9_]+)\]: ([^\n]+)', text)
counts = {}
for code, msg in violations:
    counts[f"[{code}]: {msg}"] = counts.get(f"[{code}]: {msg}", 0) + 1

print("Violation summary:")
for k, v in counts.items():
    print(f"  {v}x {k}")

pos_unconn = text.find('unconnected pads')
if pos_unconn != -1:
    print("\nUnconnected section:")
    print(text[pos_unconn:pos_unconn+1500])
