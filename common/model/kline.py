# -*- coding: utf-8 -*
"""
@file: kline.py
@author: luhx
@description: K线数据元素
"""
from datetime import datetime
from enum import Enum


class KLine:
    """K线类
    """
    def __init__(self, time=0, open=0, high=0, low=0, close=0, volume=0, symbol=""):
        self.time = time    # 时间
        self.open = open    # 开
        self.high = high    # 高
        self.low = low      # 低
        self.close = close  # 收
        self.volume = volume    # 成交量
        self.symbol = symbol    # 合约号

    def __str__(self):
        return "t:{},o:{},h:{},l:{},c:{},v:{}".\
            format(str(datetime.fromtimestamp(self.time)),
                   self.open, self.high, self.low, self.close, self.volume)

    def __repr__(self):
        return self.__str__()


class KSide(Enum):
    """K线方向
    """
    UP = 1      # 向上
    DOWN = -1   # 向下
    Init = 0    # 不确定


class KExtreme(Enum):
    """顶或是底"""
    TOP = 1         # 顶
    BOTTOM = -1     # 底
    NORMAL = 0      # 不是顶也不是底


class stCombineK:
    """K线合并类
    """
    def __init__(self, low, high, begin, end, base, isup):
        self.range_low: float = low
        self.range_high: float = high
        self.pos_begin: int = begin      # 起始
        self.pos_end: int = end          # 结束
        self.pos_extreme: int = base     # 最高或者最低位置,极值点位置
        self.isUp: KSide = KSide(isup)            # 是否向上
        # self.data: KLine = data
        # print(self.isUp)

    def __str__(self):
        if self.isUp == KSide.UP:
            side = "up"
        elif self.isUp == KSide.DOWN:
            side = "down"
        elif self.isUp == KSide.Init:
            side = "init"
        return "[{}]:begin:[{}]{},end:[{}]{},base:{}".format(
            side, self.pos_begin, self.range_low, self.pos_end, self.range_high, self.pos_extreme)

    def __repr__(self):
        return self.__str__()


class stFxK:
    """
    K线分型，顶或是底
    分型是由顶或底，左，右三个独立K线构成
    """
    def __init__(self, index: int, side: KExtreme, low: float, high: float):
        self.index: int = index
        self.side: KExtreme = side   # 顶或是底， 0表示非顶或是非底
        self.lowest: float = low
        self.highest: float = high
        self.extremal: stCombineK = None    # 顶或是底中独立K线
        self.left: stCombineK = None
        self.right: stCombineK = None
        self.invalid: bool = True   # 标记该分型是否完整。针对实时数据，有时为了快，直接用不完整的分型进行计算


    def __str__(self):
        bottom_str = f"⬉⬈[{self.index}]:{self.lowest:.2f}"
        top_str = f"⬋⬊[{self.index}]: {self.highest:.2f}"
        normal_str = f"[{self.index}]⬅⮕{self.lowest} : {self.highest}"
        if self.side == KExtreme.BOTTOM:
            return bottom_str
        elif self.side == KExtreme.TOP:
            return top_str
        else:
            return normal_str

    def __repr__(self):
        return self.__str__()


class stBiK:
    """
    K线笔类
    """
    def __init__(self):
        self.pos_begin: int = 0     # 开始
        self.pos_end: int = 0       # 结束
        self.top: stCombineK = None     # 顶
        self.bottom: stCombineK = None  # 底
        self.highest: float = 0.0   # 最高
        self.lowest: float = 0.0    # 最低
        self.side: KSide = KSide.Init

    def __str__(self):
        up_str = f"[{self.pos_begin}]{self.lowest}⬈[{self.pos_end}]{self.highest}"
        down_str = f"[{self.pos_begin}]{self.highest}⬊[{self.pos_end}]{self.lowest}"
        init_str = f"[{self.pos_begin}]{self.lowest}⬅⮕[{self.pos_end}]{self.highest}"
        if self.side == KSide.UP:
            return up_str
        elif self.side == KSide.DOWN:
            return down_str
        else:
            return init_str

    def __repr__(self):
        return self.__str__()


class Segment:
    """段"""
    def __init__(self):
        self.start_index: int = 0
        self.end_index: int = 0
        self.highest: float = 0.0
        self.lowest: float = 0.0
        self.up: bool = False
        self.is_sure = False    # 是否被确认

    def __str__(self):
        up_seg = f"[{self.is_sure}][{self.start_index}]⬈[{self.end_index}]"
        down_seg = f"[{self.is_sure}][{self.start_index}]⬊[{self.end_index}]"
        if self.up:
            return up_seg
        else:
            return down_seg


class Pivot:
    """中枢"""
    def __init__(self):
        self.up: bool = False  # 中枢方向，True为向上，False为向下
        self.bg_pos_index: int = 0
        self.ed_pos_index: int = 0
        self.highly_value: float = 0.0
        self.lowly_value: float = 0.0

    def __str__(self):
        direction = "⬈" if self.up else "⬊"
        return (f"pos_index:[{self.bg_pos_index}]{direction}[{self.ed_pos_index}]"
                f",l:[{self.lowly_value}],h:[{self.highly_value}]")

    def __repr__(self):
        return self.__str__()
