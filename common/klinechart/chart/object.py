"""
Basic data structure used for general trading function in the trading platform.
"""
from __future__ import annotations
from datetime import datetime
from typing import List, Dict, NewType, Tuple
from enum import Enum


TIndex = int


class DataItem(list):
    """ 表格数据
    如果输入数据类似如下：‘2022-01-14 22:16:00,4625.0,4626.0,4621.0,4622.0’
    我们将其转换为：['2022-01-14 22:16:00', 4625.0, 4626.0, 4621.0, 4622.0]
    如果输入数据如下：‘2022-01-14 22:16:00,4622.0’
    我们将其转换为：['2022-01-14 22:16:00', 4622.0]
    """

    def __init__(self, txt="", data_type=[]):
        list.__init__([])
        self.init_txt(txt, data_type)

    def init_txt(self, txt, data_type=[]):
        if not txt:
            return
        arr = txt.split(",")
        if not data_type:
            arr = [float(arr[i]) if i > 0 else datetime.strptime(arr[0], "%Y-%m-%d %H:%M:%S") for i in
                   range(0, len(arr))]
        else:
            for i in range(len(arr)):
                if data_type[i] == "datetime":
                    arr[i] = datetime.strptime(arr[i], "%Y-%m-%d %H:%M:%S")
                elif data_type[i] == "float":
                    arr[i] = float(arr[i])
        self.extend(arr)

    def init_kline(self, kline):
        arr = [datetime.fromtimestamp(kline.time), kline.open, kline.high, kline.low, kline.close]
        self.extend(arr)
        return self

    def init_line(self, lines):
        arr = [lines[i] if i > 0 else datetime.strptime(lines[0], "%Y-%m-%d %H:%M:%S") for i in
               range(0, len(lines))]
        self.extend(arr)
        return self




BarList : List[DataItem] = {}
BarDict : Dict[datetime, DataItem] = {}


class ChartItemInfo:
    """
    图表数据信息
    """

    def __init__(self):
        self.type = ""
        self.discrete_list: BarList = []
        self.bars: BarDict = {}
        self.params: List[str] = []
        self.func_name: str = ""    # 获取数据的函数名
        self.data_type: List[str] = []
        self.max_height: int = 0


PlotIndex = NewType('PlotIndex', int)
ItemIndex = NewType('ItemIndex', int)
PlotItemInfo = Dict[ItemIndex, ChartItemInfo]
MinMaxIdxTuple = Tuple[int, int]
MinMaxPriceTuple = Tuple[float, float]


class Offset(Enum):
    """
    Offset of order/trade.
    """
    NONE = -1
    OPEN = 0
    CLOSE = 1
