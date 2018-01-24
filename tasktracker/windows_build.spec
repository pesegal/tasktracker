# -*- mode: python -*-
from kivy.deps import sdl2, glew, gstreamer

block_cipher = None


a = Analysis(['main.py'],
             pathex=['C:\\Users\\Peter\\code\\tasktracker\\tasktracker'],
             binaries=[],
             datas=[
			    ('themes\\gfx\\*.png', 'themes\\gfx'),
                ('themes\\sounds\\*.wav', 'themes\\sounds'),
                ('themes\\colors.conf', 'themes'),
                ('themes\\tasktracker.conf', 'themes'),
                ('database\\tt_schema.sql', 'database'),
				('layouts\\*.kv', 'layouts'),
				('tasktracker.ico', '.'),
                ('..\\readme.md', '.')],
             hiddenimports=['win32timezone'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='tasktracker-0.1-beta',
          debug=False,
          strip=False,
          upx=True,
          console=False,
		  icon='tasktracker\\tasktracker.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
			   *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins + gstreamer.dep_bins)],
               strip=False,
               upx=True,
               name='tasktracker')
