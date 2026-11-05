#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?                              _
#?             ____ ___  ____ _(_)___
#?            / __ `__ \/ __ `/ / __ \
#?           / / / / / / /_/ / / / / /
#?          /_/ /_/ /_/\__,_/_/_/ /_/
#?
#?
#? Name:        main.py
#? Purpose:     Launcher: ``python main.py`` runs Flash straight from a source checkout.
#?              If the interpreter running this file lacks the dependencies (for example the global Python with the wrong
#?              ``serial`` package installed) and the project's ``.venv`` exists, it relaunches itself with the venv. It is
#?              also the PyInstaller entry script (see flash.spec).
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
import  os
import  subprocess
import  sys
from    pathlib                     import  Path
#?----------------------------------------------------------------------------------------------------------------------------------------
ROOT                        = Path(__file__).resolve().parent
SRC                         = ROOT / "src"
if SRC.is_dir() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
#?----------------------------------------------------------------------------------------------------------------------------------------
def _missing_dependency() -> str | None:
    try:
        import  serial
        if not hasattr(serial, "Serial"):
            return ("the PyPI package 'serial' is shadowing 'pyserial' "
                    "(fix: pip uninstall serial && pip install --force-reinstall pyserial)")
        import  esptool                                                                # noqa: F401
        import  PySide6.QtWidgets                                                      # noqa: F401
    except ImportError as exc:
        return f"missing dependency: {exc.name or exc}"
    return None
#?----------------------------------------------------------------------------------------------------------------------------------------
def _venv_python() -> Path:
    if os.name == "nt":
        return ROOT / ".venv" / "Scripts" / "python.exe"
    return ROOT / ".venv" / "bin" / "python"
#?----------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if not getattr(sys, "frozen", False) and (problem := _missing_dependency()):
        venv                = _venv_python()
        if venv.exists() and Path(sys.executable).resolve() != venv.resolve():
            raise SystemExit(subprocess.call([str(venv), str(Path(__file__).resolve()), *sys.argv[1:]]))
        setup               = r"scripts\setup_venv.ps1" if os.name == "nt" else "scripts/setup_venv.sh"
        sys.stderr.write(f"Flash cannot start: {problem}\nCreate the environment with: {setup}\n")
        raise SystemExit(1)

    from    flash.app                   import  main
    raise SystemExit(main())
#?----------------------------------------------------------------------------------------------------------------------------------------
