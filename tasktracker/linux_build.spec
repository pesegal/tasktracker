# -*- mode: python -*-


from kivy.tools.packaging.pyinstaller_hooks import (
    runtime_hooks, hookspath, get_deps_all, add_dep_paths, excludedimports, datas, get_deps_all,
    get_factory_modules, get_deps_minimal, kivy_modules)

block_cipher = None

deps = get_deps_minimal(video=None)

hidden_imports = deps['hiddenimports']
hidden_imports.extend(
[
	'kivy.weakmethod',
	'kivy.core.audio'
	
])
excludes = deps['excludes']

a = Analysis(['main.py'],
             pathex=['/home/peter/Desktop/tasktracker/tasktracker'],
             binaries=[],
             datas=[
                ('themes/gfx/*.png', 'themes/gfx'),
                ('themes/sounds/*.wav', 'themes/sounds'),
                ('themes/colors.conf', 'themes/'),
                ('themes/tasktracker.conf', 'themes/'),
                ('database/tt_schema.sql', 'database/'),
		('layouts/*.kv', 'layouts/'),
		('tasktracker.ico', '.'),
                ('../readme.md', '.')
             ],
             hookspath=hookspath(),
             hiddenimports=hidden_imports,
             excludes=excludes,
             runtime_hooks=runtime_hooks(),
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher
             )
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='Tasktracker++',
          debug=False,
          strip=False,
          upx=True,
          console=True,
          icon='tasktracker.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='main')
