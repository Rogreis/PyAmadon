from __future__ import annotations
from .tbar_0base import ToolBar_Base
from i18n import _

class ToolBar_Documentos(ToolBar_Base):
    def GenerateData(self) -> str:  # noqa: N802
        self._log_info("log.open.documentos")
        self._status_curto("status.curto.doc")
        self._status_principal("status.msg.documentos")
        return _("status.msg.documentos")