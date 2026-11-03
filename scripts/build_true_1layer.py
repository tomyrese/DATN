import re

# Read original user PCB
with open('robot_electronics.kicad_pcb.user_backup', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Clean up redundant vias from user's manual experimentation:
# Remove via at (89.18 75.291806)
text = re.sub(r'\t\(via\s+\(at 89\.18 75\.291806\)[\s\S]*?\n\t\)\n', '', text)
# Remove segment (start 89.18 75.291806) (end 89.175489 75.296317)
text = re.sub(r'\t\(segment\s+\(start 89\.18 75\.291806\)[\s\S]*?\n\t\)\n', '', text)
# Remove micro stub from (89.18 72.4425) to (89.18 75.291806)
text = re.sub(r'\t\(segment\s+\(start 89\.18 72\.4425\)[\s\S]*?\(end 89\.18 75\.291806\)[\s\S]*?\n\t\)\n', '', text)

# Remove via at (94 99)
text = re.sub(r'\t\(via\s+\(at 94 99\)[\s\S]*?\n\t\)\n', '', text)
# Remove segment (start 94 102.4425) (end 94 99)
text = re.sub(r'\t\(segment\s+\(start 94 102\.4425\)[\s\S]*?\(end 94 99\)[\s\S]*?\n\t\)\n', '', text)

# 2. Add Jumper Vias on the board (drill 0.8, size 1.6 for comfortable DIY soldering):
new_vias = """\t(via
\t\t(at 112.08 88.5)
\t\t(size 1.6)
\t\t(drill 0.8)
\t\t(layers "F.Cu" "B.Cu")
\t\t(net "/I2C_SDA")
\t\t(uuid "f0e1d2c3-1001-4000-8000-000000000001")
\t)
\t(via
\t\t(at 144.5 88.5)
\t\t(size 1.6)
\t\t(drill 0.8)
\t\t(layers "F.Cu" "B.Cu")
\t\t(net "/I2C_SDA")
\t\t(uuid "f0e1d2c3-1002-4000-8000-000000000002")
\t)
\t(via
\t\t(at 99.38 85.0)
\t\t(size 1.6)
\t\t(drill 0.8)
\t\t(layers "F.Cu" "B.Cu")
\t\t(net "/+3V3_LOGIC")
\t\t(uuid "f0e1d2c3-2001-4000-8000-000000000001")
\t)
\t(via
\t\t(at 152.12 85.0)
\t\t(size 1.6)
\t\t(drill 0.8)
\t\t(layers "F.Cu" "B.Cu")
\t\t(net "/+3V3_LOGIC")
\t\t(uuid "f0e1d2c3-2002-4000-8000-000000000002")
\t)
\t(via
\t\t(at 54.0 63.5)
\t\t(size 1.6)
\t\t(drill 0.8)
\t\t(layers "F.Cu" "B.Cu")
\t\t(net "GND")
\t\t(uuid "f0e1d2c3-3001-4000-8000-000000000001")
\t)
\t(via
\t\t(at 63.88 62.7795)
\t\t(size 1.6)
\t\t(drill 0.8)
\t\t(layers "F.Cu" "B.Cu")
\t\t(net "GND")
\t\t(uuid "f0e1d2c3-3002-4000-8000-000000000002")
\t)\n"""

# 3. Add B.Cu copper tracks (100% on B.Cu, ZERO ON F.Cu!):
new_bcu_tracks = """\t(segment
\t\t(start 112.08 93.5575)
\t\t(end 112.08 88.5)
\t\t(width 1)
\t\t(layer "B.Cu")
\t\t(net "/I2C_SDA")
\t\t(uuid "f0e1d2c3-1003-4000-8000-000000000003")
\t)
\t(segment
\t\t(start 144.5 88.5)
\t\t(end 144.5 96.5)
\t\t(width 1)
\t\t(layer "B.Cu")
\t\t(net "/I2C_SDA")
\t\t(uuid "f0e1d2c3-1004-4000-8000-000000000004")
\t)
\t(segment
\t\t(start 152.12 85.0)
\t\t(end 152.12 96.5)
\t\t(width 1)
\t\t(layer "B.Cu")
\t\t(net "/+3V3_LOGIC")
\t\t(uuid "f0e1d2c3-2003-4000-8000-000000000003")
\t)\n"""

# 4. Comprehensive Silkscreen Annotations & Jumper Guides on F.SilkS:
# We draw silkscreen lines connecting the vias and text labels!
silkscreen_annotations = """\t(gr_line
\t\t(start 112.08 88.5)
\t\t(end 144.5 88.5)
\t\t(stroke
\t\t\t(width 0.25)
\t\t\t(type dash)
\t\t)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5001-4000-8000-000000000001")
\t)
\t(gr_circle
\t\t(center 112.08 88.5)
\t\t(end 113.2 88.5)
\t\t(stroke
\t\t\t(width 0.2)
\t\t\t(type default)
\t\t)
\t\t(fill none)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5002-4000-8000-000000000002")
\t)
\t(gr_circle
\t\t(center 144.5 88.5)
\t\t(end 145.6 88.5)
\t\t(stroke
\t\t\t(width 0.2)
\t\t\t(type default)
\t\t)
\t\t(fill none)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5003-4000-8000-000000000003")
\t)
\t(gr_text "JMP1: SDA (Wire 32mm)"
\t\t(at 128.0 89.8)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5004-4000-8000-000000000004")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.8 0.8)
\t\t\t\t(thickness 0.15)
\t\t\t)
\t\t)
\t)
\t(gr_line
\t\t(start 99.38 85.0)
\t\t(end 152.12 85.0)
\t\t(stroke
\t\t\t(width 0.25)
\t\t\t(type dash)
\t\t)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5011-4000-8000-000000000011")
\t)
\t(gr_circle
\t\t(center 99.38 85.0)
\t\t(end 100.5 85.0)
\t\t(stroke
\t\t\t(width 0.2)
\t\t\t(type default)
\t\t)
\t\t(fill none)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5012-4000-8000-000000000012")
\t)
\t(gr_circle
\t\t(center 152.12 85.0)
\t\t(end 153.2 85.0)
\t\t(stroke
\t\t\t(width 0.2)
\t\t\t(type default)
\t\t)
\t\t(fill none)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5013-4000-8000-000000000013")
\t)
\t(gr_text "JMP2: +3V3 (Wire 53mm)"
\t\t(at 125.0 83.8)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5014-4000-8000-000000000014")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.8 0.8)
\t\t\t\t(thickness 0.15)
\t\t\t)
\t\t)
\t)
\t(gr_line
\t\t(start 76.58 80.316335)
\t\t(end 86.378918 72.4425)
\t\t(stroke
\t\t\t(width 0.25)
\t\t\t(type dash)
\t\t)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5021-4000-8000-000000000021")
\t)
\t(gr_circle
\t\t(center 76.58 80.316335)
\t\t(end 77.7 80.316335)
\t\t(stroke
\t\t\t(width 0.2)
\t\t\t(type default)
\t\t)
\t\t(fill none)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5022-4000-8000-000000000022")
\t)
\t(gr_circle
\t\t(center 86.378918 72.4425)
\t\t(end 87.5 72.4425)
\t\t(stroke
\t\t\t(width 0.2)
\t\t\t(type default)
\t\t)
\t\t(fill none)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5023-4000-8000-000000000023")
\t)
\t(gr_text "JMP3: GND_L (13mm)"
\t\t(at 81.5 77.0)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5024-4000-8000-000000000024")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.7 0.7)
\t\t\t\t(thickness 0.14)
\t\t\t)
\t\t)
\t)
\t(gr_line
\t\t(start 54.0 63.5)
\t\t(end 63.88 62.7795)
\t\t(stroke
\t\t\t(width 0.25)
\t\t\t(type dash)
\t\t)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5031-4000-8000-000000000031")
\t)
\t(gr_circle
\t\t(center 54.0 63.5)
\t\t(end 55.1 63.5)
\t\t(stroke
\t\t\t(width 0.2)
\t\t\t(type default)
\t\t)
\t\t(fill none)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5032-4000-8000-000000000032")
\t)
\t(gr_circle
\t\t(center 63.88 62.7795)
\t\t(end 64.9 62.7795)
\t\t(stroke
\t\t\t(width 0.2)
\t\t\t(type default)
\t\t)
\t\t(fill none)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5033-4000-8000-000000000033")
\t)
\t(gr_text "JMP4: GND_PWR (0Ω/10mm)"
\t\t(at 58.0 61.5)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5034-4000-8000-000000000034")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.65 0.65)
\t\t\t\t(thickness 0.13)
\t\t\t)
\t\t)
\t)
\t(gr_line
\t\t(start 77.0 101.5)
\t\t(end 87.5 101.5)
\t\t(stroke
\t\t\t(width 0.25)
\t\t\t(type dash)
\t\t)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5041-4000-8000-000000000041")
\t)
\t(gr_line
\t\t(start 87.5 101.5)
\t\t(end 90.0 99.0)
\t\t(stroke
\t\t\t(width 0.25)
\t\t\t(type dash)
\t\t)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5042-4000-8000-000000000042")
\t)
\t(gr_circle
\t\t(center 77.0 101.5)
\t\t(end 78.1 101.5)
\t\t(stroke
\t\t\t(width 0.2)
\t\t\t(type default)
\t\t)
\t\t(fill none)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5043-4000-8000-000000000043")
\t)
\t(gr_circle
\t\t(center 90.0 99.0)
\t\t(end 91.1 99.0)
\t\t(stroke
\t\t\t(width 0.2)
\t\t\t(type default)
\t\t)
\t\t(fill none)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5044-4000-8000-000000000044")
\t)
\t(gr_text "JMP5: GND_PI4 (14mm)"
\t\t(at 83.5 103.2)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5045-4000-8000-000000000045")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.7 0.7)
\t\t\t\t(thickness 0.14)
\t\t\t)
\t\t)
\t)
\t(gr_text "+VM_12V"
\t\t(at 51.0 48.0)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5051-4000-8000-000000000051")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.8 0.8)
\t\t\t\t(thickness 0.15)
\t\t\t)
\t\t)
\t)
\t(gr_text "GND_IN"
\t\t(at 51.0 50.5)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5052-4000-8000-000000000052")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.8 0.8)
\t\t\t\t(thickness 0.15)
\t\t\t)
\t\t)
\t)
\t(gr_text "OLED 1.3\\" I2C [1:3V3  2:GND  3:SCL  4:SDA]"
\t\t(at 148.0 93.0)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5061-4000-8000-000000000061")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.7 0.7)
\t\t\t\t(thickness 0.14)
\t\t\t)
\t\t)
\t)
\t(gr_text "SINGLE-SIDED PCB (1 LAYER) - TOP WIRE JUMPERS JMP1..JMP5"
\t\t(at 105.0 40.0)
\t\t(layer "F.SilkS")
\t\t(uuid "f0e1d2c3-5071-4000-8000-000000000071")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.0 1.0)
\t\t\t\t(thickness 0.18)
\t\t\t)
\t\t)
\t)\n"""

idx_via = text.find('(via')
text = text[:idx_via] + new_vias + text[idx_via:]

idx_seg = text.find('(segment')
text = text[:idx_seg] + new_bcu_tracks + silkscreen_annotations + text[idx_seg:]

with open('robot_electronics.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(text)

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved robot_electronics.kicad_pcb and Pi4_Robot_Carrier_1Layer.kicad_pcb successfully!")

