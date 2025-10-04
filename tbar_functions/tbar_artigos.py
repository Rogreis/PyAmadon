from tbar_functions.tbar_0base import ToolBar_Base
from i18n import _

class ToolBar_Artigos(ToolBar_Base):
    def __init__(self, context=None):
        super().__init__(context)
        self._log_info("log.open.artigos")
        self._status_curto("status.curto.art")
        self._status_principal("status.msg.artigos")
        self._css_left = "body{font-family:'Segoe UI';color:#123;} h2{color:#0a3d7a;border-bottom:1px solid #d6dde8;margin-top:0;} ol{padding-left:20px;} li{margin:4px 0;}"

    def GenerateData(self) -> str:  # noqa: N802
        return f"""
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

    def css_left(self):
        return getattr(self, '_css_left', None)