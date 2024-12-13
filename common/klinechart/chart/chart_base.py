from abc import abstractmethod
from typing import List, Dict, Tuple
from datetime import datetime
import pyqtgraph as pg

from PySide6 import QtCore, QtGui, QtWidgets
from common.klinechart.chart.object import DataItem
from common.klinechart.chart.base import to_int

from .base import BLACK_COLOR, UP_COLOR, DOWN_COLOR, PEN_WIDTH
from .manager import BarManager
from .object import ChartItemInfo, TIndex
import logging


class ChartBase(pg.GraphicsObject):
    """
    """

    def __init__(self, layout_index: int, chart_index: int, manager: BarManager):
        """"""
        super().__init__()
        self._layout_index = layout_index  # 排布的索引， 从0开始
        self._chart_index = chart_index  # 在某个layout上的表格的索引，从0开始
        self._type = ""  # 类型
        self._params = []  # 显示的参数
        self._manager: BarManager = manager

        self._bar_picutures: Dict[int, QtGui.QPicture] = {}
        self._item_picuture: QtGui.QPicture = None

        self._black_brush: QtGui.QBrush = pg.mkBrush(color=BLACK_COLOR)

        self._up_pen: QtGui.QPen = pg.mkPen(
            color=UP_COLOR, width=PEN_WIDTH
        )

        self._yellow_pen: QtGui.QPen = pg.mkPen(
            color="yellow", width=PEN_WIDTH
        )

        self._blue_pen: QtGui.QPen = pg.mkPen(
            color="blue", width=PEN_WIDTH
        )
        self._magenta_pen: QtGui.QPen = pg.mkPen(
            color="magenta", width=PEN_WIDTH
        )

        self._up_brush: QtGui.QBrush = pg.mkBrush(color=UP_COLOR)
        self._yellow_brush: QtGui.QBrush = pg.mkBrush(color="yellow")

        self._down_pen: QtGui.QPen = pg.mkPen(
            color=DOWN_COLOR, width=PEN_WIDTH
        )
        self._down_brush: QtGui.QBrush = pg.mkBrush(color=DOWN_COLOR)

        self._rect_area: Tuple[float, float] = None

        # Very important! Only redraw the visible part and improve speed a lot.
        # self.setFlag(self.ItemUsesExtendedStyleOption)
        self._bars: Dict[datetime, DataItem] = {}
        self._discrete_list: List[DataItem] = []  # 离散数据，例如直线类，不是每个点上都有直线，也可能一个点上多个直线
        self._pens = [self._yellow_pen, self._up_pen, self._down_pen, self._magenta_pen, self._blue_pen]
        colors_ = ["yellow", "red", "green", "magenta", "blue"]
        self.color_to_pen = dict(zip(colors_, self._pens))

    # 定义获取笔对象的方法
    def get_pen_by_color(self, color):
        try:
            return self.color_to_pen[color]
        except KeyError:
            return self.color_to_pen["yellow"]

    def get_index(self, dt: datetime) -> TIndex:
        """
        Get index with datetime.
        """
        return self._manager.get_index_from_dt(dt)
        # return self._manager._datetime_index_map.get(dt, None)

    def get_datetime(self, ix: float) -> datetime:
        """
        Get datetime with index.
        """
        # ix = to_int(ix)
        return self._manager.get_dt_from_index(ix)
        # return self._index_datetime_map.get(ix, None)

    def get_bar_from_index(self, ix: float) -> DataItem:
        """
        Get bar data with index.
        """
        # ix = to_int(ix)
        dt = self._manager.get_dt_from_index(ix)
        # dt = self._manager._index_datetime_map.get(ix, None)
        if not dt:
            return None

        return self._bars[dt] if dt in self._bars else None

    def get_bar_from_dt(self, dt: datetime) -> DataItem:
        """
        Get bar data with dt.
        """
        return self._bars[dt] if dt in self._bars else None

    @abstractmethod
    def _draw_bar_picture(self, ix: int, old_bar: DataItem, cur_bar: DataItem) -> QtGui.QPicture:
        """
        Draw picture for specific bar.
        """
        pass

    def boundingRect(self) -> QtCore.QRectF:
        """
        Get bounding rectangles for item.
        """
        min_volume, max_volume = self._manager.get_layout_range(self._layout_index)
        # logging.info("boundingRect: min:{}, max:{}".format(min_volume, max_volume))
        rect = QtCore.QRectF(
            0,
            min_volume,
            len(self._bar_picutures),
            max_volume - min_volume
        )
        return rect

    def get_y_range(self, min_ix: int = None, max_ix: int = None) -> Tuple[float, float]:
        """
        Get range of y-axis with given x-axis range.

        If min_ix and max_ix not specified, then return range with whole data set.
        """
        min_value, max_value = self._manager.get_layout_range(self._layout_index, min_ix, max_ix)
        # logging.info("【{}】get_y_range::min_max_value:【{}，{}】".format(
        #     self.__class__.__name__, min_value, max_value))
        return min_value, max_value

    @abstractmethod
    def get_info_text(self, ix: int) -> str:
        """
        Get information text to show by cursor.
        """
        pass

    def update_history_data(self, info: ChartItemInfo):
        self._discrete_list = info.discrete_list
        self._bars = info.bars
        self._type = info.type
        self._params = info.params

        for ix in range(len(self._manager._datetime_index_map)):
            self._bar_picutures[ix] = None
        self.update()

    def update(self) -> None:
        """
        Refresh the item.
        """
        if self.scene():
            self.scene().update()

    def paint(self,
              painter: QtGui.QPainter,
              opt: QtWidgets.QStyleOptionGraphicsItem,
              w: QtWidgets.QWidget):
        """
        Reimplement the paint method of parent class.

        This function is called by external QGraphicsView.
        """
        rect = opt.exposedRect

        min_ix = int(rect.left())
        max_ix = int(rect.right())
        max_ix = min(max_ix, len(self._bar_picutures))

        rect_area = (min_ix, max_ix)
        if rect_area != self._rect_area or not self._item_picuture:
            self._rect_area = rect_area
            self._draw_item_picture(min_ix, max_ix)

        self._item_picuture.play(painter)

    def _draw_item_picture(self, min_ix: int, max_ix: int) -> None:
        """
        Draw the picture of item in specific range.
        """
        self._item_picuture = QtGui.QPicture()
        painter = QtGui.QPainter(self._item_picuture)
        if min_ix > 0:
            old_bar = self.get_bar_from_index(min_ix - 1)
        else:
            old_bar = self.get_bar_from_index(min_ix)
        for ix in range(min_ix, max_ix):
            bar_picture = self._bar_picutures[ix]

            if bar_picture is None:
                cur_bar = self.get_bar_from_index(ix)
                bar_picture = self._draw_bar_picture(ix, old_bar, cur_bar)
                self._bar_picutures[ix] = bar_picture
                old_bar = cur_bar

            bar_picture.play(painter)

        painter.end()

    def clear_all(self) -> None:
        """
        Clear all data in the item.
        """
        self._item_picuture = None
        self._bar_picutures.clear()
        self.update()



