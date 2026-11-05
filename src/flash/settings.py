#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?                        __  __  _
#?             ________  / /_/ /_(_)___  ____ ______
#?            / ___/ _ \/ __/ __/ / __ \/ __ `/ ___/
#?           (__  )  __/ /_/ /_/ / / / / /_/ (__  )
#?          /____/\___/\__/\__/_/_/ /_/\__, /____/
#?                                    /____/
#?
#?
#? Name:        settings.py
#? Purpose:     Persist widget values automatically and export/import them as JSON profiles.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    __future__                  import  annotations

import  json
from    pathlib                     import  Path
from    typing                      import  Any

from    PySide6.QtCore              import  QSettings
from    PySide6.QtWidgets           import  QCheckBox, QComboBox, QLineEdit, QSpinBox, QWidget

from    flash                       import  APP_NAME, ORG_NAME
#?----------------------------------------------------------------------------------------------------------------------------------------
def app_settings() -> QSettings:
    return QSettings(ORG_NAME, APP_NAME)
#?----------------------------------------------------------------------------------------------------------------------------------------
class StateStore:
    """Registry of ``key -> widget``. Values survive restarts and can be saved to profiles."""

    PROFILE_VERSION         = 1

    def __init__(self) -> None:
        self._widgets: dict[str, QWidget] = {}
        self._extra: dict[str, tuple[callable, callable]] = {}

    def bind(self, key: str, widget: QWidget) -> QWidget:
        self._widgets[key]  = widget
        return widget

    def bind_custom(self, key: str, getter, setter) -> None:
        """Bind a value that is not a single widget (e.g. the firmware image table)."""
        self._extra[key]    = (getter, setter)

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Values
    #?------------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _get(widget: QWidget) -> Any:
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        if isinstance(widget, QComboBox):
            return widget.currentText()
        if isinstance(widget, QSpinBox):
            return widget.value()
        if isinstance(widget, QLineEdit):
            return widget.text()
        raise TypeError(type(widget))

    @staticmethod
    def _set(widget: QWidget, value: Any) -> None:
        if value is None:
            return
        if isinstance(widget, QCheckBox):
            widget.setChecked(value in (True, "true", "1", 1))
        elif isinstance(widget, QComboBox):
            text            = str(value)
            idx             = widget.findText(text)
            if idx >= 0:
                widget.setCurrentIndex(idx)
            elif widget.isEditable():
                widget.setEditText(text)
        elif isinstance(widget, QSpinBox):
            try:
                widget.setValue(int(value))
            except (TypeError, ValueError):
                pass
        elif isinstance(widget, QLineEdit):
            widget.setText(str(value))

    def to_dict(self) -> dict[str, Any]:
        data                = {k: self._get(w) for k, w in self._widgets.items()}
        for k, (getter, _) in self._extra.items():
            data[k]         = getter()
        return data

    def from_dict(self, data: dict[str, Any]) -> None:
        for k, w in self._widgets.items():
            if k in data:
                self._set(w, data[k])
        for k, (_, setter) in self._extra.items():
            if k in data:
                setter(data[k])

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Persistence
    #?------------------------------------------------------------------------------------------------------------------------------------
    def save(self) -> None:
        s                   = app_settings()
        s.setValue("state/json", json.dumps(self.to_dict()))
        s.sync()

    def restore(self) -> None:
        raw                 = app_settings().value("state/json")
        if not raw:
            return
        try:
            self.from_dict(json.loads(raw))
        except (ValueError, TypeError):
            pass

    def export_profile(self, path: str | Path) -> None:
        payload             = {"app": APP_NAME, "version": self.PROFILE_VERSION, "values": self.to_dict()}
        Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def import_profile(self, path: str | Path) -> None:
        payload             = json.loads(Path(path).read_text(encoding="utf-8"))
        values              = payload.get("values", payload) if isinstance(payload, dict) else {}
        self.from_dict(values)
#?----------------------------------------------------------------------------------------------------------------------------------------
