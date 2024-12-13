from PySide6 import QtCore, QtGui
from common.klinechart.chart.object import DataItem
from .chart_base import ChartBase
from .base import BAR_WIDTH
from .manager import BarManager


class ChartCandle(ChartBase):
    """
    K线图
    """

    def __init__(self, layout_index, chart_index, manager: BarManager):
        """"""
        super().__init__(layout_index, chart_index, manager)

    def _draw_bar_picture(self, ix: int, old_bar: DataItem, bar: DataItem) -> QtGui.QPicture:
        """"""
        # Create objects
        candle_picture = QtGui.QPicture()
        painter = QtGui.QPainter(candle_picture)
        # 1 open
        # 2 high
        # 3 low
        # 4 close
        # Set painter color
        if bar[4] > bar[1]:  # bar.close_price >= bar.open_price:
            painter.setPen(self._up_pen)
            painter.setBrush(self._black_brush)
        else:
            painter.setPen(self._down_pen)
            painter.setBrush(self._down_brush)

        # Draw candle shadow
        if bar[2] > bar[3]:  # bar.high_price > bar.low_price:
            painter.drawLine(
                QtCore.QPointF(ix, bar[2]),
                QtCore.QPointF(ix, bar[3])
            )

        # Draw candle body
        if bar[1] == bar[4]:  # bar.open_price == bar.close_price:
            painter.drawLine(
                QtCore.QPointF(ix - BAR_WIDTH, bar[1]),
                QtCore.QPointF(ix + BAR_WIDTH, bar[1]),
            )
        else:
            rect = QtCore.QRectF(
                ix - BAR_WIDTH,
                bar[1],
                BAR_WIDTH * 2,
                bar[4] - bar[1]
            )
            painter.drawRect(rect)

        # Finish
        painter.end()
        return candle_picture

    def get_info_text(self, ix: int) -> str:
        """
        Get information text to show by cursor.
        """
        bar = self.get_bar_from_index(ix)
        if not bar:
            text = ""
        else:
            if self.__class__.__name__ == "ChartCandle":
                words = [f'Date:{bar[0].strftime("%Y-%m-%d")}', f'Time:{bar[0].strftime("%H:%M")}',
                         f'Open:{str(bar[1])}', f'High :{str(bar[2])}', f"low   :{str(bar[3])}",
                         f"close:{str(bar[4])}", f'index:{str(ix)}']
            else:
                words = [str(bar[i]) for i in range(1, len(bar))]
            text = "\n".join(words)
        return text
