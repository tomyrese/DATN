import os, sys
import win32com.client

ppt_path = os.path.abspath('KLTN_DeCuong_NguyenPhuQuy_LeMinhNgoc.pptx')
out_dir = os.path.abspath('extracted_imgs/pptx_rendered_slides')
os.makedirs(out_dir, exist_ok=True)

powerpoint = win32com.client.Dispatch('PowerPoint.Application')
# Powerpoint may throw if not visible or visible
pres = None
try:
    pres = powerpoint.Presentations.Open(ppt_path, WithWindow=False)
    # ppSaveAsJPG = 17, ppSaveAsPNG = 18
    # In PowerPoint COM, SaveAs with 17 exports each slide as Slide1.JPG, Slide2.JPG... into the directory
    pres.SaveAs(out_dir, 17)
    print(f"Exported all slides to {out_dir}")
finally:
    if pres:
        pres.Close()
    powerpoint.Quit()

