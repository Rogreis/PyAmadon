from __future__ import annotations
from .tbar_0base import ToolBar_Base
from i18n import _
from PySide6.QtWidgets import QLabel

class ToolBar_Artigos(ToolBar_Base):
    def GenerateData(self) -> str:  # noqa: N802
        self._log_info("log.open.artigos")
        self._status_curto("status.curto.art")
        self._status_principal("status.msg.artigos")
        body = f"""
        <div style='padding:12px'>
            <h2>{_("html.artigos.title")}</h2>
            <p>{_("html.artigos.intro")}</p>
            <ol>
                <li>Planejamento de indexação</li>
                <li>Referências cruzadas</li>
                <li>Exportação (PDF/HTML)</li>
            </ol>
        </div>
        """
        self.inject_web_content(body, target='left', css="body{font-family:'Segoe UI';color:#123;} h2{color:#0a3d7a;border-bottom:1px solid #d6dde8;margin-top:0;} ol{padding-left:20px;} li{margin:4px 0;}")
        return _("status.msg.artigos")