"""
FileZen – GUI para Linux (PySide6)
Funcionalidades:
  • Selecionar pastas e executar o organizador
  • Visualizar logs em tempo real
  • Editar config.json dentro da GUI
  • Agendamento periódico (timer interno)
"""

import json
import os
import sys
import glob
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import (
    Qt, QThread, Signal, QTimer, QSize
)
from PySide6.QtGui import (
    QFont, QIcon, QColor, QPalette, QAction
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QTabWidget, QLabel, QPushButton, QLineEdit,
    QTextEdit, QPlainTextEdit, QListWidget, QListWidgetItem,
    QFileDialog, QMessageBox, QComboBox, QSpinBox,
    QCheckBox, QGroupBox, QSplitter, QStatusBar,
    QToolBar, QSizePolicy, QFrame, QProgressBar,
    QSystemTrayIcon, QMenu, QHeaderView,
    QTreeWidget, QTreeWidgetItem
)

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
LOG_DIR = os.path.join(BASE_DIR, "logs")

sys.path.insert(0, SRC_DIR)
from logger import Logger
from organizer import FileOrganizer

# ---------------------------------------------------------------------------
# Cores / Tema – estilo "flat dark"
# ---------------------------------------------------------------------------
STYLE = """
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', 'Ubuntu', 'Noto Sans', sans-serif;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #313244;
    border-radius: 6px;
    background: #1e1e2e;
}
QTabBar::tab {
    background: #313244;
    color: #a6adc8;
    padding: 8px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}
QTabBar::tab:selected {
    background: #45475a;
    color: #cdd6f4;
    font-weight: bold;
}
QTabBar::tab:hover {
    background: #585b70;
}
QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #74c7ec;
}
QPushButton:pressed {
    background-color: #89dceb;
}
QPushButton:disabled {
    background-color: #45475a;
    color: #6c7086;
}
QPushButton#btnDanger {
    background-color: #f38ba8;
}
QPushButton#btnDanger:hover {
    background-color: #eba0ac;
}
QPushButton#btnSuccess {
    background-color: #a6e3a1;
}
QPushButton#btnSuccess:hover {
    background-color: #94e2d5;
}
QLineEdit, QSpinBox, QComboBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 10px;
}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #89b4fa;
}
QPlainTextEdit, QTextEdit {
    background-color: #181825;
    color: #a6e3a1;
    border: 1px solid #313244;
    border-radius: 6px;
    font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
    font-size: 12px;
    padding: 6px;
}
QGroupBox {
    border: 1px solid #313244;
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 18px;
    font-weight: bold;
    color: #89b4fa;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 6px;
}
QListWidget {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 6px;
    color: #cdd6f4;
    padding: 4px;
}
QListWidget::item {
    padding: 4px 8px;
    border-radius: 4px;
}
QListWidget::item:selected {
    background-color: #45475a;
}
QCheckBox {
    spacing: 8px;
    color: #cdd6f4;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #585b70;
    background: #313244;
}
QCheckBox::indicator:checked {
    background: #89b4fa;
    border-color: #89b4fa;
}
QStatusBar {
    background: #11111b;
    color: #6c7086;
    font-size: 12px;
}
QProgressBar {
    border: none;
    border-radius: 4px;
    background: #313244;
    text-align: center;
    color: #1e1e2e;
    height: 18px;
}
QProgressBar::chunk {
    background-color: #a6e3a1;
    border-radius: 4px;
}
QTreeWidget {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 6px;
    color: #cdd6f4;
}
QTreeWidget::item {
    padding: 3px 0;
}
QTreeWidget::item:selected {
    background-color: #45475a;
}
QHeaderView::section {
    background-color: #313244;
    color: #cdd6f4;
    padding: 4px 8px;
    border: none;
    font-weight: bold;
}
QScrollBar:vertical {
    background: #181825;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #45475a;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #585b70;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
"""


# ---------------------------------------------------------------------------
# Worker thread – executa organizer.run_scan() sem bloquear a UI
# ---------------------------------------------------------------------------
class ScanWorker(QThread):
    log_signal = Signal(str)
    finished_signal = Signal()
    error_signal = Signal(str)

    def __init__(self, config, log_dir):
        super().__init__()
        self.config = config
        self.log_dir = log_dir

    def run(self):
        try:
            logger = GUILogger(self.log_dir, self.log_signal)
            organizer = FileOrganizer(self.config, logger)
            organizer.run_scan()
        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            self.finished_signal.emit()


class GUILogger:
    """Logger que redireciona para o widget via Signal."""
    def __init__(self, log_dir, signal):
        self._real = Logger(log_dir)
        self._signal = signal

    def log_info(self, msg):
        self._real.log_info(msg)
        self._signal.emit(f"[INFO]  {msg}")

    def log_error(self, msg):
        self._real.log_error(msg)
        self._signal.emit(f"[ERRO]  {msg}")

    def log_move(self, filename, source, destination):
        self._real.log_move(filename, source, destination)
        self._signal.emit(f"[MOVE]  '{filename}' → {destination}")


# ---------------------------------------------------------------------------
# Janela Principal
# ---------------------------------------------------------------------------
class FileZenWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FileZen – Organizador de Arquivos")
        self.setMinimumSize(900, 620)
        self.resize(1020, 700)

        self.config = self._load_config()
        self.scan_worker = None
        self.scheduler_timer = QTimer(self)
        self.scheduler_timer.timeout.connect(self._run_scan)
        self._scheduler_active = False

        # ---------- toolbar ----------
        toolbar = QToolBar("Principal")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)

        title_lbl = QLabel("  FileZen")
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #89b4fa;")
        toolbar.addWidget(title_lbl)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        self.status_label = QLabel("Pronto")
        self.status_label.setStyleSheet("color: #a6adc8; padding-right: 10px;")
        toolbar.addWidget(self.status_label)

        # ---------- abas ----------
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tabs.addTab(self._create_organize_tab(), "⚡  Organizar")
        self.tabs.addTab(self._create_logs_tab(), "📋  Logs")
        self.tabs.addTab(self._create_config_tab(), "⚙  Configurações")
        self.tabs.addTab(self._create_schedule_tab(), "🕐  Agendamento")

        # status bar
        self.statusBar().showMessage("FileZen iniciado")

    # ---------------------------------------------------------------
    # Config helpers
    # ---------------------------------------------------------------
    def _load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "monitored_folders": ["Downloads", "Documents"],
            "destination_folder": "Organizados",
            "scan_interval_seconds": 60,
            "organize_by_date": False,
            "extensions": {
                "Imagens": [".jpg", ".jpeg", ".png", ".gif"],
                "Documentos": [".pdf", ".doc", ".docx", ".txt"],
                "Videos": [".mp4", ".mov", ".avi"],
                "Audio": [".mp3", ".wav"],
                "Compactados": [".zip", ".rar"]
            }
        }

    def _save_config(self, config=None):
        cfg = config or self.config
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
        self.config = cfg

    # ---------------------------------------------------------------
    # Aba 1 – Organizar
    # ---------------------------------------------------------------
    def _create_organize_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Pastas monitoradas
        grp_folders = QGroupBox("Pastas Monitoradas")
        gl = QVBoxLayout(grp_folders)

        self.folder_list = QListWidget()
        self.folder_list.setMaximumHeight(140)
        for f in self.config.get("monitored_folders", []):
            self.folder_list.addItem(f)
        gl.addWidget(self.folder_list)

        btn_row = QHBoxLayout()
        btn_add = QPushButton("+ Adicionar Pasta")
        btn_add.clicked.connect(self._add_folder)
        btn_rm = QPushButton("− Remover Selecionada")
        btn_rm.setObjectName("btnDanger")
        btn_rm.clicked.connect(self._remove_folder)
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_rm)
        btn_row.addStretch()
        gl.addLayout(btn_row)
        layout.addWidget(grp_folders)

        # Destino
        grp_dest = QGroupBox("Pasta de Destino")
        dest_lay = QHBoxLayout(grp_dest)
        self.dest_edit = QLineEdit(self.config.get("destination_folder", "Organizados"))
        dest_lay.addWidget(QLabel("Subpasta de destino:"))
        dest_lay.addWidget(self.dest_edit)
        layout.addWidget(grp_dest)

        # Botão executar
        self.btn_run = QPushButton("▶  Executar Organização")
        self.btn_run.setObjectName("btnSuccess")
        self.btn_run.setMinimumHeight(44)
        self.btn_run.setStyleSheet(
            self.btn_run.styleSheet() + "font-size: 15px;"
        )
        self.btn_run.clicked.connect(self._run_scan)
        layout.addWidget(self.btn_run)

        # Progress
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Log rápido
        self.quick_log = QPlainTextEdit()
        self.quick_log.setReadOnly(True)
        self.quick_log.setPlaceholderText("Saída do organizador aparecerá aqui…")
        layout.addWidget(self.quick_log)

        return tab

    def _add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecionar pasta")
        if folder:
            self.folder_list.addItem(folder)
            self._sync_folders_to_config()

    def _remove_folder(self):
        row = self.folder_list.currentRow()
        if row >= 0:
            self.folder_list.takeItem(row)
            self._sync_folders_to_config()

    def _sync_folders_to_config(self):
        folders = [self.folder_list.item(i).text() for i in range(self.folder_list.count())]
        self.config["monitored_folders"] = folders
        self.config["destination_folder"] = self.dest_edit.text() or "Organizados"
        self._save_config()

    def _run_scan(self):
        if self.scan_worker and self.scan_worker.isRunning():
            return

        self._sync_folders_to_config()
        self.quick_log.clear()
        self.btn_run.setEnabled(False)
        self.progress.setVisible(True)
        self.status_label.setText("Organizando…")

        self.scan_worker = ScanWorker(self.config, LOG_DIR)
        self.scan_worker.log_signal.connect(self._on_log_line)
        self.scan_worker.finished_signal.connect(self._on_scan_done)
        self.scan_worker.error_signal.connect(self._on_scan_error)
        self.scan_worker.start()

    def _on_log_line(self, text):
        self.quick_log.appendPlainText(text)

    def _on_scan_done(self):
        self.btn_run.setEnabled(True)
        self.progress.setVisible(False)
        self.status_label.setText("Concluído ✓")
        self.statusBar().showMessage(
            f"Última execução: {datetime.now().strftime('%H:%M:%S')}"
        )

    def _on_scan_error(self, msg):
        self.btn_run.setEnabled(True)
        self.progress.setVisible(False)
        self.status_label.setText("Erro!")
        QMessageBox.critical(self, "Erro", f"Falha na organização:\n{msg}")

    # ---------------------------------------------------------------
    # Aba 2 – Logs
    # ---------------------------------------------------------------
    def _create_logs_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("Arquivo de log:"))
        self.log_combo = QComboBox()
        self.log_combo.setMinimumWidth(280)
        self.log_combo.currentTextChanged.connect(self._load_log_file)
        top_bar.addWidget(self.log_combo)

        btn_refresh_logs = QPushButton("Atualizar")
        btn_refresh_logs.clicked.connect(self._refresh_log_list)
        top_bar.addWidget(btn_refresh_logs)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText("Selecione um arquivo de log acima…")
        layout.addWidget(self.log_view)

        self._refresh_log_list()
        return tab

    def _refresh_log_list(self):
        self.log_combo.blockSignals(True)
        self.log_combo.clear()
        if os.path.isdir(LOG_DIR):
            logs = sorted(glob.glob(os.path.join(LOG_DIR, "*.log")), reverse=True)
            for lf in logs:
                self.log_combo.addItem(os.path.basename(lf), lf)
        self.log_combo.blockSignals(False)
        if self.log_combo.count() > 0:
            self._load_log_file(self.log_combo.currentText())

    def _load_log_file(self, name):
        idx = self.log_combo.currentIndex()
        if idx < 0:
            return
        path = self.log_combo.itemData(idx)
        if path and os.path.isfile(path):
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                self.log_view.setPlainText(f.read())
            # scroll to bottom
            sb = self.log_view.verticalScrollBar()
            sb.setValue(sb.maximum())

    # ---------------------------------------------------------------
    # Aba 3 – Configurações (editor de config.json)
    # ---------------------------------------------------------------
    def _create_config_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ---------- Extensões ----------
        grp_ext = QGroupBox("Mapeamento de Extensões")
        ext_layout = QVBoxLayout(grp_ext)

        self.ext_tree = QTreeWidget()
        self.ext_tree.setHeaderLabels(["Categoria", "Extensões"])
        self.ext_tree.header().setStretchLastSection(True)
        self.ext_tree.setAlternatingRowColors(False)
        self._populate_ext_tree()
        ext_layout.addWidget(self.ext_tree)

        ext_btn_row = QHBoxLayout()
        btn_add_cat = QPushButton("+ Categoria")
        btn_add_cat.clicked.connect(self._add_category)
        btn_add_ext = QPushButton("+ Extensão")
        btn_add_ext.clicked.connect(self._add_extension)
        btn_rm_ext = QPushButton("− Remover")
        btn_rm_ext.setObjectName("btnDanger")
        btn_rm_ext.clicked.connect(self._remove_ext_item)
        ext_btn_row.addWidget(btn_add_cat)
        ext_btn_row.addWidget(btn_add_ext)
        ext_btn_row.addWidget(btn_rm_ext)
        ext_btn_row.addStretch()
        ext_layout.addLayout(ext_btn_row)

        layout.addWidget(grp_ext)

        # ---------- Opções gerais ----------
        grp_opts = QGroupBox("Opções Gerais")
        opts_lay = QGridLayout(grp_opts)

        self.chk_by_date = QCheckBox("Organizar por data (subpastas Ano-Mês)")
        self.chk_by_date.setChecked(self.config.get("organize_by_date", False))
        opts_lay.addWidget(self.chk_by_date, 0, 0, 1, 2)

        opts_lay.addWidget(QLabel("Intervalo de scan (segundos):"), 1, 0)
        self.spin_interval = QSpinBox()
        self.spin_interval.setRange(5, 86400)
        self.spin_interval.setValue(self.config.get("scan_interval_seconds", 60))
        opts_lay.addWidget(self.spin_interval, 1, 1)

        layout.addWidget(grp_opts)

        # ---------- JSON raw ----------
        grp_raw = QGroupBox("Edição Manual (JSON)")
        raw_lay = QVBoxLayout(grp_raw)
        self.json_editor = QPlainTextEdit()
        self.json_editor.setPlaceholderText("config.json aparecerá aqui")
        self.json_editor.setPlainText(json.dumps(self.config, indent=4, ensure_ascii=False))
        self.json_editor.setMaximumHeight(180)
        raw_lay.addWidget(self.json_editor)
        layout.addWidget(grp_raw)

        # ---------- Botões ----------
        btn_row = QHBoxLayout()
        btn_save = QPushButton("💾  Salvar Configurações")
        btn_save.setObjectName("btnSuccess")
        btn_save.clicked.connect(self._save_config_from_ui)
        btn_reload = QPushButton("↻  Recarregar do Disco")
        btn_reload.clicked.connect(self._reload_config_ui)
        btn_row.addStretch()
        btn_row.addWidget(btn_reload)
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

        return tab

    def _populate_ext_tree(self):
        self.ext_tree.clear()
        for cat, exts in self.config.get("extensions", {}).items():
            parent = QTreeWidgetItem([cat, ", ".join(exts)])
            for ext in exts:
                QTreeWidgetItem(parent, ["", ext])
            self.ext_tree.addTopLevelItem(parent)
        self.ext_tree.expandAll()

    def _add_category(self):
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Nova Categoria", "Nome da categoria:")
        if ok and name.strip():
            name = name.strip()
            if name not in self.config.get("extensions", {}):
                self.config.setdefault("extensions", {})[name] = []
                self._populate_ext_tree()

    def _add_extension(self):
        from PySide6.QtWidgets import QInputDialog
        item = self.ext_tree.currentItem()
        if not item:
            QMessageBox.information(self, "Selecione", "Selecione uma categoria primeiro.")
            return
        # Se é filho, subir para o pai
        parent = item.parent() or item
        cat_name = parent.text(0)

        ext, ok = QInputDialog.getText(self, "Nova Extensão", f"Extensão para '{cat_name}' (ex: .pdf):")
        if ok and ext.strip():
            ext = ext.strip().lower()
            if not ext.startswith("."):
                ext = "." + ext
            exts = self.config["extensions"].get(cat_name, [])
            if ext not in exts:
                exts.append(ext)
                self.config["extensions"][cat_name] = exts
                self._populate_ext_tree()

    def _remove_ext_item(self):
        item = self.ext_tree.currentItem()
        if not item:
            return
        if item.parent() is None:
            # remover categoria inteira
            cat = item.text(0)
            reply = QMessageBox.question(
                self, "Confirmar",
                f"Remover toda a categoria '{cat}' e suas extensões?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.config["extensions"].pop(cat, None)
                self._populate_ext_tree()
        else:
            # remover extensão
            ext = item.text(1)
            cat = item.parent().text(0)
            exts = self.config["extensions"].get(cat, [])
            if ext in exts:
                exts.remove(ext)
                self._populate_ext_tree()

    def _save_config_from_ui(self):
        """Tenta salvar o que está no editor JSON; se vazio usa estado da UI."""
        raw = self.json_editor.toPlainText().strip()
        if raw:
            try:
                cfg = json.loads(raw)
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "JSON inválido", f"Erro no JSON:\n{e}")
                return
        else:
            cfg = self.config

        # Guardar opções gerais do UI
        cfg["organize_by_date"] = self.chk_by_date.isChecked()
        cfg["scan_interval_seconds"] = self.spin_interval.value()

        self._save_config(cfg)
        self._populate_ext_tree()
        self.json_editor.setPlainText(json.dumps(self.config, indent=4, ensure_ascii=False))
        self.statusBar().showMessage("Configurações salvas ✓")

    def _reload_config_ui(self):
        self.config = self._load_config()
        self._populate_ext_tree()
        self.chk_by_date.setChecked(self.config.get("organize_by_date", False))
        self.spin_interval.setValue(self.config.get("scan_interval_seconds", 60))
        self.json_editor.setPlainText(json.dumps(self.config, indent=4, ensure_ascii=False))
        # Atualizar aba Organizar também
        self.folder_list.clear()
        for f in self.config.get("monitored_folders", []):
            self.folder_list.addItem(f)
        self.dest_edit.setText(self.config.get("destination_folder", "Organizados"))
        self.statusBar().showMessage("Configurações recarregadas do disco")

    # ---------------------------------------------------------------
    # Aba 4 – Agendamento
    # ---------------------------------------------------------------
    def _create_schedule_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        grp = QGroupBox("Agendamento Automático")
        g_lay = QVBoxLayout(grp)

        desc = QLabel(
            "Ative o agendamento para executar a organização de arquivos\n"
            "automaticamente a cada intervalo definido."
        )
        desc.setStyleSheet("color: #a6adc8;")
        g_lay.addWidget(desc)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Intervalo (segundos):"))
        self.sched_spin = QSpinBox()
        self.sched_spin.setRange(10, 86400)
        self.sched_spin.setValue(self.config.get("scan_interval_seconds", 60))
        row1.addWidget(self.sched_spin)
        row1.addStretch()
        g_lay.addLayout(row1)

        row2 = QHBoxLayout()
        self.btn_sched_start = QPushButton("▶  Iniciar Agendamento")
        self.btn_sched_start.setObjectName("btnSuccess")
        self.btn_sched_start.clicked.connect(self._toggle_scheduler)
        row2.addWidget(self.btn_sched_start)

        self.sched_status = QLabel("⏹  Parado")
        self.sched_status.setStyleSheet("font-size: 14px; margin-left: 12px; color: #f38ba8;")
        row2.addWidget(self.sched_status)
        row2.addStretch()
        g_lay.addLayout(row2)

        self.sched_log = QPlainTextEdit()
        self.sched_log.setReadOnly(True)
        self.sched_log.setPlaceholderText("Log do agendamento aparecerá aqui…")
        g_lay.addWidget(self.sched_log)

        layout.addWidget(grp)

        # Cron helper
        grp_cron = QGroupBox("Dica: Agendar via cron (systemd)")
        cron_lay = QVBoxLayout(grp_cron)
        cron_text = QLabel(
            "Para agendar fora do app, adicione ao crontab:\n\n"
            f"  */5 * * * * cd {BASE_DIR} && .venv/bin/python src/main.py\n\n"
            "Ou crie um timer systemd para maior controle."
        )
        cron_text.setStyleSheet("color: #a6adc8; font-family: monospace; font-size: 12px;")
        cron_text.setTextInteractionFlags(Qt.TextSelectableByMouse)
        cron_text.setWordWrap(True)
        cron_lay.addWidget(cron_text)
        layout.addWidget(grp_cron)

        layout.addStretch()
        return tab

    def _toggle_scheduler(self):
        if self._scheduler_active:
            self.scheduler_timer.stop()
            self._scheduler_active = False
            self.btn_sched_start.setText("▶  Iniciar Agendamento")
            self.btn_sched_start.setObjectName("btnSuccess")
            self.btn_sched_start.setStyleSheet("")  # force refresh
            self.sched_status.setText("⏹  Parado")
            self.sched_status.setStyleSheet("font-size: 14px; margin-left: 12px; color: #f38ba8;")
            self.sched_log.appendPlainText(
                f"[{datetime.now().strftime('%H:%M:%S')}] Agendamento parado."
            )
            self.statusBar().showMessage("Agendamento desativado")
        else:
            interval_sec = self.sched_spin.value()
            self.scheduler_timer.start(interval_sec * 1000)
            self._scheduler_active = True
            self.btn_sched_start.setText("⏹  Parar Agendamento")
            self.btn_sched_start.setObjectName("btnDanger")
            self.btn_sched_start.setStyleSheet("")
            self.sched_status.setText(f"▶  Ativo (a cada {interval_sec}s)")
            self.sched_status.setStyleSheet("font-size: 14px; margin-left: 12px; color: #a6e3a1;")
            self.sched_log.appendPlainText(
                f"[{datetime.now().strftime('%H:%M:%S')}] Agendamento iniciado — intervalo {interval_sec}s"
            )
            self.statusBar().showMessage(f"Agendamento ativo: a cada {interval_sec} segundos")
            # Executa imediatamente a primeira vez
            self._run_scan()


# ---------------------------------------------------------------------------
# Entry-point
# ---------------------------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("FileZen")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)

    window = FileZenWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
