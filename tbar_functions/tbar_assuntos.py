from __future__ import annotations
from .tbar_0base import ToolBar_Base
from i18n import _
from PySide6.QtWidgets import QLabel

class ToolBar_Assuntos(ToolBar_Base):
    def GenerateData(self) -> str:  # noqa: N802
        self._log_info("log.open.assuntos")
        self._status_curto("status.curto.ass")
        self._status_principal("status.msg.assuntos")
        body = f"""
        <div class='p-3'>
            <h2>{_("html.assuntos.title")}</h2>
            <p>{_("html.assuntos.intro")}</p>
            <p><b>Planned:</b></p>
            <ul>
                <li>Taxonomias</li>
                <li>Filtros hierárquicos</li>
                <li>Anotações por assunto</li>
            </ul>
        </div>
        """
        self.inject_web_content(body, target='left', use_bootstrap=False, css="body{font-family:'Segoe UI';color:#122;} h2{color:#0a3d7a;border-bottom:1px solid #d0dbe6;margin-top:0;}")
        return _("status.msg.assuntos")