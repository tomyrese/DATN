import route_clean_pcb as rcp
from geometry_checker import check_clearance
from init_world_pads import world_pads

# Fix net name helper in route_clean_pcb
def get_net_id(name):
    if name in rcp.net_id:
        return rcp.net_id[name]
    if '/' + name in rcp.net_id:
        return rcp.net_id['/' + name]
    return 0

rcp.get_net_id = get_net_id

# Fix add_trace and add_raw to use get_net_id
def add_trace(net, pts, width=1.0, d=1.2):
    c_pts = rcp.chamfer_path(pts, d=d)
    nid = get_net_id(net)
    canonical_net = net if net.startswith('/') or net.startswith('Net-') else '/' + net
    for i in range(len(c_pts) - 1):
        rcp.tracks.append({
            'net': canonical_net,
            'net_id': nid,
            'p1': c_pts[i],
            'p2': c_pts[i+1],
            'width': width
        })

def add_raw(net, pts, width=1.0):
    nid = get_net_id(net)
    canonical_net = net if net.startswith('/') or net.startswith('Net-') else '/' + net
    for i in range(len(pts) - 1):
        rcp.tracks.append({
            'net': canonical_net,
            'net_id': nid,
            'p1': pts[i],
            'p2': pts[i+1],
            'width': width
        })

rcp.add_trace = add_trace
rcp.add_raw = add_raw

# Re-run route_all
rcp.route_all()
print(f"Total routed tracks: {len(rcp.tracks)}")

violations = check_clearance(rcp.tracks, world_pads, min_clearance=0.5)
print(f"Total geometry violations: {len(violations)}")
for v in violations[:15]:
    if v['type'] == 'track_pad_clearance':
        print(f"  Track-Pad: Track [{v['track_net']}] vs Pad {v['pad_ref']} [{v['pad_net']}] clearance={v['clearance']:.3f} mm at {v['pos']}")
    else:
        print(f"  Track-Track: [{v['net1']}] vs [{v['net2']}] clearance={v['clearance']:.3f} mm at {v['p1']} and {v['p2']}")

