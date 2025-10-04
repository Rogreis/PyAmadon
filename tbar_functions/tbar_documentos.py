from tbar_functions.tbar_0base import ToolBar_Base
from i18n import _
from PySide6.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QLineEdit,
    QWidget,
    QVBoxLayout,
)
from pathlib import Path
from PySide6.QtWidgets import QApplication
from document_resolver import resolve_doc_link

class ToolBar_Documentos(ToolBar_Base):
    def __init__(self, context=None):
        super().__init__(context)
        self._log_info("log.open.documentos")
        self._status_curto("status.curto.doc")
        self._status_principal("status.msg.documentos")
        base = Path(__file__).resolve().parent.parent
        css_path = base / 'assets' / 'css' / 'documentos.css'
        js_path = base / 'assets' / 'js' / 'documentos.js'
        tree_json = base / 'assets' / 'data' / 'documentos_tree.json'
        try:
            self._css_external = css_path.read_text(encoding='utf-8')
        except Exception:
            self._css_external = "body{font-family:Segoe UI,Arial,sans-serif;}"
        try:
            self._js_external = js_path.read_text(encoding='utf-8')
        except Exception:
            self._js_external = "console.warn('documentos.js não encontrado');"

        # Monta árvore (widget esquerdo)
        container = QWidget()
        vlayout = QVBoxLayout(container)
        vlayout.setContentsMargins(0, 0, 0, 0)
        vlayout.setSpacing(4)
        filtro = QLineEdit()
        filtro.setPlaceholderText(_("filter.placeholder.documentos"))
        filtro.setClearButtonEnabled(True)
        vlayout.addWidget(filtro)
        tree = QTreeWidget()
        tree.setHeaderHidden(True)
        vlayout.addWidget(tree, 1)
        tree.setStyleSheet("QTreeWidget { border-radius:4px; }")
        self._tree = tree
        self._filter = filtro
        import json
        cls = self.__class__
        if not hasattr(cls, '_cache_data'):
            cls._cache_data = None  # type: ignore[attr-defined]
            cls._cache_mtime = None  # type: ignore[attr-defined]
        try:
            mtime = tree_json.stat().st_mtime
        except Exception:
            mtime = None
        if getattr(cls, '_cache_data') is None or getattr(cls, '_cache_mtime') != mtime:
            try:
                data = json.loads(tree_json.read_text(encoding='utf-8'))
            except Exception:
                data = {"nodes": []}
            setattr(cls, '_cache_data', data)
            setattr(cls, '_cache_mtime', mtime)
        else:
            data = getattr(cls, '_cache_data')
        style = QApplication.instance().style() if QApplication.instance() else None

        def add_nodes(parent_item, nodes, level=0):
            for n in nodes:
                titulo = n.get("titulo", "(sem título)")
                item = QTreeWidgetItem([titulo])
                item.setData(0, 32, n.get("link"))
                if style:
                    if level == 0:
                        item.setIcon(0, style.standardIcon(style.StandardPixmap.SP_DirIcon))
                    elif level == 1:
                        item.setIcon(0, style.standardIcon(style.StandardPixmap.SP_FileDialogListView))
                    else:
                        item.setIcon(0, style.standardIcon(style.StandardPixmap.SP_FileIcon))
                if parent_item:
                    parent_item.addChild(item)
                else:
                    tree.addTopLevelItem(item)
                filhos = n.get("filhos")
                if filhos:
                    add_nodes(item, filhos, level + 1)
        add_nodes(None, data.get("nodes", []))
        tree.expandToDepth(1)

        def on_item_clicked(item: QTreeWidgetItem):
            link = item.data(0, 32) or "(sem link)"
            try:
                from mensagens import AmadonLogging
                AmadonLogging.info(self.context, _("log.open.documentos.node").format(link=link))
            except Exception:
                pass
            resolved = resolve_doc_link(str(link))
            body = f"""
            <div class='container py-3'>
                <h2>{item.text(0)}</h2>
                <p class='text-muted small mb-2'>ID lógico: <code>{link}</code></p>
                <div class='mb-3 doc-content'>{resolved}</div>
                <button id='btnCount' class='btn btn-primary btn-sm'>Clique para contar <span class='badge text-bg-light' id='ctr'>0</span></button>
                <hr/>
                <p class='footer-note text-secondary'>Renderizado em tempo real. Markdown suportado.</p>
            </div>
            """
            self.inject_web_content(body, target='right', clear=True, use_bootstrap=True, css=self._css_external, js=self._js_external)
        tree.itemClicked.connect(on_item_clicked)  # type: ignore

        def apply_filter(text: str):
            pattern = text.strip().lower()
            def match_item(it: QTreeWidgetItem):
                child_match = False
                for i in range(it.childCount()):
                    child = it.child(i)
                    child_visible = match_item(child)
                    child_match = child_match or child_visible
                own = pattern in it.text(0).lower() if pattern else True
                visible = own or child_match
                it.setHidden(not visible)
                return visible
            for i in range(tree.topLevelItemCount()):
                match_item(tree.topLevelItem(i))
        filtro.textChanged.connect(apply_filter)  # type: ignore
        # Injeta painel esquerdo já na criação
        if self.context:
            self.inject_widget(container, target='left', clear=True)

    def GenerateData(self) -> str:  # noqa: N802
        return f"""
        <div class='container py-3'>
            <h2>{_("html.doc.title")}</h2>
            <p class='lead'>{_("html.doc.intro")}</p>
            <p>Selecione um nó da árvore à esquerda para ver detalhes.</p>
        </div>
        """

    def css_right(self):
        return getattr(self, '_css_external', None)

    def js_right(self):
        return getattr(self, '_js_external', None)