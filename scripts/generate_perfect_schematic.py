#!/usr/bin/env python3
"""
Generate Pi4_Robot_Carrier_1Layer.kicad_sch
Khớp 100% phong cách thiết kế, 4 khối chức năng, khung nét đứt xanh và title block
tương tự ảnh tham chiếu robot_electronics (Image 3).
Định dạng: KiCad 10 / version 20260306 (Không có thanh cảnh báo phiên bản cũ).
"""

import sys
import re
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def generate_schematic():
    sch_path = Path("Pi4_Robot_Carrier_1Layer.kicad_sch")
    
    # Đọc lib_symbols đã trích xuất từ robot_electronics
    lib_symbols_path = Path("extracted_lib_symbols.txt")
    if lib_symbols_path.exists():
        lib_symbols_text = lib_symbols_path.read_text(encoding="utf-8")
    else:
        print("Lỗi: Không tìm thấy extracted_lib_symbols.txt")
        sys.exit(1)

    # Thêm symbol OLED 1.3 I2C nếu chưa có
    oled_symbol_str = """
		(symbol "robot_electronics:Display_OLED_1.3_I2C"
			(pin_names
				(offset 1.016)
			)
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(property "Reference" "J_OLED"
				(at 0 7.62 0)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Value" "OLED_1.3_I2C"
				(at 0 -7.62 0)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Footprint" "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical"
				(at 0 0 0)
				(effects
					(font
						(size 1.27 1.27)
					)
					(hide yes)
				)
			)
			(symbol "Display_OLED_1.3_I2C_0_1"
				(rectangle
					(start -6.35 6.35)
					(end 6.35 -6.35)
					(stroke
						(width 0.254)
						(type default)
					)
					(fill
						(type background)
					)
				)
			)
			(symbol "Display_OLED_1.3_I2C_1_1"
				(pin power_in line
					(at -8.89 3.81 0)
					(length 2.54)
					(name "VCC_3V3"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "1"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin power_in line
					(at -8.89 1.27 0)
					(length 2.54)
					(name "GND"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "2"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin input line
					(at 8.89 3.81 180)
					(length 2.54)
					(name "SCK"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "3"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
				(pin bidirectional line
					(at 8.89 1.27 180)
					(length 2.54)
					(name "SDA"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
					(number "4"
						(effects
							(font
								(size 1.27 1.27)
							)
						)
					)
				)
			)
		)
"""
    # Chèn OLED symbol vào lib_symbols trước ngoặc đóng cuối cùng
    last_bracket = lib_symbols_text.rfind(')')
    full_lib_symbols = lib_symbols_text[:last_bracket] + oled_symbol_str + "\n\t)"

    header = """(kicad_sch
	(version 20260306)
	(generator "eeschema")
	(generator_version "10.0")
	(uuid "d0a1b2c3-1111-2222-3333-000000000001")
	(paper "A3")
	(title_block
		(title "SO DO NGUYEN LY ROBOT 4WD RASPBERRY PI 4 (TOI GIAN - CHUAN 1 LOP)")
		(date "2026-10-29")
		(rev "2.0")
		(company "DATN - He Thong Nhung & Dien Tu Cong Suat")
		(comment 1 "Toi gian hoa toi da - So do doi xung hoan hao de di mach 1 lop (Single-Sided PCB) de nhat")
		(comment 2 "Tin hieu trai ben Trai, tin hieu phai ben Phai, khong cat cheo day")
	)
"""

    # 4 khung nét đứt phân khối (Bounding Boxes)
    boxes = """
	(polyline
		(pts
			(xy 20.32 20.32) (xy 190.5 20.32) (xy 190.5 114.3) (xy 20.32 114.3) (xy 20.32 20.32)
		)
		(stroke
			(width 0.4)
			(type dash)
			(color 0 100 220 1)
		)
		(fill
			(type none)
		)
		(uuid "box-khoi-1-uuid-0001")
	)
	(polyline
		(pts
			(xy 195.58 20.32) (xy 406.4 20.32) (xy 406.4 114.3) (xy 195.58 114.3) (xy 195.58 20.32)
		)
		(stroke
			(width 0.4)
			(type dash)
			(color 0 100 220 1)
		)
		(fill
			(type none)
		)
		(uuid "box-khoi-2-uuid-0002")
	)
	(polyline
		(pts
			(xy 20.32 119.38) (xy 190.5 119.38) (xy 190.5 241.3) (xy 20.32 241.3) (xy 20.32 119.38)
		)
		(stroke
			(width 0.4)
			(type dash)
			(color 0 100 220 1)
		)
		(fill
			(type none)
		)
		(uuid "box-khoi-3-uuid-0003")
	)
	(polyline
		(pts
			(xy 195.58 119.38) (xy 406.4 119.38) (xy 406.4 241.3) (xy 195.58 241.3) (xy 195.58 119.38)
		)
		(stroke
			(width 0.4)
			(type dash)
			(color 0 100 220 1)
		)
		(fill
			(type none)
		)
		(uuid "box-khoi-4-uuid-0004")
	)

	(text "KHOI 1: NGUON DIEN (PIN 3S2P 11.1V-12.6V, BAO VE & BUCK XL4015)"
		(exclude_from_sim no)
		(at 25.4 26.67 0)
		(effects
			(font
				(size 2 2)
				(bold yes)
			)
			(justify left bottom)
		)
		(uuid "txt-khoi-1-uuid-0001")
	)
	(text "KHOI 2: TIN HIEU & CAM BIEN (2x HC-SR04 + CHIA AP, 1x OLED 1.3\\" I2C)"
		(exclude_from_sim no)
		(at 200.66 26.67 0)
		(effects
			(font
				(size 2 2)
				(bold yes)
			)
			(justify left bottom)
		)
		(uuid "txt-khoi-2-uuid-0002")
	)
	(text "KHOI 3: DIEU KHIEN (RASPBERRY PI 4 MODEL B - 40-PIN GPIO)"
		(exclude_from_sim no)
		(at 25.4 125.73 0)
		(effects
			(font
				(size 2 2)
				(bold yes)
			)
			(justify left bottom)
		)
		(uuid "txt-khoi-3-uuid-0003")
	)
	(text "KHOI 4: CHAP HANH (2x TB6612FNG BREAKOUT, 4x DONG CO DC)"
		(exclude_from_sim no)
		(at 200.66 125.73 0)
		(effects
			(font
				(size 2 2)
				(bold yes)
			)
			(justify left bottom)
		)
		(uuid "txt-khoi-4-uuid-0004")
	)

	(text "Ghi chu: Module Camera Pi ket noi truc tiep vao cong CSI tren Pi 4 bang cap FFC de dam bao toan ven tin hieu vi sai toc do cao."
		(exclude_from_sim no)
		(at 25.4 246.00 0)
		(effects
			(font
				(size 1.6 1.6)
				(italic yes)
			)
			(justify left bottom)
		)
		(uuid "txt-csi-note-uuid-0005")
	)
"""

    # Đọc symbol instances, wires, labels từ template hoàn hảo của robot_electronics
    # và điều chỉnh linh kiện cho đúng 100% với danh mục của Pi4_Robot_Carrier_1Layer
    with open('d:/Study/DATN_FULL/robot_electronics/robot_electronics.kicad_sch', 'r', encoding='utf-8') as ref_f:
        ref_text = ref_f.read()

    # Lấy phần sau lib_symbols từ ref_text
    lib_end_idx = ref_text.find('\n\t(symbol\n')
    if lib_end_idx == -1:
        lib_end_idx = ref_text.find('\n\t(symbol ')
    symbols_and_wires = ref_text[lib_end_idx:]

    # Thay thế TCRT5000 bằng Display_OLED_1.3_I2C và R_JMP1
    # Trong ref_text: U_LINE là TCRT5000_3CH tại (355.60, 68.58)
    oled_replacement = """
	(symbol
		(lib_id "robot_electronics:Display_OLED_1.3_I2C")
		(at 355.60 68.58 0)
		(unit 1)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(dnp no)
		(uuid "sym-oled-uuid-0001")
		(property "Reference" "J_OLED"
			(at 355.60 60.96 0)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Value" "OLED_1.3_I2C"
			(at 355.60 76.20 0)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Footprint" "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical"
			(at 355.60 68.58 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(pin "1" (uuid "oled-pin1-uuid"))
		(pin "2" (uuid "oled-pin2-uuid"))
		(pin "3" (uuid "oled-pin3-uuid"))
		(pin "4" (uuid "oled-pin4-uuid"))
	)
	(symbol
		(lib_id "robot_electronics:R")
		(at 335.28 69.85 0)
		(unit 1)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(dnp no)
		(uuid "sym-rjmp1-uuid-0002")
		(property "Reference" "R_JMP1"
			(at 335.28 66.04 0)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Value" "0R"
			(at 335.28 73.66 0)
			(effects
				(font
					(size 1.27 1.27)
				)
			)
		)
		(property "Footprint" "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"
			(at 335.28 69.85 0)
			(effects
				(font
					(size 1.27 1.27)
				)
				(hide yes)
			)
		)
		(pin "1" (uuid "rjmp1-pin1-uuid"))
		(pin "2" (uuid "rjmp1-pin2-uuid"))
	)
	(label "I2C_SDA"
		(at 327.66 69.85 0)
		(fields_autoplaced yes)
		(effects
			(font
				(size 1.27 1.27)
			)
			(justify right bottom)
		)
		(uuid "lbl-sda1-uuid")
	)
	(label "I2C_SDA_IN"
		(at 342.90 69.85 0)
		(fields_autoplaced yes)
		(effects
			(font
				(size 1.27 1.27)
			)
			(justify left bottom)
		)
		(uuid "lbl-sda2-uuid")
	)
	(wire
		(pts
			(xy 342.90 69.85) (xy 364.49 69.85)
		)
		(stroke (width 0) (type default))
		(uuid "wire-sda-oled-uuid")
	)
	(label "I2C_SCL"
		(at 364.49 72.39 0)
		(fields_autoplaced yes)
		(effects
			(font
				(size 1.27 1.27)
			)
			(justify left bottom)
		)
		(uuid "lbl-scl-oled-uuid")
	)
	(label "3V3"
		(at 346.71 72.39 180)
		(fields_autoplaced yes)
		(effects
			(font
				(size 1.27 1.27)
			)
			(justify right bottom)
		)
		(uuid "lbl-3v3-oled-uuid")
	)
	(symbol
		(lib_id "robot_electronics:GND")
		(at 346.71 77.47 0)
		(unit 1)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(dnp no)
		(uuid "sym-gnd-oled-uuid")
		(property "Reference" "#PWR_OLED_GND"
			(at 346.71 83.82 0)
			(effects
				(font (size 1.27 1.27))
				(hide yes)
			)
		)
		(property "Value" "GND"
			(at 346.71 81.28 0)
			(effects
				(font (size 1.27 1.27))
				(hide yes)
			)
		)
		(property "Footprint" ""
			(at 346.71 77.47 0)
			(effects
				(font (size 1.27 1.27))
				(hide yes)
			)
		)
		(pin "1" (uuid "gnd-oled-p1-uuid"))
	)
	(wire
		(pts
			(xy 346.71 69.85) (xy 346.71 77.47)
		)
		(stroke (width 0) (type default))
		(uuid "wire-gnd-oled-uuid")
	)
"""

    # Thay thế symbol U_LINE bằng OLED
    symbols_and_wires = re.sub(
        r'\(symbol\s+\(lib_id\s+"robot_electronics:Sensor_Line_TCRT5000_3CH"\)[\s\S]*?\n\t\)',
        oled_replacement,
        symbols_and_wires,
        count=1
    )

    # Thay thế các nhãn LINE_L, LINE_C, LINE_R thành nhãn OLED tương ứng trên IDC40
    symbols_and_wires = symbols_and_wires.replace('LINE_L', 'I2C_SDA')
    symbols_and_wires = symbols_and_wires.replace('LINE_C', 'I2C_SCL')

    # Thay thế điện trở P7.62mm thành P10.16mm theo đúng yêu cầu DRC THT
    symbols_and_wires = symbols_and_wires.replace(
        'R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',
        'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal'
    )

    # Đổi tên connector motor J_M1..J_M4 hoặc J_MOT_L / J_MOT_R footprint
    symbols_and_wires = symbols_and_wires.replace(
        'robot_electronics:TerminalBlock_Phoenix_MKDS-1,5-2-5.08',
        'Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical'
    )
    symbols_and_wires = symbols_and_wires.replace(
        'robot_electronics:PinSocket_2x20_P2.54mm_Vertical',
        'Connector_IDC:IDC-Header_2x20_P2.54mm_Vertical'
    )

    final_sch = header + full_lib_symbols + boxes + symbols_and_wires
    sch_path.write_text(final_sch, encoding="utf-8")
    print(f"[XUẤT SẮC] Đã tạo thành công Schematic mới: {sch_path}")

if __name__ == "__main__":
    generate_schematic()
