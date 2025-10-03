from __future__ import annotations
from .tbar_0base import ToolBar_Base
from i18n import _
from PySide6.QtWidgets import QLabel

class ToolBar_Ajuda(ToolBar_Base):
    def GenerateData(self) -> str:  # noqa: N802
        self._log_info("log.open.ajuda")
        self._status_curto("status.curto.help")
        self._status_principal("status.msg.ajuda")
        body = f"""
        <div class='container py-3'>
            <h2>{_("html.ajuda.title")}</h2>
            <p>{_("html.ajuda.intro")}</p>
            <div class='row g-3'>
                <div class='col-md-4'>
                    <div class='card h-100 shadow-sm'>
                        <div class='card-body'>
                            <h5 class='card-title'>FAQ</h5>
                            <p class='card-text'>Perguntas frequentes e esclarecimentos iniciais.</p>
                            <button class='btn btn-outline-primary btn-sm' onclick="alert('FAQ placeholder');">Abrir</button>
                        </div>
                    </div>
                </div>
                <div class='col-md-4'>
                    <div class='card h-100 shadow-sm'>
                        <div class='card-body'>
                            <h5 class='card-title'>Atalhos</h5>
                            <p class='card-text'>Lista futura de atalhos do sistema.</p>
                            <button class='btn btn-outline-secondary btn-sm' onclick="alert('Atalhos placeholder');">Ver</button>
                        </div>
                    </div>
                </div>
                <div class='col-md-4'>
                    <div class='card h-100 shadow-sm'>
                        <div class='card-body'>
                            <h5 class='card-title'>Sobre</h5>
                            <p class='card-text'>Informações de licenças e créditos.</p>
                            <button class='btn btn-outline-info btn-sm' onclick="alert('Sobre placeholder');">Info</button>
                        </div>
                    </div>
                </div>
            </div>
            <hr/>
            <p class='text-muted small'>Exemplo com Bootstrap 5 + JavaScript inline. Clique no botão abaixo para incrementar:</p>
            <button id='btnCounter' class='btn btn-primary'>Contador <span id='counterBadge' class='badge text-bg-light'>0</span></button>
        </div>
        """
        js = """
        let count = 0; const btn = document.getElementById('btnCounter'); const badge = document.getElementById('counterBadge');
        if(btn && badge){ btn.addEventListener('click', ()=>{ count++; badge.innerText = count; }); }
        """
        self.inject_web_content(body, target='left', use_bootstrap=True, js=js, css="body{font-family:'Segoe UI';} h2{color:#0a3d7a;}")
        return _("status.msg.ajuda")