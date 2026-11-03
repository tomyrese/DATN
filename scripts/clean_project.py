import os, shutil, glob

def safe_remove_file(filepath):
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Removed file: {filepath}")
            return True
    except Exception as e:
        print(f"Error removing {filepath}: {e}")
    return False

def safe_remove_dir(dirpath):
    try:
        if os.path.exists(dirpath):
            shutil.rmtree(dirpath)
            print(f"Removed directory: {dirpath}")
            return True
    except Exception as e:
        print(f"Error removing directory {dirpath}: {e}")
    return False

def main():
    root = os.path.abspath('.')
    print(f"=== Deep Project Cleanup in: {root} ===")

    removed_files = 0
    removed_dirs = 0

    # 1. Clean root temporary test kicad files
    test_pcbs = [
        'temp_drc.kicad_pcb',
        'test_clean_1layer.kicad_pcb',
        'test_complete_routing.kicad_pcb',
        'test_direct_jumper.kicad_pcb',
        'test_gnd_direct.kicad_pcb',
        'test_masterpiece_clean.kicad_pcb',
        'test_no_silk_drc.kicad_pcb',
        'schematic_diagram.pdf',
        'schematic_diagram_nosheet.pdf',
        'pcb_render_complete.svg',
    ]
    for f in test_pcbs:
        if safe_remove_file(f):
            removed_files += 1

    # 2. Clean all *.kicad_prl in root
    for f in glob.glob('*.kicad_prl'):
        if safe_remove_file(f):
            removed_files += 1

    # 3. Clean obsolete backups and root duplicate exports
    obsolete_root_files = [
        'KLTN_DeCuong_NguyenPhuQuy_LeMinhNgoc_backup.pptx',
        'KLTN_DeCuong_NguyenPhuQuy_LeMinhNgoc.pptx.bak',
        'machin.pdf',
        '07_Don_1X_Mach_Day_B_Cu_DIRECT_In_Film.docx',
        'Pi4_Robot_Carrier_1Layer_pcb.pdf',
        'Pi4_Robot_Carrier_1Layer_sch.pdf',
        'Pi4_Robot_Carrier_1Layer.pdf',
        'Pi4_Robot_Carrier_1Layer.svg',
        'Pi4_Robot_Carrier_Schematic.pdf',
        'Pi4_Robot_Carrier_1Layer.kicad_pcb.bak',
        'robot_electronics.kicad_pcb.bak',
        'robot_electronics.kicad_pcb.user_backup',
        '~Pi4_Robot_Carrier_1Layer.kicad_pro.lck',
        '~robot_electronics.kicad_pro.lck',
    ]
    for f in obsolete_root_files:
        if safe_remove_file(f):
            removed_files += 1

    # 4. Clean DRC/ERC text reports & dump logs in root
    report_patterns = [
        'drc_*.txt',
        'erc_*.txt',
        '*.rpt',
        'report.txt',
        'slides_*.txt',
        'slides_detailed.json',
        'slide_full_analysis.txt',
        'theme_analysis.txt',
    ]
    for pat in report_patterns:
        for f in glob.glob(pat):
            if safe_remove_file(f):
                removed_files += 1

    # 5. Clean obsolete / accidental directories
    obsolete_dirs = [
        '.history',
        'Pi4_Robot_Carrier_1Layer_sch.svg',
        'Pi4_Robot_Carrier_Schematic_SVG',
        'schematic_diagram.svg',
        os.path.join('scripts', 'archive'),
        os.path.join('extracted_imgs', 'pptx_rendered_slides'),
        os.path.join('extracted_imgs', 'all_embedded'),
        os.path.join('extracted_imgs', 'bak_slides'),
        os.path.join('extracted_imgs', 'pptx_slides'),
        os.path.join('extracted_imgs', 'pptx_imgs'),
    ]
    for d in obsolete_dirs:
        if safe_remove_dir(d):
            removed_dirs += 1

    # 6. Clean intermediate images in extracted_imgs/
    # Keep only official assets
    keep_imgs = {
        'block1_power_clean.png',
        'block2_control_clean.png',
        'block3_signal_clean.png',
        'block4_actuators_clean.png',
        'pcb_complete_routed.png',
        'pcb_zoom_completed.png',
        'pcb_oled_zoom.png',
        'pcb_with_oled_visual.png',
        'web_dashboard.png',
        'schematic_diagram_cropped.png',
    }
    extracted_imgs_dir = os.path.abspath('extracted_imgs')
    if os.path.exists(extracted_imgs_dir):
        for item in os.listdir(extracted_imgs_dir):
            p = os.path.join(extracted_imgs_dir, item)
            if os.path.isfile(p):
                if item not in keep_imgs:
                    if safe_remove_file(p):
                        removed_files += 1

    # 7. Clean obsolete gerbers (old robot_electronics 2-layer gerbers from 10/29)
    gerbers_dir = os.path.abspath('gerbers')
    if os.path.exists(gerbers_dir):
        for item in os.listdir(gerbers_dir):
            if item.startswith('robot_electronics'):
                p = os.path.join(gerbers_dir, item)
                if safe_remove_file(p):
                    removed_files += 1

    # 8. Clean scripts folder: only keep core scripts
    scripts_dir = os.path.abspath('scripts')
    core_scripts = {
        'generate_block_diagrams.py',
        'apply_block_diagrams.py',
        'export_all_pptx_slides.py',
        'refine_all_slides.py',
        'render_completed_pcb.py',
        'render_oled_zoom.py',
        'render_pcb_oled.py',
        'render_zoom_completed.py',
        'build_true_1layer.py',
        'add_rich_silk.py',
        'build_panels.py',
        'export_all_fabrication_pdfs.py',
        'check_fonts.py',
        'clean_project.py',
    }

    if os.path.exists(scripts_dir):
        for item in os.listdir(scripts_dir):
            item_path = os.path.join(scripts_dir, item)
            if item == '__pycache__':
                if safe_remove_dir(item_path):
                    removed_dirs += 1
            elif os.path.isfile(item_path):
                if item not in core_scripts:
                    if safe_remove_file(item_path):
                        removed_files += 1

    print(f"\nCleanup Complete:")
    print(f"  - Deleted {removed_files} obsolete / temporary / backup files")
    print(f"  - Deleted {removed_dirs} scratch / archive directories")

if __name__ == '__main__':
    main()
