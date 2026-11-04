with open('scripts/lib_symbols.sexpr', 'r', encoding='utf-8') as f:
    lib_text = f.read()

# Replace "C_Polarized" with "robot_electronics:C_Polarized"
lib_text = lib_text.replace('(symbol "C_Polarized"', '(symbol "robot_electronics:C_Polarized"')

with open('scripts/lib_symbols.sexpr', 'w', encoding='utf-8') as f:
    f.write(lib_text)

print("Updated lib_symbols.sexpr with robot_electronics:C_Polarized")

