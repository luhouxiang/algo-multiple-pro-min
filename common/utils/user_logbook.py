# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename:user_logbook.py
import datetime
import os

import logbook
from logbook import Logger, TimedRotatingFileHandler, FileHandler
from logbook.more import ColorizedStderrHandler


def user_handler_log_formatter(record, handler):  # [{func_name}]
    dt = record.time
    st = "{:02d}-{:02d}{:02d} {:02d}:{:02d}:{:02d}.{:03d}".format(
        dt.year % 100, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond // 1000)
    log = "[{dt}][{level}][{filename}][{lineno}] {msg}".format(
        dt=st,
        level=record.level_name,  # 日志等级
        filename=os.path.split(record.filename)[-1],  # 文件名
        # func_name=record.func_name,  # 函数名
        lineno=record.lineno,  # 行号
        msg=record.message,  # 日志内容
    )
    return log


class _InSideLog:
    main_log_dir = os.path.join('log')  # 日志路径，在主工程下生成log目录
    # 用户代码logger日志
    user_log = Logger("user_log")
    system_log = Logger("system_log")
    # 错误记录logger日志
    err_log = Logger('err_log')


def init_logger(path="../log", name="server", level="INFO", init_date=None):
    _InSideLog.main_log_dir = path
    if not os.path.exists(_InSideLog.main_log_dir):
        os.makedirs(_InSideLog.main_log_dir)

    logbook.set_datetime_format("local")

    _InSideLog.user_std_handler = ColorizedStderrHandler(bubble=True, level=level)
    _InSideLog.user_std_handler.formatter = user_handler_log_formatter

    # 打印到文件句柄
    if init_date:
        _InSideLog.user_file_handler = FileHandler(
            os.path.join(_InSideLog.main_log_dir,'user_{}-{}.log'.format(name, init_date)), bubble=True, level=level)
        _InSideLog.system_file_handler = FileHandler(
            os.path.join(_InSideLog.main_log_dir, 'system_{}-{}.log'.format(name, init_date)), bubble=True, level=level)
    else:
        _InSideLog.user_file_handler = TimedRotatingFileHandler(
            os.path.join(_InSideLog.main_log_dir, 'user_{}.log'.format(name)), date_format='%Y%m%d', bubble=True, level=level)

        _InSideLog.system_file_handler = TimedRotatingFileHandler(
            os.path.join(_InSideLog.main_log_dir, 'system_{}.log'.format(name)), date_format='%Y%m%d', bubble=True, level=level)

    _InSideLog.user_file_handler.formatter = user_handler_log_formatter
    _InSideLog.system_file_handler.formatter = user_handler_log_formatter

    _InSideLog.user_log.handlers = []
    _InSideLog.user_log.handlers.append(_InSideLog.user_std_handler)
    _InSideLog.user_log.handlers.append(_InSideLog.user_file_handler)
    _InSideLog.system_log.handlers = [_InSideLog.system_file_handler]


user_log = _InSideLog.user_log
system_log = _InSideLog.system_log
init_logger()

if __name__ == '__main__':
    # init_logger_postfix_v3('', '')
    # init_logger(name="mylog")
    user_log.info("abc")
    user_log.debug("bbb")
