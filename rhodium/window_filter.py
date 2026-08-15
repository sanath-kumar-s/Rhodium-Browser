from PyQt6.QtCore import QObject, QPoint, Qt, QEvent
from PyQt6.QtWidgets import QApplication

class ResizeMoveFilter(QObject):
    """Handles frameless-window resizing and dragging without stealing widget clicks."""

    def __init__(self, window):
        super().__init__(window)

        self.win = window
        self.margin = 8

        self.is_resizing = False
        self.is_moving = False

        self.drag_start_pos = QPoint()
        self.resize_edges = []

    def _start_window_drag(self, global_pos):
        """Start dragging the frameless browser window."""
        win_rect = self.win.frameGeometry()

        self.is_moving = True
        self.is_resizing = False

        self.drag_start_pos = global_pos - win_rect.topLeft()

    def _can_drag_window(self, global_pos):
        """Return True only when the user clicked empty browser chrome."""

        local_pos = self.win.mapFromGlobal(global_pos)

        # ---------------------------------------------------------
        # TOP 8px border
        # ---------------------------------------------------------
        if 0 <= local_pos.y() <= 8:
            return True

        # ---------------------------------------------------------
        # Empty area of the toolbar (NavBar)
        # ---------------------------------------------------------
        toolbar = getattr(self.win, "toolbar", None)
        if toolbar and toolbar.isVisible():
            tool_pos = toolbar.mapFromGlobal(global_pos)
            if toolbar.rect().contains(tool_pos):
                child = toolbar.childAt(tool_pos)
                if child is None:
                    return True

        # ---------------------------------------------------------
        # Empty area of the tab bar
        # ---------------------------------------------------------
        tab_widget = getattr(self.win, "tab_widget", None)
        if tab_widget:
            tab_bar = tab_widget.tabBar()
            if tab_bar and tab_bar.isVisible():
                tab_pos = tab_bar.mapFromGlobal(global_pos)
                if tab_bar.rect().contains(tab_pos):
                    if tab_bar.tabAt(tab_pos) < 0:
                        child = tab_bar.childAt(tab_pos)
                        if child is None:
                            return True

        return False

    def eventFilter(self, obj, event):

        # =========================================================
        # MOUSE PRESS
        # =========================================================
        if (
            event.type() == QEvent.Type.MouseButtonPress
            and event.button() == Qt.MouseButton.LeftButton
        ):

            pos = event.globalPosition().toPoint()
            win_rect = self.win.frameGeometry()

            # -----------------------------------------------------
            # RESIZE
            # -----------------------------------------------------
            edges = self._get_edges(pos, win_rect)

            if edges:
                self.resize_edges = edges
                self.is_resizing = True
                self.is_moving = False

                return True

            # -----------------------------------------------------
            # WINDOW DRAG
            # -----------------------------------------------------
            if self._can_drag_window(pos):
                self._start_window_drag(pos)
                return True

            # IMPORTANT:
            # This click belongs to the widget.
            return False

        # =========================================================
        # MOUSE MOVE
        # =========================================================
        elif event.type() == QEvent.Type.MouseMove:

            pos = event.globalPosition().toPoint()
            win_rect = self.win.frameGeometry()

            # -----------------------------------------------------
            # RESIZING
            # -----------------------------------------------------
            if self.is_resizing:

                self._apply_resize(pos)

                return True

            # -----------------------------------------------------
            # MOVING
            # -----------------------------------------------------
            if self.is_moving:
                if self.win.isMaximized():
                    # Dragging a maximized window restores it
                    local_pos = self.win.mapFromGlobal(pos)
                    click_x_ratio = local_pos.x() / self.win.width()
                    self.win.showNormal()
                    new_width = self.win.width()
                    new_x = int(pos.x() - click_x_ratio * new_width)
                    new_y = pos.y() - local_pos.y()
                    self.win.move(new_x, new_y)
                    self.drag_start_pos = pos - self.win.frameGeometry().topLeft()
                else:
                    self.win.move(
                        pos - self.drag_start_pos
                    )

                return True

            # -----------------------------------------------------
            # CURSOR
            # -----------------------------------------------------
            edges = self._get_edges(
                pos,
                win_rect
            )

            self._update_cursor(edges)

            # NEVER consume normal mouse movement
            return False

        # =========================================================
        # MOUSE RELEASE
        # =========================================================
        elif event.type() == QEvent.Type.MouseButtonRelease:

            was_handled = (
                self.is_resizing
                or self.is_moving
            )

            self.is_resizing = False
            self.is_moving = False
            self.resize_edges = []

            self.win.unsetCursor()

            if was_handled:
                return True

            return False

        return False

    # =============================================================
    # WINDOW EDGE DETECTION
    # =============================================================

    def _get_edges(self, global_pos, win_rect):

        edges = []

        x = global_pos.x()
        y = global_pos.y()

        # Left / Right
        if (
            win_rect.top()
            <= y
            <= win_rect.bottom()
        ):

            if abs(x - win_rect.left()) <= self.margin:
                edges.append("left")

            if abs(x - win_rect.right()) <= self.margin:
                edges.append("right")

        # Top / Bottom
        if (
            win_rect.left()
            <= x
            <= win_rect.right()
        ):

            if abs(y - win_rect.top()) <= self.margin:
                edges.append("top")

            if abs(y - win_rect.bottom()) <= self.margin:
                edges.append("bottom")

        return edges

    # =============================================================
    # RESIZE WINDOW
    # =============================================================

    def _apply_resize(self, global_pos):

        geom = self.win.geometry()

        minimum_width = self.win.minimumWidth()
        minimum_height = self.win.minimumHeight()

        # Right
        if "right" in self.resize_edges:

            new_width = (
                global_pos.x()
                - geom.left()
            )

            if new_width >= minimum_width:
                geom.setRight(
                    global_pos.x()
                )

        # Bottom
        if "bottom" in self.resize_edges:

            new_height = (
                global_pos.y()
                - geom.top()
            )

            if new_height >= minimum_height:
                geom.setBottom(
                    global_pos.y()
                )

        # Left
        if "left" in self.resize_edges:

            new_width = (
                geom.right()
                - global_pos.x()
            )

            if new_width >= minimum_width:
                geom.setLeft(
                    global_pos.x()
                )

        # Top
        if "top" in self.resize_edges:

            new_height = (
                geom.bottom()
                - global_pos.y()
            )

            if new_height >= minimum_height:
                geom.setTop(
                    global_pos.y()
                )

        self.win.setGeometry(geom)

    # =============================================================
    # RESIZE CURSOR
    # =============================================================

    def _update_cursor(self, edges):

        if (
            ("top" in edges and "left" in edges)
            or
            ("bottom" in edges and "right" in edges)
        ):

            self.win.setCursor(
                Qt.CursorShape.SizeFDiagCursor
            )

        elif (
            ("top" in edges and "right" in edges)
            or
            ("bottom" in edges and "left" in edges)
        ):

            self.win.setCursor(
                Qt.CursorShape.SizeBDiagCursor
            )

        elif (
            "left" in edges
            or
            "right" in edges
        ):

            self.win.setCursor(
                Qt.CursorShape.SizeHorCursor
            )

        elif (
            "top" in edges
            or
            "bottom" in edges
        ):

            self.win.setCursor(
                Qt.CursorShape.SizeVerCursor
            )

        else:

            self.win.unsetCursor()
