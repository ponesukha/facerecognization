import sys
from pathlib import Path

root = Path(SPECPATH).parent
name = "MRO Face"

a = Analysis(
    [str(root / "app" / "__main__.py")],
    pathex=[str(root)],
    datas=[(str(root / "models" / "*.onnx"), "models")],
    hiddenimports=[],
    excludes=["tkinter"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=name,
    console=False,
    target_arch="arm64" if sys.platform == "darwin" else None,
)

coll = COLLECT(exe, a.binaries, a.datas, name=name)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name=f"{name}.app",
        bundle_identifier="org.monrefugee.mroface",
        info_plist={
            "CFBundleDisplayName": name,
            "CFBundleShortVersionString": "0.1.0",
            "CFBundleVersion": "0.1.0",
            "NSCameraUsageDescription": "MRO Face uses the camera to capture member faces for identity checks.",
            "NSHighResolutionCapable": True,
            "LSMinimumSystemVersion": "12.0",
        },
    )
