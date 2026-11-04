import json

for pro_file in ['Pi4_Robot_Carrier_1Layer.kicad_pro', 'robot_electronics.kicad_pro']:
    with open(pro_file, 'r', encoding='utf-8') as f:
        pro = json.load(f)
    
    # 1. Update net classes
    pro['net_settings']['classes'] = [
        {
            "name": "Default",
            "clearance": 0.5,
            "track_width": 1.0,
            "via_diameter": 2.0,
            "via_drill": 0.8,
            "wire_width": 6,
            "bus_width": 12,
            "diff_pair_gap": 0.5,
            "diff_pair_via_gap": 0.5,
            "diff_pair_width": 1.0,
            "line_style": 0,
            "microvia_diameter": 0.3,
            "microvia_drill": 0.1,
            "pcb_color": "rgba(0, 0, 0, 0.000)",
            "priority": 2147483647,
            "schematic_color": "rgba(0, 0, 0, 0.000)",
            "tuning_profile": ""
        },
        {
            "name": "Power",
            "clearance": 0.5,
            "track_width": 1.4,
            "via_diameter": 2.0,
            "via_drill": 0.8,
            "wire_width": 6,
            "bus_width": 12,
            "diff_pair_gap": 0.5,
            "diff_pair_via_gap": 0.5,
            "diff_pair_width": 1.4,
            "line_style": 0,
            "microvia_diameter": 0.3,
            "microvia_drill": 0.1,
            "pcb_color": "rgba(0, 0, 0, 0.000)",
            "priority": 100,
            "schematic_color": "rgba(0, 0, 0, 0.000)",
            "tuning_profile": ""
        }
    ]
    
    # Netclass patterns
    pro['net_settings']['netclass_patterns'] = [
        {"netclass": "Power", "pattern": "GND*"},
        {"netclass": "Power", "pattern": "*5V*"},
        {"netclass": "Power", "pattern": "*VM*"},
        {"netclass": "Power", "pattern": "*12V*"}
    ]
    
    # 2. Update board design rules
    if 'board' in pro and 'design_settings' in pro['board']:
        rules = pro['board']['design_settings']['rules']
        rules['min_clearance'] = 0.5
        rules['min_track_width'] = 1.0
        rules['min_via_diameter'] = 2.0
        rules['min_copper_edge_clearance'] = 0.5
        rules['min_hole_clearance'] = 0.5
        rules['min_hole_to_hole'] = 0.5
        
        # Track angles: enforce no 90 degree corners
        pro['board']['design_settings']['rule_severities']['track_angle'] = 'error'
        pro['board']['design_settings']['rule_severities']['clearance'] = 'error'
        pro['board']['design_settings']['rule_severities']['track_width'] = 'error'

    with open(pro_file, 'w', encoding='utf-8') as f:
        json.dump(pro, f, indent=2)
    print(f"Updated design rules in {pro_file}")

