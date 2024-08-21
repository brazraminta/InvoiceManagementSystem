from cx_Freeze import setup, Executable

setup(
    name = "main_MS_Access",
    version = "0.1",
    description = "Sąskaitų registro programa",
    executables = [Executable("main_MS_Access.py")],
)
