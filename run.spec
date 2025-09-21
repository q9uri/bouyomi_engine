# -*- mode: python ; coding: utf-8 -*-
# このファイルはPyInstallerによって自動生成されたもので、それをカスタマイズして使用しています。
from argparse import ArgumentParser
from pathlib import Path
from shutil import copy2, copytree

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = []
datas += collect_data_files('e2k')
datas += collect_data_files('unidic_lite')
datas += collect_data_files('yomikata')
datas += collect_data_files('kabosu_core')

hiddenimports = []
hiddenimports += collect_submodules("transformers")

a = Analysis(
    ["run.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="run",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    contents_directory="engine_internal",  # 実行時に"sys._MEIPASS"が参照するディレクトリ名
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="run",
)

# 実行ファイルのディレクトリに配置するファイルのコピー

# 実行ファイルと同じrootディレクトリ
target_dir = Path(DISTPATH) / "run"

# リソースをコピー
manifest_file_path = Path("engine_manifest.json")
copy2(manifest_file_path, target_dir)
copytree("resources", target_dir / "resources")
copytree("bouyomi-cli", target_dir / "bouyomi-cli")

license_file_path = Path("licenses.json")
if license_file_path.is_file():
    copy2("licenses.json", target_dir)
