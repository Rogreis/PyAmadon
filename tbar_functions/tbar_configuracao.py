from tbar_functions.tbar_0base import ToolBar_Base
from i18n import _
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QCheckBox, QMessageBox, QApplication, QPlainTextEdit, QSpinBox, QLineEdit
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QGroupBox, QFormLayout, QTabWidget, QWidget
from PySide6.QtCore import Qt
from app_settings import settings, apply_global_theme
import json, os, hashlib, threading, urllib.request, time


class ToolBar_Configuracao(ToolBar_Base):
    def __init__(self, context=None):
        super().__init__(context)
        self._log_info("log.open.configuracao")
        self._status_curto("status.curto.cfg")
    # Remove mensagem antiga de placeholder
        # Conteúdo informativo para painel (HTML somente gerado em GenerateData)
        self._left_css = "body{font-family:'Segoe UI';color:#124;} h2{color:#0a3d7a;border-bottom:1px solid #cbd3df;margin-top:0;} ul{padding-left:18px;} li{margin:3px 0;}"
        # Lista de fontes sugeridas (pode evoluir para leitura dinâmica do sistema)
        # Lista base existente permanece dinâmica; adicionaremos Lato e Roboto Condensed se carregadas
        base_fonts = [
            "Segoe UI", "Arial", "Calibri", "Georgia", "Verdana",
            "Tahoma", "Times New Roman", "Trebuchet MS", "Noto Sans", "Open Sans"
        ]
        # Apenas adiciona novas fontes se disponíveis localmente (previamente carregadas em main)
        # Garante presença de Lato e Roboto Condensed na lista (serão carregadas em main se arquivos forem adicionados)
        self._font_options = base_fonts + ["Lato", "Roboto Condensed"]
        # Ordena alfabeticamente (case-insensitive) e remove duplicatas preservando ordem original antes do sort via dict
        self._font_options = sorted(dict.fromkeys(self._font_options), key=lambda s: s.lower())

    def GenerateData(self) -> str:  # noqa: N802
        # Apenas gera HTML (não abre diálogo, não injeta)
        body = f"""
        <div class='p-3'>
            <h2>{_("html.config.title")}</h2>
            <p>{_("html.config.intro")}</p>
            <p><i>Use o botão de configuração para alterar preferências.</i></p>
            <ul>
                <li>Layout</li>
                <li>Idioma</li>
                <li>Fonte</li>
                <li>Temas futuros</li>
            </ul>
        </div>
        """
        return body

    def Show(self):  # noqa: N802
        if self.context is None:
            return
        try:
            dialog = QDialog(self.context)
            dialog.setWindowTitle(_("toolbar.configuracao"))
            dialog.setModal(True)
            dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
            layout = QVBoxLayout(dialog)

            tabs = QTabWidget(dialog)
            layout.addWidget(tabs, 1)

            # --- Tab Traduções ---
            tab_trans = QWidget()
            tab_trans_layout = QVBoxLayout(tab_trans)
            tab_trans_layout.setContentsMargins(8,8,8,8)
            tab_trans_layout.setSpacing(10)

            # --- Tab Configuração Geral ---
            tab_cfg = QWidget()
            tab_cfg_layout = QVBoxLayout(tab_cfg)
            tab_cfg_layout.setContentsMargins(8,8,8,8)
            tab_cfg_layout.setSpacing(10)

            # --- Tab Buscas (nova) ---
            tab_buscas = QWidget()
            tab_buscas_layout = QVBoxLayout(tab_buscas)
            tab_buscas_layout.setContentsMargins(8,8,8,8)
            tab_buscas_layout.setSpacing(10)
            lbl_buscas = QLabel(_("tab.buscas.placeholder"), tab_buscas)
            lbl_buscas.setWordWrap(True)
            tab_buscas_layout.addWidget(lbl_buscas)
            # Grupo de configurações de buscas
            buscas_group = QGroupBox(_("config.search.group"), tab_buscas)
            buscas_form = QFormLayout(buscas_group)
            buscas_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
            # Campo: Máximo de itens (QSpinBox)
            spn_max_items = QSpinBox(buscas_group)
            spn_max_items.setRange(10, 300)
            spn_max_items.setSingleStep(10)
            spn_max_items.setValue(max(10, min(300, getattr(settings, 'search_max_items', 200) or 200)))
            spn_max_items.setToolTip(_("config.search.max_items.tip"))
            buscas_form.addRow(_("config.search.max_items")+":", spn_max_items)
            # Campo: habilitar busca semântica (checkbox)
            chk_semantic = QCheckBox(_("config.search.semantic"), buscas_group)
            chk_semantic.setChecked(bool(getattr(settings, 'search_semantic_enabled', False)))
            chk_semantic.setToolTip(_("config.search.semantic.tip"))
            buscas_form.addRow("", chk_semantic)
            tab_buscas_layout.addWidget(buscas_group)
            tab_buscas_layout.addStretch(1)

            # --- Tab Tradução em Execução (nova) ---
            tab_tr_exec = QWidget()
            tab_tr_exec_layout = QVBoxLayout(tab_tr_exec)
            tab_tr_exec_layout.setContentsMargins(8,8,8,8)
            tab_tr_exec_layout.setSpacing(10)
            lbl_tr_exec = QLabel(_("tab.traducao.execucao.placeholder"), tab_tr_exec)
            lbl_tr_exec.setWordWrap(True)
            tab_tr_exec_layout.addWidget(lbl_tr_exec)
            # Placeholders - serão preenchidos após carregamento de available_translations
            chk_edit_enable = None
            edit_group = None
            cmb_edit_translation = None
            txt_repo_base = None

            # Checkbox Dark Mode
            chk_dark = QCheckBox(_("config.darkmode.label"), tab_cfg)
            chk_dark.setChecked(settings.dark_mode)
            chk_dark.setToolTip(_("config.darkmode.tooltip"))
            tab_cfg_layout.addWidget(chk_dark)

            def _instant_toggle(state: int):
                desired = state == 2
                if desired != settings.dark_mode:
                    settings.dark_mode = desired
                    from PySide6.QtWidgets import QApplication
                    app = QApplication.instance()
                    if app:
                        apply_global_theme(app)
                        try:
                            if hasattr(self.context, '_update_embedded_docs_theme'):
                                self.context._update_embedded_docs_theme()
                        except Exception:
                            pass
                    settings.save()

            chk_dark.stateChanged.connect(_instant_toggle)  # type: ignore
            # Removido label descritivo (tooltip substitui)

            # --- Seleção de Fonte ---
            font_inline = QHBoxLayout()
            font_label = QLabel(_("config.font.label"), tab_cfg)
            font_label.setStyleSheet("font-weight:bold;")
            font_inline.addWidget(font_label)
            cmb_font = QComboBox(tab_cfg)
            cmb_font.setToolTip(_("config.font.tooltip"))
            for f in self._font_options:
                cmb_font.addItem(f)
            try:
                idx = self._font_options.index(settings.font_family)
                cmb_font.setCurrentIndex(idx)
            except Exception:
                pass
            font_inline.addWidget(cmb_font, 1)
            font_inline.addStretch(1)
            tab_cfg_layout.addLayout(font_inline)

            def _apply_font_change(new_font: str):
                changed = new_font != settings.font_family
                settings.font_family = new_font
                # Reaplica stylesheet global
                from PySide6.QtWidgets import QApplication
                app = QApplication.instance()
                if app:
                    apply_global_theme(app)
                # Atualiza webviews existentes com JS que altera body font-family
                try:
                    if hasattr(self.context, 'left_panel') and self.context.left_panel:
                        self._update_webview_font(self.context.left_panel, new_font)
                    if hasattr(self.context, 'right_panel') and self.context.right_panel:
                        self._update_webview_font(self.context.right_panel, new_font)
                except Exception:
                    pass
                settings.save()
                if changed:
                    from mensagens import AmadonLogging
                    try:
                        AmadonLogging.info(self.context, _("config.font.applied").format(font=new_font))
                    except Exception:
                        pass

            def on_font_change(index: int):  # noqa: ARG001
                fnt = cmb_font.currentText().strip()
                if fnt:
                    _apply_font_change(fnt)
            cmb_font.currentIndexChanged.connect(on_font_change)  # type: ignore

            # --- Seleção de Traduções (até 3 slots) ---
            translations_box = QGroupBox(_("config.translations.section"), tab_trans)
            translations_layout = QVBoxLayout(translations_box)
            translations_layout.setContentsMargins(8,8,8,8)
            translations_layout.setSpacing(6)
            # Descrição removida em favor de tooltips nos combos

            form = QFormLayout()
            form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
            # Carrega AvailableTranslations.json (estrutura esperada: lista de objetos com campos id/descricao/... )
            available_translations: list[dict] = []
            # Prioriza arquivo baixado em 'downloads', depois fallback em 'resources'
            candidate_paths = [
                os.path.join('downloads', 'AvailableTranslations.json'),
                os.path.join('resources', 'AvailableTranslations.json')
            ]
            for translations_path in candidate_paths:
                if not os.path.exists(translations_path):
                    continue
                try:
                    with open(translations_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Estrutura esperada: { "AvailableTranslations": [ ... ] }
                        if isinstance(data, dict) and isinstance(data.get('AvailableTranslations'), list):
                            for item in data['AvailableTranslations']:
                                if isinstance(item, dict) and ('Description' in item or 'descricao' in item):
                                    available_translations.append(item)
                            break  # já carregou com sucesso
                        # Fallback: se for lista direta
                        elif isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict) and ('Description' in item or 'descricao' in item):
                                    available_translations.append(item)
                            break
                except Exception:
                    continue

            # Localiza índices preferenciais por Description (case-insensitive)
            english_idx = -1
            portuguese_alt_idx = -1
            for idx, item in enumerate(available_translations):
                desc_raw = str(item.get('Description') or item.get('descricao') or '')
                low = desc_raw.lower()
                if english_idx == -1 and low == 'english 2009':
                    english_idx = idx
                if portuguese_alt_idx == -1 and low == 'portuguese alternative':
                    portuguese_alt_idx = idx

            # Agora que available_translations está carregado, construir painel de edição de tradução
            try:
                from PySide6.QtWidgets import QCheckBox as _QB, QGroupBox as _GB, QFormLayout as _FL, QComboBox as _CB, QLineEdit as _LE
                # Usamos um dicionário container para guardar referências mutáveis dentro deste escopo
                edit_refs = {}
                chk_edit_enable_local = _QB(_("config.trx.edit.enable"), tab_tr_exec)
                chk_edit_enable_local.setChecked(bool(getattr(settings, 'translation_edit_enabled', False)))
                chk_edit_enable_local.setToolTip(_("config.trx.edit.enable.tip"))
                tab_tr_exec_layout.addWidget(chk_edit_enable_local)
                edit_group_local = _GB(_("config.trx.edit.group"), tab_tr_exec)
                edit_form = _FL(edit_group_local)
                edit_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
                cmb_edit_translation_local = _CB(edit_group_local)
                cmb_edit_translation_local.setToolTip(_("config.trx.edit.translation.tip"))
                cmb_edit_translation_local.addItem(_("config.translation.none"), -1)
                for t_idx, t_item in enumerate(available_translations):
                    desc = (t_item.get('descricao') or t_item.get('Description') or t_item.get('description') or t_item.get('desc') or f"Item {t_idx}")
                    lang_id = None
                    try:
                        raw_id = t_item.get('LanguageID') if isinstance(t_item, dict) else getattr(t_item, 'LanguageID', None)
                        if raw_id is not None:
                            lang_id = int(raw_id)
                    except Exception:
                        lang_id = None
                    if lang_id is None:
                        lang_id = t_idx
                    cmb_edit_translation_local.addItem(desc, lang_id)
                initial_edit_id = getattr(settings, 'translation_edit_target', -1)
                for i_c in range(cmb_edit_translation_local.count()):
                    if cmb_edit_translation_local.itemData(i_c) == initial_edit_id:
                        cmb_edit_translation_local.setCurrentIndex(i_c)
                        break
                edit_form.addRow(_("config.trx.edit.translation")+":", cmb_edit_translation_local)
                txt_repo_base_local = _LE(edit_group_local)
                txt_repo_base_local.setPlaceholderText(_("config.trx.edit.repo.placeholder"))
                txt_repo_base_local.setToolTip(_("config.trx.edit.repo.tip"))
                txt_repo_base_local.setText(getattr(settings, 'translation_edit_repo_base', "") or "")
                edit_form.addRow(_("config.trx.edit.repo")+":", txt_repo_base_local)
                tab_tr_exec_layout.addWidget(edit_group_local)
                tab_tr_exec_layout.addStretch(1)
                edit_group_local.setVisible(chk_edit_enable_local.isChecked())
                def _toggle_edit_group2(_state: int):
                    try:
                        edit_group_local.setVisible(chk_edit_enable_local.isChecked())
                    except Exception:
                        pass
                chk_edit_enable_local.stateChanged.connect(_toggle_edit_group2)  # type: ignore
                controls_to_disable.extend([chk_edit_enable_local, cmb_edit_translation_local, txt_repo_base_local])
                # Guarda em edit_refs para acesso no _on_finished
                edit_refs['chk'] = chk_edit_enable_local
                edit_refs['cmb'] = cmb_edit_translation_local
                edit_refs['repo'] = txt_repo_base_local
            except Exception:
                edit_refs = {}
            # Helper para criar combo com ajustes específicos por slot
            def build_translation_combo(label_key: str, slot_attr: str, tip_key: str, allow_none: bool, force_default_idx: int|None=None, fallback_default_idx: int|None=None) -> QComboBox:
                cmb = QComboBox(translations_box)
                cmb.setToolTip(_(tip_key))
                # Lista ordenada (descricao, idxOriginal)
                display_items: list[tuple[str,int]] = []
                for idx, item in enumerate(available_translations):
                    desc = (
                        item.get('descricao') or item.get('Description') or item.get('description') or
                        item.get('desc') or f"Item {idx}"
                    )
                    display_items.append((desc, idx))
                display_items.sort(key=lambda x: x[0].lower())
                if allow_none:
                    cmb.addItem(_("config.translation.none"), -1)
                for desc, original_idx in display_items:
                    cmb.addItem(desc, original_idx)
                # Determina valor salvo
                current_val = getattr(settings, slot_attr, -1)
                # Aplica lógica de default forçado (slot1 deve ser English 2009)
                if force_default_idx is not None:
                    # Se ainda não selecionado (valor -1 ou inválido), define para default
                    if current_val == -1 or all(cmb.itemData(i) != current_val for i in range(cmb.count())):
                        current_val = force_default_idx
                        setattr(settings, slot_attr, current_val)
                        settings.save()
                elif (current_val == -1 or all(cmb.itemData(i) != current_val for i in range(cmb.count()))) and fallback_default_idx is not None:
                    # Usa fallback (ex.: Portuguese Alternative para slot2)
                    current_val = fallback_default_idx
                    setattr(settings, slot_attr, current_val)
                    settings.save()
                # Seleciona no combo
                for i in range(cmb.count()):
                    if cmb.itemData(i) == current_val:
                        cmb.setCurrentIndex(i)
                        break
                form.addRow(_(label_key)+":", cmb)
                return cmb

            # Slot1: sem opção Nenhuma, default = English 2009
            cmb_slot1 = build_translation_combo(
                "config.translation.slot1",
                'translation_slot1',
                'config.translation.slot1.tip',
                allow_none=False,
                force_default_idx=english_idx if english_idx != -1 else (0 if available_translations else None)
            )
            # Slot2: com opção Nenhuma, fallback default = Portuguese Alternative se ainda não escolhido
            cmb_slot2 = build_translation_combo(
                "config.translation.slot2",
                'translation_slot2',
                'config.translation.slot2.tip',
                allow_none=True,
                fallback_default_idx=portuguese_alt_idx if portuguese_alt_idx != -1 else -1
            )
            # Slot3: com opção Nenhuma, sem default especial
            cmb_slot3 = build_translation_combo(
                "config.translation.slot3",
                'translation_slot3',
                'config.translation.slot3.tip',
                allow_none=True
            )

            # Prevenção de duplicação entre combos
            translation_combo_map = {
                cmb_slot1: 'translation_slot1',
                cmb_slot2: 'translation_slot2',
                cmb_slot3: 'translation_slot3'
            }

            def _on_translation_change(changed_cmb: QComboBox):
                val = changed_cmb.itemData(changed_cmb.currentIndex())
                if not isinstance(val, int):
                    return
                # Atualiza setting do combo alterado
                setattr(settings, translation_combo_map[changed_cmb], val)
                # Se valor válido e diferente de -1, remove duplicações em outros
                if val != -1:
                    for other_cmb, attr in translation_combo_map.items():
                        if other_cmb is changed_cmb:
                            continue
                        other_val = other_cmb.itemData(other_cmb.currentIndex())
                        if other_val == val:
                            # Reset regra: se o outro permitir '- Nenhuma -' mantém index 0, senão mantém default (slot1)
                            if other_cmb is cmb_slot1:
                                # Força slot1 a continuar com English 2009 (já está), então revertimos alteração atual
                                # Reverter mudança: restaurar slot1 e colocar changed_cmb em none se permitido
                                if changed_cmb is not cmb_slot1:
                                    # Se changed_cmb permite none, manda para none; caso contrário, ignora
                                    if changed_cmb is not cmb_slot1 and changed_cmb is not None:
                                        # Procura opção none (-1)
                                        for i in range(changed_cmb.count()):
                                            if changed_cmb.itemData(i) == -1:
                                                changed_cmb.setCurrentIndex(i)
                                                setattr(settings, translation_combo_map[changed_cmb], -1)
                                                break
                                # Não altera slot1
                            else:
                                # other_cmb não é slot1 -> envia para none (index 0) se existir
                                if other_cmb.itemData(0) == -1:
                                    other_cmb.setCurrentIndex(0)
                                    setattr(settings, attr, -1)
                settings.save()

            for c in translation_combo_map.keys():
                c.currentIndexChanged.connect(lambda _i, cmb=c: _on_translation_change(cmb))  # type: ignore
            translations_layout.addLayout(form)
            tab_trans_layout.addWidget(translations_box)
            tab_trans_layout.addStretch(1)
            tab_cfg_layout.addStretch(1)

            tabs.addTab(tab_trans, _("config.tab.translations"))
            tabs.addTab(tab_cfg, _("config.tab.general"))
            # Novas abas adicionadas ao final conforme solicitado
            tabs.addTab(tab_buscas, _("tab.buscas.title"))
            tabs.addTab(tab_tr_exec, _("tab.traducao.execucao.title"))

            # Removido botão Aplicar (aplicação imediata). Mantém apenas Fechar.
            btn_close = QPushButton(_("config.close"), dialog)
            btn_close.setToolTip(_("config.close.tip"))
            btn_close.clicked.connect(dialog.accept)
            btn_retry = QPushButton(_("config.translations.retry.button"), dialog)
            btn_retry.setToolTip(_("config.translations.retry.button.tip"))
            btn_retry.setVisible(False)
            btn_retry.setEnabled(True)
            buttons_row = QHBoxLayout()
            buttons_row.addWidget(btn_close)
            buttons_row.addWidget(btn_retry)
            buttons_row.addStretch(1)
            layout.addLayout(buttons_row)
            # Área de log de mensagens (lista cumulativa)
            log_box = QPlainTextEdit(dialog)
            log_box.setReadOnly(True)
            log_box.setMaximumBlockCount(500)
            log_box.setStyleSheet("font-family:Consolas,Monaco,monospace;font-size:11px;background:#10151a;color:#e0e6ee;border:1px solid #2c3e50;padding:4px;border-radius:4px;")
            # Insere abaixo das tabs
            layout.insertWidget(1, log_box, 1)

            class _TransSignals(QObject):
                progress = Signal(str)                    # mensagens intermediárias
                finished = Signal(bool, list)             # sucesso geral, lista de índices que falharam
            _signals = _TransSignals()

            def _verify_and_download():
                try:
                    AmadonLogging = None
                    try:
                        from mensagens import AmadonLogging as _AL
                        AmadonLogging = _AL
                    except Exception:
                        pass
                    if AmadonLogging:
                        AmadonLogging.info(self.context, _("config.translations.check.start"))
                    # Map idxOriginal -> item dict
                    idx_map = {i: it for i, it in enumerate(available_translations)}
                    slots = [settings.translation_slot1, settings.translation_slot2, settings.translation_slot3]
                    any_download = False
                    had_failure = False
                    failed_indices: list[int] = []
                    for slot_val in slots:
                        if slot_val is None or slot_val < 0:
                            continue
                        item = idx_map.get(slot_val)
                        if not item:
                            continue
                        # Determina o LanguageID de forma robusta (converte para int; fallback = slot_val)
                        try:
                            lang_raw = item.get('LanguageID') if isinstance(item, dict) else getattr(item, 'LanguageID', slot_val)
                        except Exception:
                            lang_raw = slot_val
                        try:
                            lang_id = int(lang_raw)
                        except Exception:
                            lang_id = slot_val if isinstance(slot_val, int) else 0
                        fname = f"TR{lang_id:03d}.gz"
                        local_dir = os.path.join('doc_sources')
                        os.makedirs(local_dir, exist_ok=True)
                        local_path = os.path.join(local_dir, fname)
                        expected_hash = str(item.get('Hash') or item.get('hash') or '').strip().lower()
                        need_download = False
                        if not os.path.exists(local_path):
                            need_download = True
                            if AmadonLogging:
                                AmadonLogging.warning(self.context, _("config.translations.file.missing").format(file=fname))
                        else:
                            if expected_hash:
                                try:
                                    h = hashlib.md5()
                                    with open(local_path, 'rb') as fbin:
                                        for chunk in iter(lambda: fbin.read(65536), b''):
                                            h.update(chunk)
                                    if h.hexdigest().lower() != expected_hash:
                                        need_download = True
                                        if AmadonLogging:
                                            AmadonLogging.warning(self.context, _("config.translations.hash.mismatch").format(file=fname))
                                except Exception:
                                    need_download = True
                        if need_download:
                            any_download = True
                            _signals.progress.emit(_("config.translations.downloading.ui").format(idx=slot_val))
                            # URL definitiva (corrigida para raw.githubusercontent.com)
                            raw_url = f"https://raw.githubusercontent.com/Rogreis/TUB_Files/main/{fname}"
                            max_attempts = 3
                            backoff_base = 1.0
                            for attempt in range(1, max_attempts + 1):
                                start_t = time.monotonic()
                                if AmadonLogging:
                                    # URL e tentativa
                                    try:
                                        AmadonLogging.info(self.context, _("config.translations.download.url").format(idx=slot_val, url=raw_url))
                                    except Exception:
                                        pass
                                    AmadonLogging.info(self.context, _("config.translations.retry.attempt").format(n=attempt, idx=slot_val))
                                try:
                                    with urllib.request.urlopen(raw_url, timeout=45) as resp:
                                        # Verifica status HTTP explicitamente
                                        status_code = getattr(resp, 'status', None) or getattr(resp, 'getcode', lambda: None)()
                                        if status_code and status_code != 200:
                                            raise RuntimeError(f"HTTP {status_code}")
                                        data = resp.read()
                                    # Verifica hash antes de gravar (se houver hash esperado)
                                    if expected_hash:
                                        h2 = hashlib.md5(); h2.update(data)
                                        if h2.hexdigest().lower() != expected_hash:
                                            raise ValueError("MD5 mismatch")
                                    # Escreve somente após validação
                                    with open(local_path, 'wb') as fout:
                                        fout.write(data)
                                    duration = time.monotonic() - start_t
                                    size_bytes = len(data)
                                    if AmadonLogging:
                                        # Log simples de sucesso + detalhado
                                        try:
                                            AmadonLogging.info(self.context, _("config.translations.download.success").format(idx=slot_val))
                                        except Exception:
                                            pass
                                        try:
                                            AmadonLogging.info(self.context, _("config.translations.download.detail").format(idx=slot_val, size=size_bytes, secs=f"{duration:.2f}"))
                                        except Exception:
                                            pass
                                    break  # sucesso
                                except Exception as e:  # noqa: BLE001
                                    duration = time.monotonic() - start_t
                                    if AmadonLogging:
                                        try:
                                            AmadonLogging.warning(self.context, _("config.translations.download.error.url").format(idx=slot_val, url=raw_url, erro=e))
                                        except Exception:
                                            pass
                                    if attempt < max_attempts:
                                        # Backoff exponencial
                                        wait_for = backoff_base * (2 ** (attempt - 1))
                                        if AmadonLogging:
                                            try:
                                                AmadonLogging.info(self.context, _("config.translations.retry.wait").format(secs=int(wait_for), idx=slot_val))
                                            except Exception:
                                                pass
                                        time.sleep(wait_for)
                                    else:
                                        # Última tentativa falhou – registra erro final
                                        if AmadonLogging:
                                            try:
                                                AmadonLogging.error(self.context, _("config.translations.download.error.url").format(idx=slot_val, url=raw_url, erro=e))
                                            except Exception:
                                                pass
                                        # Se arquivo parcial foi criado (não deveria), remove
                                        try:
                                            if os.path.exists(local_path):
                                                os.remove(local_path)
                                        except Exception:
                                            pass
                                        had_failure = True
                                        failed_indices.append(slot_val)
                    if not any_download and AmadonLogging:
                        AmadonLogging.info(self.context, _("config.translations.all.ok"))
                    success_all = not had_failure
                except Exception:
                    # Em caso de exceção não capturada, considera falha geral
                    success_all = False
                    # Em falha abrupta não listada, marcar todos selecionados sem arquivo válido
                    try:
                        sel = [s for s in [settings.translation_slot1, settings.translation_slot2, settings.translation_slot3] if isinstance(s, int) and s >= 0]
                        failed_indices = list(dict.fromkeys(sel))  # unique
                    except Exception:
                        failed_indices = []
                finally:
                    _signals.progress.emit(_("config.translations.done"))
                    try:
                        _signals.finished.emit(success_all, failed_indices)
                    except Exception:
                        pass

            controls_to_disable = [cmb_slot1, cmb_slot2, cmb_slot3, chk_dark]
            try:
                controls_to_disable.append(cmb_font)
            except Exception:
                pass
            # Incluir controles da aba Buscas
            try:
                controls_to_disable.extend([spn_max_items, chk_semantic])
            except Exception:
                pass
            # Incluir controles de edição de tradução
            # (Edição de tradução será adicionada depois que criarmos os controles reais)

            def _set_controls_enabled(flag: bool):
                for w in controls_to_disable:
                    try:
                        w.setEnabled(flag)
                    except Exception:
                        pass
                btn_close.setEnabled(flag)
                # Retry apenas habilitado fora da execução e se houve falha
                if flag and btn_retry.isVisible():
                    btn_retry.setEnabled(True)
                else:
                    btn_retry.setEnabled(False)

            def _start_verification_and_close():
                # Preparar ciclo de verificação
                btn_retry.setVisible(False)
                btn_retry.setEnabled(False)
                _set_controls_enabled(False)
                log_box.appendPlainText("")
                log_box.appendPlainText("== " + _("config.translations.verifying") + " ==")
                threading.Thread(target=_verify_and_download, daemon=True).start()

            def _on_progress(msg: str):
                log_box.appendPlainText(msg)

            def _on_finished(success: bool, failed_indices: list):  # noqa: D401
                # Persistir configurações de buscas (sempre que terminar uma verificação ou tentativa)
                try:
                    new_max = spn_max_items.value()
                    if new_max < 10:
                        new_max = 10
                    elif new_max > 300:
                        new_max = 300
                    settings.search_max_items = new_max
                    settings.search_semantic_enabled = chk_semantic.isChecked()
                    # Persistir configurações de edição de tradução
                    # Persistência de edição de tradução somente se os controles já existirem
                    # Persistência de edição de tradução via referencias dinâmicas
                    try:
                        chk_ref = edit_refs.get('chk')
                        cmb_ref = edit_refs.get('cmb')
                        repo_ref = edit_refs.get('repo')
                        if chk_ref and cmb_ref and repo_ref:
                            settings.translation_edit_enabled = chk_ref.isChecked()
                            sel_id = cmb_ref.itemData(cmb_ref.currentIndex())
                            if isinstance(sel_id, int):
                                settings.translation_edit_target = sel_id
                            else:
                                settings.translation_edit_target = -1
                            settings.translation_edit_repo_base = repo_ref.text().strip()
                    except Exception:
                        pass
                    settings.save()
                except Exception:
                    pass
                if success:
                    log_box.appendPlainText(_("config.translations.summary.success"))
                    dialog.accept()
                else:
                    log_box.appendPlainText(_("config.translations.summary.failure"))
                    if failed_indices:
                        try:
                            ids_fmt = ", ".join(f"TR{idx:03d}" for idx in failed_indices)
                            log_box.appendPlainText(_("config.translations.summary.failure.list").format(indices=ids_fmt))
                        except Exception:
                            pass
                    # Exibe botão retry e reabilita controles
                    btn_retry.setVisible(True)
                    _set_controls_enabled(True)
                if success:
                    return

            _signals.progress.connect(_on_progress)
            _signals.finished.connect(_on_finished)

            btn_close.clicked.disconnect()
            btn_close.clicked.connect(_start_verification_and_close)
            btn_retry.clicked.connect(_start_verification_and_close)

            dialog.resize(600, 520)
            dialog.exec()
        except Exception:
            pass

    def _update_webview_font(self, panel, font):
        """Aplica fonte às instâncias de QWebEngineView já carregadas."""
        try:
            from PySide6.QtWebEngineWidgets import QWebEngineView  # type: ignore
        except Exception:
            return
        js = f"""
        (function(){{
            try {{
                document.body.style.fontFamily = '{font}';
                const all = document.querySelectorAll('.markdown-body, .doc-body');
                all.forEach(el => el.style.fontFamily = '{font}');
            }} catch(e){{}}
        }})();
        """
        for view in panel.findChildren(QWebEngineView):
            try:
                view.page().runJavaScript(js)
            except Exception:
                pass

    def css_left(self):
        return getattr(self, '_left_css', None)