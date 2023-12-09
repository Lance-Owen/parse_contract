# -*- mode: python ; coding: utf-8 -*-


block_cipher = None
a = Analysis(['..\\parse_contract.py'],
pathex=['../venv/Lib/site-packages/paddle/include/paddle/phi/backends/dynload','../venv/Lib/site-packages/paddle/libs','../venv/Lib/site-packages/paddleocr','../venv/Lib/site-packages'],
    binaries=[('../venv/Lib/site-packages/paddle','.'),('../venv/Lib/site-packages/paddle/libs','.'),('../venv/Lib/site-packages/paddleocr','.'),('../venv/Lib/site-packages/paddle/include/paddle/phi/backends/dynload','.'),('../venv/Lib/site-packages/paddleocr/ppocr','.')],
     datas=[],
     hiddenimports=[],
     hookspath=['.'],
     runtime_hooks=[],
     excludes=[],
     noarchive=False)
pyz = PYZ(a.pure,
            a.zipped_data,
     cipher=block_cipher)

exe = EXE(pyz,
     a.scripts,
     [],
     exclude_binaries=True,
     name='main',
     debug=False,
     bootloader_ignore_signals=False,
     strip=False,
     upx=True,
     console=True)
coll = COLLECT(exe,
     a.binaries,
     a.zipfiles,
     a.datas,
     strip=False,
     upx=True,
     upx_exclude=[],
     name='main')