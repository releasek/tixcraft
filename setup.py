from setuptools import setup, Extension
from Cython.Build import cythonize
import os

# 在這裡列出你想要編譯成 .pyd 的所有核心邏輯檔案
# 我們不編譯 GUI 啟動器 (settings.py)，只編譯它會呼叫的背景邏輯
files_to_compile = [
    "chrome_tixcraft.py", # 你的搶票主程式
    "util.py",
    "NonBrowser.py",
    # 如果未來有其他核心邏輯檔案，也加到這裡
]

# 自動生成 Extension 物件
extensions = [
    Extension(os.path.splitext(py_file)[0], [py_file])
    for py_file in files_to_compile
]

# 執行編譯
setup(
    ext_modules=cythonize(extensions, compiler_directives={'language_level': "3"})
)
