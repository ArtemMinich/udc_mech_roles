from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtGui import QPixmap, QWheelEvent, QMouseEvent
from PySide6.QtCore import Qt, QPointF


class ImageViewer(QGraphicsView):
    """Віджет для відображення картинки з масштабуванням і перетягуванням."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self._photo = QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def hasPhoto(self):
        return not self._empty

    def setPhoto(self, pixmap: QPixmap = None):
        if pixmap and not pixmap.isNull():
            self._empty = False
            self._photo.setPixmap(pixmap)
            self.fitInView(self._photo, Qt.KeepAspectRatio)
        else:
            self._empty = True
            self._photo.setPixmap(QPixmap())

    def wheelEvent(self, event: QWheelEvent):
        """Масштабування колесиком миші."""
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1

            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView(self._photo, Qt.KeepAspectRatio)
            else:
                self._zoom = 0

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Подвійний клік = скидання масштабу."""
        if self.hasPhoto():
            self._zoom = 0
            self.fitInView(self._photo, Qt.KeepAspectRatio)
