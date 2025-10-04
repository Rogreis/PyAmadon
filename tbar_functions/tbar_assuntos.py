from tbar_functions.tbar_0base import ToolBar_Base
from i18n import _

class ToolBar_Assuntos(ToolBar_Base):
    def __init__(self, context=None):
        super().__init__(context)
        self._log_info("log.open.assuntos")
        self._status_curto("status.curto.ass")
        self._status_principal("status.msg.assuntos")
        self._css_left = "body{font-family:'Segoe UI';color:#122;} h2{color:#0a3d7a;border-bottom:1px solid #d0dbe6;margin-top:0;}"

    def GenerateData(self) -> str:  # noqa: N802
        return f"""
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

    def css_left(self):
        return getattr(self, '_css_left', None)