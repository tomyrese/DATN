# Add rich silkscreen labels to robot_electronics.kicad_pcb
with open('robot_electronics.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

rich_labels = """\t(gr_text "1:3V3"
\t\t(at 79.06 91.2)
\t\t(layer "F.SilkS")
\t\t(uuid "a1b2c3d4-6001-4000-8000-000000000001")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.7 0.7)
\t\t\t\t(thickness 0.14)
\t\t\t)
\t\t)
\t)
\t(gr_text "2:5V"
\t\t(at 79.06 98.2)
\t\t(layer "F.SilkS")
\t\t(uuid "a1b2c3d4-6002-4000-8000-000000000002")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.7 0.7)
\t\t\t\t(thickness 0.14)
\t\t\t)
\t\t)
\t)
\t(gr_text "27:SDA"
\t\t(at 112.08 91.2)
\t\t(layer "F.SilkS")
\t\t(uuid "a1b2c3d4-6003-4000-8000-000000000003")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.7 0.7)
\t\t\t\t(thickness 0.14)
\t\t\t)
\t\t)
\t)
\t(gr_text "28:SCL"
\t\t(at 112.08 98.2)
\t\t(layer "F.SilkS")
\t\t(uuid "a1b2c3d4-6004-4000-8000-000000000004")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.7 0.7)
\t\t\t\t(thickness 0.14)
\t\t\t)
\t\t)
\t)
\t(gr_text "39:GND"
\t\t(at 127.32 91.2)
\t\t(layer "F.SilkS")
\t\t(uuid "a1b2c3d4-6005-4000-8000-000000000005")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.7 0.7)
\t\t\t\t(thickness 0.14)
\t\t\t)
\t\t)
\t)
\t(gr_text "40"
\t\t(at 127.32 98.2)
\t\t(layer "F.SilkS")
\t\t(uuid "a1b2c3d4-6006-4000-8000-000000000006")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.7 0.7)
\t\t\t\t(thickness 0.14)
\t\t\t)
\t\t)
\t)
\t(gr_text "M1_FL"
\t\t(at 67.7 51.0)
\t\t(layer "F.SilkS")
\t\t(uuid "a1b2c3d4-6011-4000-8000-000000000011")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.8 0.8)
\t\t\t\t(thickness 0.15)
\t\t\t)
\t\t)
\t)
\t(gr_text "M2_RL"
\t\t(at 76.8 51.0)
\t\t(layer "F.SilkS")
\t\t(uuid "a1b2c3d4-6012-4000-8000-000000000012")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.8 0.8)
\t\t\t\t(thickness 0.15)
\t\t\t)
\t\t)
\t)
\t(gr_text "M3_FR"
\t\t(at 139.8 51.0)
\t\t(layer "F.SilkS")
\t\t(uuid "a1b2c3d4-6013-4000-8000-000000000013")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.8 0.8)
\t\t\t\t(thickness 0.15)
\t\t\t)
\t\t)
\t)
\t(gr_text "M4_RR"
\t\t(at 150.8 51.0)
\t\t(layer "F.SilkS")
\t\t(uuid "a1b2c3d4-6014-4000-8000-000000000014")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.8 0.8)
\t\t\t\t(thickness 0.15)
\t\t\t)
\t\t)
\t)
\t(gr_text "US_LEFT"
\t\t(at 90.0 48.0)
\t\t(layer "F.SilkS")
\t\t(uuid "a1b2c3d4-6021-4000-8000-000000000021")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.8 0.8)
\t\t\t\t(thickness 0.15)
\t\t\t)
\t\t)
\t)
\t(gr_text "US_RIGHT"
\t\t(at 118.0 48.0)
\t\t(layer "F.SilkS")
\t\t(uuid "a1b2c3d4-6022-4000-8000-000000000022")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.8 0.8)
\t\t\t\t(thickness 0.15)
\t\t\t)
\t\t)
\t)
\t(gr_text "LINE_3CH"
\t\t(at 105.0 48.0)
\t\t(layer "F.SilkS")
\t\t(uuid "a1b2c3d4-6023-4000-8000-000000000023")
\t\t(effects
\t\t\t(font
\t\t\t\t(size 0.8 0.8)
\t\t\t\t(thickness 0.15)
\t\t\t)
\t\t)
\t)\n"""

idx_seg = text.find('(segment')
text = text[:idx_seg] + rich_labels + text[idx_seg:]

with open('robot_electronics.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(text)

with open('Pi4_Robot_Carrier_1Layer.kicad_pcb', 'w', encoding='utf-8') as f:
    f.write(text)

print("Added rich labels to robot_electronics.kicad_pcb and Pi4_Robot_Carrier_1Layer.kicad_pcb!")

