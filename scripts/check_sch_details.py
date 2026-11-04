with open('Pi4_Robot_Carrier_1Layer.kicad_sch', 'r', encoding='utf-8') as f:
    text = f.read()

# Find symbol U_PI4
import re
pi_sym = re.search(r'\(symbol\s+\(lib_id\s+"robot_electronics:Raspberry_Pi_4_40Pin"\)[\s\S]*?\(property\s+"Reference"\s+"U_PI4"[\s\S]*?\n\t\)', text)
if pi_sym:
    print(pi_sym.group(0)[:2000])

tb_sym = re.search(r'\(symbol\s+\(lib_id\s+"robot_electronics:Module_TB6612FNG_Breakout"\)[\s\S]*?\(property\s+"Reference"\s+"U_TB1"[\s\S]*?\n\t\)', text)
if tb_sym:
    print("\n--- U_TB1 ---")
    print(tb_sym.group(0)[:2000])

