from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hiddenimports = collect_submodules('xhtml2pdf')
hiddenimports += collect_submodules('PIL')
hiddenimports += collect_submodules('reportlab')
hiddenimports=['reportlab.graphics.barcode.code128'],
hiddenimports += collect_submodules('matplotlib')
hiddenimports += [
    'html5lib', 'pypdf', 'svglib', 'webencodings', 'olefile',
    'numpy', 'dateutil', 'tzlocal', 'pytz', 'pyparsing',
    'pkg_resources.py2_warn', 'distutils'
]

datas = collect_data_files('xhtml2pdf')
datas += collect_data_files('PIL')
datas += collect_data_files('reportlab')
datas += collect_data_files('matplotlib')
datas += [('templates/temp_template.html', 'templates'), ('templates/vde_template.html', 'templates')]