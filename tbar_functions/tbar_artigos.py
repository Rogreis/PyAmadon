from __future__ import annotations
from .tbar_0base import ToolBar_Base
from i18n import _

class ToolBar_Artigos(ToolBar_Base):
    def GenerateData(self) -> str:  # noqa: N802
        self._log_info("log.open.artigos")
        self._status_curto("status.curto.art")
        self._status_principal("status.msg.artigos")
        return _("status.msg.artigos")