"""Install the complete desktop payload, including its Windows icon and locales."""
from pathlib import Path
import shutil

FILES=("demo_launcher.py","desktop_ui.py","app_window.py","ui_text.py","create_world.py","preflight.py","campaign.py","reset_world.py","new_campaign.py")

def package_app(source:Path,destination:Path):
    destination.mkdir(parents=True,exist_ok=True)
    for name in FILES:
        shutil.copyfile(source/name,destination/name)
    (destination/"assets").mkdir(exist_ok=True)
    for name in ("zone-mark.ico","zone-mark.svg"):
        shutil.copyfile(source/"assets"/name,destination/"assets"/name)
    shutil.copyfile(source/"run_demo.py",destination/"run_demo.py")
