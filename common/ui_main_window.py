import os, sys
from PySide6 import QtWidgets
from PySide6 import QtCore, QtGui, QtWidgets
if "PyQt5" in sys.modules:
    del sys.modules["PyQt5"]

from typing import Dict, List
from common.klinechart.chart import ChartWidget, ChartCandle, ItemIndex
from common.klinechart.chart.object import DataItem
from common.klinechart.chart import PlotIndex, BarDict, PlotItemInfo, ChartItemInfo
from common.utils import file_txt
from common.model.kline import KLine
import logging
from common.klinechart.chart.keyboard_genie_window import KeyboardGenieWindow


def load_data(conf: Dict[str, any]) -> Dict[PlotIndex, PlotItemInfo]:
    """
    返回以layout_index, index为key的各item的kl_data_list
    """
    local_data: Dict[PlotIndex, PlotItemInfo] = {}
    plots = conf["plots"]
    for plot_index, plot in enumerate(plots):
        plot_info: PlotItemInfo = {}
        for item_index, item in enumerate(plot["chart_item"]):
            item_info: ChartItemInfo = ChartItemInfo()
            item_info.type = item["type"]
            item_info.params = item["params"] if "params" in item else []
            item_info.func_name = item["func_name"] if "func_name" in item else ""
            item_info.data_type = item["data_type"] if "data_type" in item else []
            data_list = file_txt.read_file(item["file_name"])
            bar_dict: BarDict = calc_bars(data_list, item_info.data_type)
            item_info.bars = bar_dict
            plot_info[ItemIndex(item_index)] = item_info
            logging.info(F"file_name: {item['file_name']}")
            logging.info(F"plot_index:{plot_index}, item_index:{item_index}, len(bar_dict)={len(bar_dict)}")
        local_data[PlotIndex(plot_index)] = plot_info

    return local_data


def calc_bars(data_list, data_type: List[str]) -> BarDict:
    bar_dict: BarDict = {}
    for data_index, txt in enumerate(data_list):
        bar = DataItem(txt, data_type)
        if bar:
            bar_dict[bar[0]] = bar
    return bar_dict


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, conf):
        super().__init__()
        datas: Dict[PlotIndex, PlotItemInfo] = load_data(conf)
        widget = ChartWidget(self)
        widget.manager.update_history_klines(datas[PlotIndex(0)][ItemIndex(0)].bars.values())
        # obtain_data_from_algo(widget.manager.klines, datas)

        self.add_chart_Item(conf["plots"], widget)  # 将页面加到plots中，然后加到widget中

        widget.add_cursor()
        # widget.update_all_history_data(datas)

        self.graphWidget = widget
        self.setCentralWidget(self.graphWidget)

        # 加载股票代码和名称列表
        self.stock_list = self.load_stock_list()

        # 创建键盘精灵窗口
        self.keyboard_genie = KeyboardGenieWindow(self)



    def load_stock_list(self):
            # 示例：从文件或数据库加载股票列表
            # 此处使用简单的列表作为示例
            stock_list = [
                {'code': '600519', 'name': '贵州茅台'},
                {'code': '000001', 'name': '平安银行'},
                {'code': '000002', 'name': '万科A'},
                {'code': '600036', 'name': '招商银行'},
                {'code': '600837', 'name': '海通证券'},
                # ... 更多股票代码和名称 ...
            ]
            return stock_list


    def add_chart_Item(self, plots, widget):
        for plot_index, plot in enumerate(plots):
            if plot_index != len(plots) - 1:
                axis = True
            else:
                axis = False
            widget.add_plot(hide_x_axis=axis, maximum_height=plots[plot_index]["max_height"])  # plot
            for index, chart_item in enumerate(plot["chart_item"]):
                if chart_item["type"] == "Candle":
                    widget.add_item(plot_index, ChartCandle)
                else:
                    raise "not match item"

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            self.stock_list = []
            self.keyboard_genie.hide()
        else:
            text = event.text()
            if text.isalnum() or text.isalpha() or text.isdigit():
                if not self.keyboard_genie.isVisible():
                    self.keyboard_genie.show()
                    self.update_keyboard_genie_position()
                    # 激活键盘精灵窗口并提升到最前
                    self.keyboard_genie.activateWindow()
                    self.keyboard_genie.raise_()
                    # 将焦点设置到键盘精灵的输入框
                    self.keyboard_genie.input_line_edit.setFocus()
                    # 清空输入框并设置初始值
                    self.keyboard_genie.input_line_edit.clear()
                    self.keyboard_genie.input_line_edit.setText(text)

                # # 将焦点设置到键盘精灵的输入框，并添加按下的字符
                # self.keyboard_genie.input_line_edit.setFocus()
                # current_text = self.keyboard_genie.input_line_edit.text()
                # self.keyboard_genie.input_line_edit.setText(current_text + text)
            else:
                super().keyPressEvent(event)

    def moveEvent(self, event):
        super().moveEvent(event)
        self.update_keyboard_genie_position()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_keyboard_genie_position()

    def update_keyboard_genie_position(self):
        if self.keyboard_genie.isVisible():
            # 获取主窗口的全局位置
            main_window_pos = self.mapToGlobal(QtCore.QPoint(0, 0))
            main_window_size = self.size()
            genie_size = self.keyboard_genie.sizeHint()
            x = main_window_pos.x() + main_window_size.width() - genie_size.width()
            y = main_window_pos.y() + main_window_size.height() - genie_size.height()
            self.keyboard_genie.move(x, y)

    # def on_input_text_changed(self, text):
    #     self.update_matching_list(text)
    #
    # def on_item_double_clicked(self, item):
    #     selected_stock_code = item.data(QtCore.Qt.UserRole)
    #     print(f"选中股票代码：{selected_stock_code}")
    #     # 在这里加载股票数据并更新图表
    #     self.keyboard_genie.close()

    def update_matching_list(self, input_text):
        matching_stocks = []
        input_upper = input_text.strip().upper()
        if input_upper:
            for stock in self.stock_list:
                if input_upper in stock['code'] or input_upper in stock['name'].upper():
                    matching_stocks.append(stock)

        self.keyboard_genie.matching_list_widget.clear()
        for stock in matching_stocks:
            item_text = f"{stock['code']} - {stock['name']}"
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.UserRole, stock['code'])
            self.keyboard_genie.matching_list_widget.addItem(item)

        if matching_stocks:
            self.keyboard_genie.matching_list_widget.setCurrentRow(0)
        else:
            pass


app = QtWidgets.QApplication(sys.argv)

