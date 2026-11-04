import re

with open('scripts/lib_symbols.sexpr', 'r', encoding='utf-8') as f:
    text = f.read()

sym_names = re.findall(r'\(symbol\s+"([^"]+)"', text)
print("Symbols in lib_symbols:", sym_names)

