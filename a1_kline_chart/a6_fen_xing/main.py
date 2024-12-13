#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
work_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(work_dir)     # 设定指定目录为工作目录
sys.path.append(work_dir)
from common.logging_cfg import SysLogInit
from common.ui_main_window import MainWindow, app
import logging
from cfg import g_cfg




if __name__ == '__main__':
    SysLogInit('a6_fen_xing', 'logs/a1_kline_chart/a6_fen_xing')
    g_cfg.load_yaml()   # 默认最先加载配置文件
    logging.info(f"...... ...... work begin... work_dir:{work_dir}")
    logging.error("abcd")
    logger = logging.getLogger(__name__)
    logger.info("color test...")

    w = MainWindow(g_cfg.conf)
    w.resize(1024, 768)
    w.show()
    app.exec()
