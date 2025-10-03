from __future__ import annotations
from .tbar_0base import ToolBar_Base
from i18n import _
from PySide6.QtWidgets import QLabel

class ToolBar_Busca(ToolBar_Base):
    def GenerateData(self) -> str:  # noqa: N802
        self._log_info("log.open.busca")
        self._status_curto("status.curto.bus")
        self._status_principal("status.msg.busca")
        body = f"""
        <div style='padding:10px'>
            <h2>{_("html.busca.title")}</h2>
            <p>{_("html.busca.intro")}</p>
            <p><b>Planos:</b></p>
            <ul>
                <li>Indexação incremental</li>
                <li>Busca booleana</li>
                <li>Destaque de termos</li>
            </ul>
        </div>
        """
        self.inject_web_content(body, target='left', css="body{font-family:'Segoe UI';color:#133;} h2{color:#0a3d7a;border-bottom:1px solid #ccd6e2;margin-top:0;} ul{padding-left:18px;} li{margin:3px 0;}")
        return _("status.msg.busca")