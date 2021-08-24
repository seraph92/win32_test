# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

added_files = [ 
#    ('config.json', '.'),
    ('./ui/auto_log_program.ui', './ui/') ,
    ('./ui/user_detail.ui', './ui/') ,
    ('./driver/chromedriver.exe', './driver/') ,
#    ('./data/log.db', './data/') ,
    ('./log', './log') ,
]

a = Analysis(['qtWinMonGui.py'],
             pathex=['C:\\work\\python\\win32_test-1'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='qtWinMonGui',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , uac_admin=True)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='qtWinMonGui')
