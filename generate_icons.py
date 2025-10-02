"""Gera ícones (PNG e ICO) para o aplicativo Amadon.
Executar uma vez ou no pipeline antes do PyInstaller.
"""
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QLinearGradient, QPixmap, QIcon, QPainterPath
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
import sys, pathlib

SIZES = [16, 24, 32, 48, 64, 128, 256]


def create_base_pixmap(size: int) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    # Halo
    grad_halo = QLinearGradient(0, 0, 0, size)
    grad_halo.setColorAt(0.0, QColor(255, 255, 255, 0))
    grad_halo.setColorAt(0.5, QColor(90, 120, 200, 35))
    grad_halo.setColorAt(1.0, QColor(40, 60, 120, 70))
    p.setBrush(QBrush(grad_halo))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(size*0.08, size*0.08, size*0.84, size*0.84)

    # Páginas
    left_grad = QLinearGradient(size*0.15, size*0.2, size*0.48, size*0.85)
    left_grad.setColorAt(0.0, QColor(250, 250, 252))
    left_grad.setColorAt(1.0, QColor(225, 228, 235))
    right_grad = QLinearGradient(size*0.52, size*0.2, size*0.85, size*0.85)
    right_grad.setColorAt(0.0, QColor(250, 250, 252))
    right_grad.setColorAt(1.0, QColor(225, 228, 235))

    border_pen = QPen(QColor(40, 70, 140))
    border_pen.setWidth(max(1, size//40))
    p.setPen(border_pen)
    p.setBrush(QBrush(left_grad))
    p.drawRoundedRect(int(size*0.14), int(size*0.18), int(size*0.34), int(size*0.60), size*0.05, size*0.05)
    p.setBrush(QBrush(right_grad))
    p.drawRoundedRect(int(size*0.52), int(size*0.18), int(size*0.34), int(size*0.60), size*0.05, size*0.05)

    # Dobra central
    center_pen = QPen(QColor(60, 90, 160))
    center_pen.setWidth(max(1, size//30))
    p.setPen(center_pen)
    p.drawLine(int(size*0.50), int(size*0.18), int(size*0.50), int(size*0.78))

    # Linhas de texto
    text_pen = QPen(QColor(90, 110, 160))
    text_pen.setWidth(max(1, size//60))
    p.setPen(text_pen)
    line_count = 4 if size < 32 else 5
    for i in range(line_count):
        y = int(size*0.25 + i*size*0.07)
        p.drawLine(int(size*0.18), y, int(size*0.44), y)
        p.drawLine(int(size*0.56), y, int(size*0.82), y)

    # Marcador
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(200, 50, 60, 230))
    marker_x = int(size*0.47)
    marker_w = int(size*0.06)
    marker_y = int(size*0.12)
    marker_h = int(size*0.25)
    p.drawRect(marker_x, marker_y, marker_w, marker_h)
    path = QPainterPath()
    tri_top = marker_y + marker_h
    path.moveTo(marker_x, tri_top)
    path.lineTo(marker_x + marker_w, tri_top)
    path.lineTo(marker_x + marker_w/2, tri_top + int(size*0.09))
    path.closeSubpath()
    p.drawPath(path)

    p.end()
    return pm


def main():
    app = QApplication(sys.argv)
    out_dir = pathlib.Path('assets/icons')
    out_dir.mkdir(parents=True, exist_ok=True)

    png_paths = []
    for sz in SIZES:
        pm = create_base_pixmap(sz)
        png_path = out_dir / f"amadon_{sz}.png"
        pm.save(str(png_path), 'PNG')
        png_paths.append(png_path)
        print(f"Gerado: {png_path}")

    # Criar ícone multi-resolução (.ico) usando maior base + conversão interna
    # QIcon não salva diretamente .ico multi-size; salvamos apenas 256 e deixamos para pipeline se quiser otimização futura
    biggest = create_base_pixmap(256)
    ico_path = out_dir / 'amadon.ico'
    biggest.save(str(ico_path), 'ICO')
    print(f"Gerado: {ico_path}")

    return 0

if __name__ == '__main__':
    raise SystemExit(main())
