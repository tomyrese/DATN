import os
import subprocess

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
OUTPUT_DIR = os.path.abspath("pdf_lam_mach")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Using --drill-shape-opt 2 (Actual Shape - vẽ đúng lỗ thật 0.8mm)
# theo đúng yêu cầu hiển thị trực quan lỗ 0.8mm của người dùng
DRILL_OPT = "2"

commands = [
    # 1. Mặt đáy đồng B.Cu Lật Gương (Mirror) - Dành cho Ủi Nhiệt (Panel 4x A4)
    {
        "name": "01_Mat_Day_B_Cu_MIRROR_Ui_Nhiet.pdf",
        "cmd": [
            KICAD_CLI, "pcb", "export", "pdf",
            "-o", os.path.join(OUTPUT_DIR, "01_Mat_Day_B_Cu_MIRROR_Ui_Nhiet.pdf"),
            "-l", "B.Cu,Edge.Cuts",
            "--mirror",
            "--black-and-white",
            "--drill-shape-opt", DRILL_OPT,
            "--scale", "1",
            "--mode-single",
            "Pi4_Robot_Carrier_Panel_4x_A4.kicad_pcb"
        ]
    },
    # 2. Mặt đáy đồng B.Cu Chiều Thuận (Direct) - Dành cho In Film Cảm Quang UV / CNC (Panel 4x A4)
    {
        "name": "02_Mat_Day_B_Cu_DIRECT_In_Film.pdf",
        "cmd": [
            KICAD_CLI, "pcb", "export", "pdf",
            "-o", os.path.join(OUTPUT_DIR, "02_Mat_Day_B_Cu_DIRECT_In_Film.pdf"),
            "-l", "B.Cu,Edge.Cuts",
            "--black-and-white",
            "--drill-shape-opt", DRILL_OPT,
            "--scale", "1",
            "--mode-single",
            "Pi4_Robot_Carrier_Panel_4x_A4.kicad_pcb"
        ]
    },
    # 3. Mặt trên F.Silkscreen - Dành cho In Chữ Linh Kiện (Panel 4x A4)
    {
        "name": "03_Mat_Tren_F_Silkscreen.pdf",
        "cmd": [
            KICAD_CLI, "pcb", "export", "pdf",
            "-o", os.path.join(OUTPUT_DIR, "03_Mat_Tren_F_Silkscreen.pdf"),
            "-l", "F.SilkS,Edge.Cuts",
            "--black-and-white",
            "--scale", "1",
            "--mode-single",
            "Pi4_Robot_Carrier_Panel_4x_A4.kicad_pcb"
        ]
    },
    # 4. Sơ đồ nguyên lý Schematic toàn mạch
    {
        "name": "04_So_Do_Nguyen_Ly_Schematic.pdf",
        "cmd": [
            KICAD_CLI, "sch", "export", "pdf",
            "-o", os.path.join(OUTPUT_DIR, "04_So_Do_Nguyen_Ly_Schematic.pdf"),
            "Pi4_Robot_Carrier_1Layer.kicad_sch"
        ]
    }
]

def main():
    print("Exporting EXACTLY 4 clean fabrication PDFs with ACTUAL 0.8mm holes...")
    success = 0
    for task in commands:
        name = task["name"]
        cmd = task["cmd"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[OK] {name}")
            success += 1
        else:
            print(f"[ERROR] {name}: {res.stderr}")
    print(f"\nCompleted {success}/{len(commands)} exports.")

if __name__ == '__main__':
    main()
