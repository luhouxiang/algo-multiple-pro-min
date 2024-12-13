from typing import List, Dict, Type

import pyqtgraph as pg
import os

from PySide6.QtWidgets import QMessageBox
showMessage = QMessageBox.question

from PySide6 import QtGui, QtWidgets, QtCore
from .object import PlotIndex, PlotItemInfo
from .manager import BarManager
from .base import (
    GREY_COLOR, WHITE_COLOR, CURSOR_COLOR, BLACK_COLOR,
    to_int, NORMAL_FONT
)
from .axis import DatetimeAxis
from .chart_base import ChartBase
from enum import Enum
import logging

pg.setConfigOptions(antialias=True)


class EAlignType(Enum): # 对齐方式
    right = 0   # 向右对齐
    center = 1  # 向中间对齐


class ChartWidget(pg.PlotWidget):
    """
    绘制和操作K线图类
    """
    MIN_BAR_COUNT = 5   # 最小K线数
    NORMAL_BAR_COUNT = 100  # 默认显示的K线数

    def __init__(self, parent: QtWidgets.QWidget = None):
        """"""
        super().__init__(None)
        self.main_window = parent.window()
        self.manager: BarManager = BarManager()

        self._plots: List[pg.PlotItem] = []
        self._plot_charts_dict: Dict[PlotIndex, List[ChartBase]] = {}  # 通过PlotIndex可以找到对应这个区域的所有实例

        # 每一个chart_item实例对应plot_item, 一个plot_item会加载若干个chart_item实例，plot_item存于self._plots
        self._item_plot_map: Dict[ChartBase, pg.PlotItem] = {}

        self._first_plot: pg.PlotItem = None
        self._cursor: ChartCursor = None

        self._right_ix: int = 0                     # 最右边K线的数据索引
        self._bar_count: int = self.NORMAL_BAR_COUNT   # 图表中可见K线数量

        self._init_ui()

    def closeEvent(self, event):
        event.accept()
        os._exit(0)
        # reply = showMessage(self, '警告', "系统将退出，是否确认?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        #
        # if reply == QMessageBox.Yes:
        #     event.accept()
        #     os._exit(0)
        # else:
        #     event.ignore()

    def _init_ui(self) -> None:
        """
        设置窗口标题，创建并配置图形布局，
        设置边距，间距和边框颜色
        """
        self.setWindowTitle("kline-chart")

        self._layout = pg.GraphicsLayout()
        self._layout.setContentsMargins(5, 5, 5, 5)  # 图形与边框的距离
        self._layout.setSpacing(0)
        self._layout.setBorder(color=GREY_COLOR, width=0.8)
        self._layout.setZValue(0)
        self.setCentralItem(self._layout)

    def _get_new_x_axis(self):
        return DatetimeAxis(self.manager, orientation='bottom')

    def add_cursor(self) -> None:
        """
        添加光标方法
        """
        if not self._cursor:
            self._cursor = ChartCursor(
                self, self.manager, self._plots, self._item_plot_map)
            self._cursor.main_window = self.main_window

    def add_plot(
        self,
        minimum_height: int = 80,
        maximum_height: int = None,
        hide_x_axis: bool = False
    ) -> None:
        """
        Add plot area.
        添加绘图区域方法
        """
        # Create plot object
        plot = pg.PlotItem(axisItems={'bottom': self._get_new_x_axis()})
        plot.setMenuEnabled(False)
        plot.setClipToView(True)
        plot.hideAxis('right')
        plot.showAxis('left')
        plot.setDownsampling(mode='peak')
        plot.setRange(xRange=(0, 1), yRange=(0, 1))
        plot.hideButtons()
        plot.setMinimumHeight(minimum_height)

        if maximum_height:
            plot.setMaximumHeight(maximum_height)

        if hide_x_axis:
            plot.hideAxis("bottom")

        if not self._first_plot:
            self._first_plot = plot

        # Connect view change signal to update y range function
        view = plot.getViewBox()
        view.sigXRangeChanged.connect(self._update_y_range)
        view.setMouseEnabled(x=True, y=False)

        # Set right axis
        right_axis = plot.getAxis('left')
        right_axis.setWidth(60)
        right_axis.tickFont = NORMAL_FONT

        # Connect x-axis link
        if self._plots:
            first_plot = self._plots[0]
            plot.setXLink(first_plot)

        # Store plot object in dict
        self._plots.append(plot)

        # Add plot onto the layout
        self._layout.nextRow()
        self._layout.addItem(plot)

    def add_item(
        self,
        layout_index: int,
        item_class: Type[ChartBase]
    ):
        """
        Add chart item.
        添加图表项目方法，用于在特定绘图区域添加图表项目
        """
        chart_index = 0 if layout_index not in self._plot_charts_dict else len(self._plot_charts_dict)
        chart_item = item_class(layout_index, chart_index, self.manager)
        if layout_index not in self._plot_charts_dict:
            self._plot_charts_dict[layout_index] = []
        self._plot_charts_dict[layout_index].append(chart_item)
        plot_item = self._plots[layout_index]
        plot_item.addItem(chart_item)

        self._item_plot_map[chart_item] = plot_item

    def get_plot(self, plot_index: int) -> pg.PlotItem:
        """
        Get specific plot with its name.
        """
        return None if plot_index >= len(self._plots) else self._plots[plot_index]

    def get_all_plots(self) -> List[pg.PlotItem]:
        """
        获取所有绘图区域方法
        """
        return self._plots

    def clear_all(self) -> None:
        """
        Clear all data.
        """
        self.manager.clear_all()

        for items in self._plot_charts_dict.values():
            for item in items:
                item.clear_all()

        if self._cursor:
            self._cursor.clear_all()

    def update_all_history_data(self, datas: Dict[PlotIndex, PlotItemInfo]) -> None:
        """
        设置历史数据
        """
        for plot_index, charts in self._plot_charts_dict.items():
            for chart_index, chart_item in enumerate(charts):
                chart_info = datas[plot_index][chart_index]
                self.manager.update_history_data(plot_index, chart_index, chart_info)
                chart_item.update_history_data(chart_info)

        self._update_history_plot_limits()
        self.move_to_right_most()

    def _update_history_plot_limits(self):
        """
        Update the limit of plots.
        """
        for item, plot in self._item_plot_map.items():
            min_value, max_value = item.get_y_range()

            plot.setLimits(
                xMin=-1,
                xMax=self.manager.get_count(),
                yMin=min_value,
                yMax=max_value
            )

    def _update_plot_limits(self) -> None:
        """
        Update the limit of plots.
        """
        for item, plot in self._item_plot_map.items():
            min_value, max_value = item.get_y_range()

            plot.setLimits(
                xMin=-1,
                xMax=self.manager.get_count(),
                yMin=min_value,
                yMax=max_value
            )

    def _update_x_range(self, align_type: EAlignType = EAlignType.right) -> None:
        """
        Update the x-axis range of plots.
        """
        # logging.info("cursor._x={}, _y={}".format(self._cursor._x, self._cursor._y))
        if align_type == EAlignType.center:
            max_ix = self._cursor._x + self._bar_count/2
            min_ix = self._cursor._x - self._bar_count/2
        else:
            max_ix = self._right_ix
            min_ix = self._right_ix - self._bar_count

        for plot in self._plots:
            plot.setRange(xRange=(min_ix, max_ix), padding=0)

    def _update_y_range(self) -> None:
        """
        Update the y-axis range of plots.
        """
        view = self._first_plot.getViewBox()
        view_range = view.viewRange()

        min_ix = max(0, int(view_range[0][0]))
        max_ix = min(self.manager.get_count(), int(view_range[0][1]))

        # Update limit for y-axis
        for item, plot in self._item_plot_map.items():
            y_range = item.get_y_range(min_ix, max_ix)
            plot.setRange(yRange=y_range)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        """
        Reimplement this method of parent to update current max_ix value.
        """
        view = self._first_plot.getViewBox()
        view_range = view.viewRange()
        self._right_ix = max(0, view_range[0][1])

        super().paintEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        """
        Reimplement this method of parent to move chart horizontally and zoom in/out.
        """
        # 如果匹配窗口显示，则不处理方向键和回车键，将事件传递给 MainWindow
        # if self.main_window.key.isVisible() and event.key() in [QtCore.Qt.Key_Up, QtCore.Qt.Key_Down, QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]:
        #     self.main_window.keyPressEvent(event)
        #     return

        if event.key() == QtCore.Qt.Key_Left:
            self._on_key_left()
        elif event.key() == QtCore.Qt.Key_Right:
            self._on_key_right()
        elif event.key() == QtCore.Qt.Key_Up:
            self._on_key_up()
        elif event.key() == QtCore.Qt.Key_Down:
            self._on_key_down()
        super().keyPressEvent(event)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        """
        Reimplement this method of parent to zoom in/out.
        """
        delta = event.angleDelta()

        if delta.y() > 0:
            self._on_key_up()
        elif delta.y() < 0:
            self._on_key_down()

    def _on_key_left(self) -> None:
        """
        Move chart to left.
        """
        self._right_ix -= 1
        self._right_ix = max(self._right_ix, self._bar_count)

        self._update_x_range()
        self._cursor.move_left()
        self._cursor.update_lefttop_info()

    def _on_key_right(self) -> None:
        """
        Move chart to right.
        """
        self._right_ix += 1
        self._right_ix = min(self._right_ix, self.manager.get_count())

        self._update_x_range()
        self._cursor.move_right()
        self._cursor.update_lefttop_info()

    def _on_key_down(self) -> None:
        """
        Zoom out the chart.
        """
        self._bar_count *= 1.2
        self._bar_count = min(int(self._bar_count), self.manager.get_count())

        self._update_x_range(align_type=EAlignType.center)
        self._cursor.update_lefttop_info()

    def _on_key_up(self) -> None:
        """
        Zoom in the chart.
        """
        self._bar_count /= 1.2
        self._bar_count = max(int(self._bar_count), self.MIN_BAR_COUNT)

        self._update_x_range(align_type=EAlignType.center)
        self._cursor.update_lefttop_info()

    def move_to_right_most(self) -> None:
        """
        Move chart to the most right.
        """
        self._right_ix = self.manager.get_count()
        self._update_x_range()
        self._cursor.move_right_most()
        self._cursor.update_lefttop_info()


class ChartCursor(QtCore.QObject):
    """
    光标类
    """

    def __init__(
        self,
        widget: ChartWidget,
        manager: BarManager,
        plots: List[pg.GraphicsObject],
        item_plot_map: Dict[ChartBase, pg.GraphicsObject]
    ):
        """"""
        super().__init__()
        self.main_window = None
        self._widget: ChartWidget = widget
        self._manager: BarManager = manager
        self._plots: List[pg.GraphicsObject] = plots
        self._item_plot_map: Dict[ChartBase, pg.GraphicsObject] = item_plot_map

        self._x: int = 0
        self._y: int = 0
        self._plot_name: int = 0

        self._infos: Dict[str, pg.TextItem] = {}

        self._v_lines: Dict[str, pg.InfiniteLine] = {}
        self._h_lines: Dict[str, pg.InfiniteLine] = {}
        self._views: Dict[str, pg.ViewBox] = {}

        self._y_labels: Dict[int, pg.TextItem] = {}
        self._x_label: pg.TextItem = None

        self._init_ui()
        self._connect_signal()

    def _init_ui(self):
        """"""
        self._init_line()
        self._init_label()
        self._init_info()

    def _init_line(self) -> None:
        """
        Create line objects.
        """
        pen = pg.mkPen(WHITE_COLOR)

        for index, plot in enumerate(self._plots):
            v_line = pg.InfiniteLine(angle=90, movable=False, pen=pen)
            h_line = pg.InfiniteLine(angle=0, movable=False, pen=pen)
            view = plot.getViewBox()

            for line in [v_line, h_line]:
                line.setZValue(0)
                line.hide()
                view.addItem(line)
            plot_name = index
            self._v_lines[plot_name] = v_line
            self._h_lines[plot_name] = h_line
            self._views[plot_name] = view

    def _init_label(self) -> None:
        """
        Create label objects on axis.
        """
        for index, plot in enumerate(self._plots):
            label = pg.TextItem(
                str(index), fill=CURSOR_COLOR, color=BLACK_COLOR)
            label.hide()
            label.setZValue(2)
            label.setFont(NORMAL_FONT)
            plot.addItem(label, ignoreBounds=True)
            self._y_labels[index] = label

        self._x_label: pg.TextItem = pg.TextItem(
            "datetime", fill=CURSOR_COLOR, color=BLACK_COLOR)
        self._x_label.hide()
        self._x_label.setZValue(2)
        self._x_label.setFont(NORMAL_FONT)
        plot.addItem(self._x_label, ignoreBounds=True)

    def _init_info(self) -> None:
        """
        """
        for index, plot in enumerate(self._plots):
            plot_name = index
            info = pg.TextItem(
                "info",
                color=CURSOR_COLOR,
                border=CURSOR_COLOR,
                fill=BLACK_COLOR
            )
            info.hide()
            info.setZValue(2)
            info.setFont(NORMAL_FONT)
            plot.addItem(info)  # , ignoreBounds=True)
            self._infos[plot_name] = info

    def _connect_signal(self) -> None:
        """
        Connect mouse move signal to update function.
        """
        self._widget.scene().sigMouseMoved.connect(self._mouse_moved)

    def _mouse_moved(self, evt: tuple) -> None:
        """
        Callback function when mouse is moved.
        鼠标移动事件处理方法
        """
        if not self._manager.get_count():
            return

        # First get current mouse point
        pos = evt

        for index, view in self._views.items():
            rect = view.sceneBoundingRect()
            plot_name = index
            if rect.contains(pos):
                mouse_point = view.mapSceneToView(pos)
                self._x = to_int(mouse_point.x())
                self._y = mouse_point.y()
                self._plot_name = plot_name
                break

        # Then update cursor component
        self._update_line()
        self._update_label()
        self.update_lefttop_info()

    def update_lefttop_info(self):
        # self.update_lefttop_info()
        # Call the appropriate method based on mouse x position in main window
        # Get the main window
        # main_window = self.window()
        main_window = self.main_window
        # Get global mouse position
        global_pos = QtGui.QCursor.pos()
        # Map global position to main window coordinate system
        main_pos = main_window.mapFromGlobal(global_pos)
        # Determine the center x coordinate of the main window
        center_x = main_window.width() / 2
        if main_pos.x() < center_x:
            self.update_left_right_top_info(False)
        else:
            self.update_left_right_top_info(True)

    def _update_line(self) -> None:
        """"""
        for v_line in self._v_lines.values():
            v_line.setPos(self._x)
            v_line.show()

        for plot_name, h_line in self._h_lines.items():
            if plot_name == self._plot_name:
                h_line.setPos(self._y)
                h_line.show()
            else:
                h_line.hide()

    def _update_label(self) -> None:
        """"""
        bottom_plot = self._plots[-1]
        axis_width = bottom_plot.getAxis("left").width()
        axis_height = bottom_plot.getAxis("bottom").height()
        axis_offset = QtCore.QPointF(axis_width, axis_height)

        bottom_view = list(self._views.values())[-1]
        bottom_right = bottom_view.mapSceneToView(
            bottom_view.sceneBoundingRect().bottomRight() - axis_offset
        )
        top_left = bottom_view.mapSceneToView(
            bottom_view.sceneBoundingRect().topLeft()
        )
        x_pos = top_left.x()
        if (bottom_right.x()-self._x)*2 > bottom_right.x() - top_left.x():
            x_pos = bottom_right.x()

        for plot_name, label in self._y_labels.items():
            if plot_name == self._plot_name:
                label.setText("{:.3f}".format(self._y))
                label.show()
                label.setPos(x_pos, self._y)
                # print("{}， bottom_right:{}, top_left:{}".format(self._x, bottom_right.x(), top_left.x()))
            else:
                label.hide()

        dt = self._manager.get_dt_from_index(self._x)
        if dt:
            self._x_label.setText(dt.strftime("%Y-%m-%d %H:%M:%S"))
            self._x_label.show()
            self._x_label.setPos(self._x, bottom_right.y())
            self._x_label.setAnchor((0, 0))

    def update_left_right_top_info(self, left: bool) -> None:
        buf = {}

        for item, plot in self._item_plot_map.items():
            item_info_text = item.get_info_text(self._x)

            if plot not in buf:
                buf[plot] = item_info_text
            else:
                if item_info_text:
                    buf[plot] += ("\n\n" + item_info_text)

        for index, plot in enumerate(self._plots):
            plot_name = index
            plot_info_text = buf[plot]
            info = self._infos[plot_name]
            info.setText(plot_info_text)
            info.show()

            view = self._views[plot_name]
            if left:
                top_pos = view.mapSceneToView(view.sceneBoundingRect().topLeft())
            else:
                # 获取视图右上角的位置
                top_right_scene_pos = view.sceneBoundingRect().topRight()
                top_right_view_pos = view.mapSceneToView(top_right_scene_pos)

                # 获取信息框的宽度
                info_width = info.boundingRect().width()

                # 考虑视图的缩放，计算实际需要减去的宽度
                delta_pos = view.mapSceneToView(QtCore.QPointF(info_width, 0)) - view.mapSceneToView(
                    QtCore.QPointF(0, 0))
                info_width_in_view = delta_pos.x()

                # 调整 x 坐标，确保信息框不会超出视图范围
                adjusted_x = top_right_view_pos.x() - info_width_in_view
                top_pos = QtCore.QPointF(adjusted_x, top_right_view_pos.y())
            info.setPos(top_pos)

    # def update_lefttop_info(self) -> None:
    #     """"""
    #     self.update_left_right_top_info(True)

    # def update_righttop_info(self) -> None:
    #     self.update_left_right_top_info(False)

    def move_right(self) -> None:
        """
        Move cursor index to right by 1.
        """
        if self._x == self._manager.get_count() - 1:
            return
        self._x += 1

        self._update_after_move()

    def move_right_most(self):
        """移到最右边"""
        self._x = self._manager.get_count() - 1

    def move_left(self) -> None:
        """
        Move cursor index to left by 1.
        """
        if self._x == 0:
            return
        self._x -= 1

        self._update_after_move()

    def _update_after_move(self) -> None:
        """
        Update cursor after moved by left/right.
        """
        _, self._y = self._manager.get_layout_range(0, self._x, self._x)
        # self._y = bar.close_price
        #
        self._update_line()
        self._update_label()
        pass

    def clear_all(self) -> None:
        """
        Clear all data.
        """
        self._x = 0
        self._y = 0
        self._plot_name = 0

        for line in list(self._v_lines.values()) + list(self._h_lines.values()):
            line.hide()

        for label in list(self._y_labels.values()) + [self._x_label]:
            label.hide()
