#!/usr/bin/env python3
# encoding: utf-8
"""
@author: lyl
@license: (C) Copyright 2017-2023, Dztec right.
@desc:这个文件主要定义一些全局的目录、或者是文件定义信息
"""
import os
from pathlib import Path
import yaml
from common.utils.singleton import Singleton
import logging


real_path = os.path.dirname(os.path.realpath(__file__))
curr_path = Path(real_path)
work_path = str(curr_path.parent)
LOG_PATH = os.path.join(work_path, "logs")
SNAPSHOT_PATH = os.path.join(work_path, "data/snapshot")  # 快照目录
BACKUP_PATH = os.path.join(work_path, "data/backup")  # 备份目录
OUTPUT_PATH = os.path.join(work_path, "data/output")  # 输出目录
OUTPUT_BK_PATH = os.path.join(work_path, "data/output_bk")  # 输出备份目录
OUTPUT_REDIS = os.path.join(work_path, "data/redis_data")  # redis数据输出目录(pickle文件)
OUTPUT_REDIS_PARQUET = os.path.join(work_path, "data/redis_data_pqt")  # redis数据输出目录(parquet文件)
OUTPUT_REDIS_LOCK_FILE = os.path.join(OUTPUT_REDIS, "my.lock")
OUTPUT_REDIS_PQT_LOCK_FILE = os.path.join(OUTPUT_REDIS_PARQUET, "my.lock")
OUTPUT_LOCK_FILE = os.path.join(OUTPUT_PATH, "my.lock")
OUTPUT_BK_LOCK_FILE = os.path.join(OUTPUT_BK_PATH, "my.lock")
SNAPSHOT_LOCK_FILE = os.path.join(SNAPSHOT_PATH, "my.lock")  # 输出目录存在多进程访问,需要用一个lock文件来加进程锁，避免文件访问冲突

PICKLE_QUOTE_SNAPSHOT_KEY = "quote"  # 行情快照保存为pickle的特殊名称，名称格式为 时间戳.quote.pkl
PICKLE_QUOTE_TICK_KEY = "tick"  # 分笔成交保存为pickle的特殊名称，名称格式为 时间戳.tick.pkl
PICKLE_QUOTE_BQ_KEY = "bq"  # 经纪人队列保存为pickle的特殊名称，名称格式为 时间戳.bq.pkl

SQLITE_DB_NAME = os.path.join(work_path, "db/dztec.db")  # 共享的sqlite数据库文件
CONF_PATH = os.path.join(work_path, "conf")
TMP_PATH = os.path.join(work_path, "data/tmp")

# redis key 和 mq的routing_key一样 (mq输出因子calc.output.exchange交换机 对应的routing_key)
REDIS_MQ_STOCK_FACTOR_OPEN_HK = "stock_factor_open_hk"      # 港股盘中因子
REDIS_MQ_STOCK_FACTOR_CLOSE_HK = "stock_factor_close_hk"    # 港股盘后因子
REDIS_MQ_STOCK_BLOCK_FACTOR_HK = "stock_block_factor_hk"    # 港股个股板块关联因子
REDIS_MQ_STOCK_FACTOR_OPEN_US = "stock_factor_open_us"      # 美股盘中因子
REDIS_MQ_STOCK_FACTOR_CLOSE_US = "stock_factor_close_us"    # 美股盘后因子
REDIS_MQ_STOCK_BLOCK_FACTOR_US = "stock_block_factor_us"    # 美股个股板块关联因子
REDIS_MQ_STOCK_FACTOR_BASIC_A = "stock_factor_basic_a"      # a股盘中因子basic
REDIS_MQ_STOCK_FACTOR_QUOTE_A = "stock_factor_quote_a"      # a股盘中因子quote
REDIS_MQ_STOCK_FACTOR_CAPITAL_A = "stock_factor_capital_a"  # a股盘中因子capital
REDIS_MQ_STOCK_FACTOR_YD_A = "stock_factor_yd_a"            # a股盘中因子竞价分析异动
REDIS_MQ_STOCK_FACTOR_CLOSE_A = "stock_factor_close_a"      # a股盘后因子
REDIS_MQ_STOCK_BLOCK_FACTOR_A = "stock_block_factor_a"      # a股个股板块关联因子(这只是个前缀，需要根据板块数据源添加后缀, 如_ths)

REDIS_MQ_BLOCK_FACTOR_BEFORE_HK = "block_factor_before_hk"  # 港股板块盘前因子
REDIS_MQ_BLOCK_FACTOR_OPEN_HK = "block_factor_open_hk"      # 港股板块盘中因子
REDIS_MQ_BLOCK_FACTOR_CLOSE_HK = "block_factor_close_hk"    # 港股板块盘后因子
REDIS_MQ_BLOCK_INFO_HK = "block_info_hk"                    # 港股板块成分股信息
REDIS_MQ_BLOCK_FACTOR_BEFORE_US = "block_factor_before_us"  # 美股板块盘前因子
REDIS_MQ_BLOCK_FACTOR_OPEN_US = "block_factor_open_us"      # 美股板块盘中因子
REDIS_MQ_BLOCK_FACTOR_CLOSE_US = "block_factor_close_us"    # 美股板块盘后因子
REDIS_MQ_BLOCK_INFO_US = "block_info_us"                    # 美股板块成分股信息

REDIS_MQ_BLOCK_FACTOR_BEFORE_A = "block_factor_before_a"    # a股板块盘前因子(这只是个前缀，需要根据板块数据源添加后缀, 如_ths)
REDIS_MQ_BLOCK_FACTOR_OPEN_A = "block_factor_open_a"        # a股板块盘中因子(这只是个前缀，需要根据板块数据源添加后缀, 如_ths)
REDIS_MQ_BLOCK_FACTOR_CLOSE_A = "block_factor_close_a"      # a股板块盘后因子(这只是个前缀，需要根据板块数据源添加后缀, 如_ths)
REDIS_MQ_BLOCK_INFO_A = "block_info_a"                      # a股板块成分股信息(这只是个前缀，需要根据板块数据源添加后缀, 如_ths)

REDIS_MQ_INDEX_FACTOR_BEFORE_HK = "index_factor_before_hk"  # 港股指数盘前因子
REDIS_MQ_INDEX_FACTOR_OPEN_HK = "index_factor_open_hk"      # 港股指数盘中因子
REDIS_MQ_INDEX_FACTOR_CLOSE_HK = "index_factor_close_hk"    # 港股指数盘后因子
REDIS_MQ_INDEX_FACTOR_BEFORE_US = "index_factor_before_us"  # 美股指数盘前因子
REDIS_MQ_INDEX_FACTOR_OPEN_US = "index_factor_open_us"      # 美股指数盘中因子
REDIS_MQ_INDEX_FACTOR_CLOSE_US = "index_factor_close_us"    # 美股指数盘后因子
REDIS_MQ_INDEX_FACTOR_BEFORE_A = "index_factor_before_a"    # a股指数盘前因子
REDIS_MQ_INDEX_FACTOR_OPEN_A = "index_factor_open_a"        # a股指数盘中因子
REDIS_MQ_INDEX_FACTOR_CLOSE_A = "index_factor_close_a"      # a股指数盘后因子

REDIS_MQ_MARKET_FACTOR_OPEN_HK = "market_factor_open_hk"    # 港股市场盘中因子
REDIS_MQ_MARKET_FACTOR_CLOSE_HK = "market_factor_close_hk"  # 港股市场盘后因子
REDIS_MQ_MARKET_FACTOR_OPEN_US = "market_factor_open_us"    # 美股市场盘中因子
REDIS_MQ_MARKET_FACTOR_CLOSE_US = "market_factor_close_us"  # 美股市场盘后因子
REDIS_MQ_MARKET_FACTOR_OPEN_A = "market_factor_open_a"      # a股市场盘中因子
REDIS_MQ_MARKET_FACTOR_CLOSE_A = "market_factor_close_a"    # a股市场盘后因子

# mysql基础数据表
SYMBOLS_TABLE = "symbols"                               # 码表数据库表
BIG_MARKET_TABLE = "big_markets"                        # 大市场数据库表
SUB_MARKET_TABLE = "sub_markets"                        # 小市场数据库表
TRADE_DAY_TABLE = "trade_day"                           # 交易日数据库表
TRADE_TIME_TABLE = "trade_time"                         # 交易时间数据库表
IPO_INFO_TABLE = "ipo_info"                             # ipo数据库表
BROKER_INFO_TABLE = "brokers_info"                      # 经纪人数据库表
BLOCK_INFO_TABLE = "block_info"                         # 板块数据库表(这只是个前缀，需要根据板块数据源添加后缀, 如_ths)
BLOCK_STOCK_INFO_TABLE = "block_stock_info"             # 板块成分股信息数据库表(这只是个前缀，需要根据板块数据源添加后缀, 如_ths)
INDEX_SYM_LIST_TABLE = "index_sym_list"                 # 指数商品列表

# mysql财务数据表
FINANCE_TABLE_HK = "finance_hk"                         # 港股财务数据库表
FINANCE_TABLE_US = "finance_us"                         # 美股财务数据库表
FINANCE_TABLE_A = "finance_a"                           # A股财务数据库表
MARGIN_TRADE_TABLE_A = "margin_trading"                 # A股融资融券数据库表

# sqlite个股预处理表
PRE_STOCK_FACTOR_TABLE_HK = "pre_stock_factor_hk"       # 港股预处理个股因子数据库表
PRE_BLOCK_FACTOR_TABLE_HK = "pre_block_factor_hk"       # 港股预处理板块因子数据库表(这只是个前缀，需要根据板块数据源添加后缀, 如_ths)
PRE_INDEX_FACTOR_TABLE_HK = "pre_index_factor_hk"       # 港股预处理指数因子数据库表
PRE_STOCK_FACTOR_TABLE_US = "pre_stock_factor_us"       # 美股预处理个股因子数据库表
PRE_BLOCK_FACTOR_TABLE_US = "pre_block_factor_us"       # 美股预处理板块因子数据库表(这只是个前缀，需要根据板块数据源添加后缀, 如_ths)
PRE_INDEX_FACTOR_TABLE_US = "pre_index_factor_us"       # 美股预处理指数因子数据库表
PRE_STOCK_FACTOR_TABLE_A = "pre_stock_factor_a"         # A股预处理个股因子数据库表
PRE_BLOCK_FACTOR_TABLE_A = "pre_block_factor_a"         # A股预处理板块因子数据库表(这只是个前缀，需要根据板块数据源添加后缀, 如_ths)
PRE_INDEX_FACTOR_TABLE_A = "pre_index_factor_a"         # A股预处理指数因子数据库表

# mysql个股历史因子表
STOCK_FACTOR_HIS_TABLE_HK = "stock_factor_his_hk"       # 港股因子历史数据库表
STOCK_FACTOR_HIS_TABLE_US = "stock_factor_his_us"       # 美股因子历史数据库表
STOCK_FACTOR_HIS_TABLE_A = "stock_factor_his_a"         # A股因子历史数据库表
STOCK_BLOCK_FACTOR_HIS_TABLE_HK = "stock_block_factor_his_hk"     # 港股个股板块关联因子历史数据库表(这只是个前缀，需要根据板块数据源添加后缀, 如_ths)
STOCK_BLOCK_FACTOR_HIS_TABLE_US = "stock_block_factor_his_us"     # 美股个股板块关联因子历史数据库表(这只是个前缀，需要根据板块数据源添加后缀, 如_ths)
STOCK_BLOCK_FACTOR_HIS_TABLE_A = "stock_block_factor_his_a"       # A股个股板块关联因子历史数据库表(这只是个前缀，需要根据板块数据源添加后缀, 如_ths)

# mysql板块历史因子表
BLOCK_FACTOR_HIS_TABLE_HK = "block_factor_his_hk"       # 港股板块因子历史数据库表
BLOCK_FACTOR_HIS_TABLE_US = "block_factor_his_us"       # 美股板块因子历史数据库表
BLOCK_FACTOR_HIS_TABLE_A = "block_factor_his_a"         # A股板块因子历史数据库表(这只是个前缀，需要根据板块数据源添加后缀, 如_ths)

# mysql标准指数历史因子表
INDEX_FACTOR_HIS_TABLE_HK = "index_factor_his_hk"       # 港股标准指数因子历史数据库表
INDEX_FACTOR_HIS_TABLE_US = "index_factor_his_us"       # 美股标准指数因子历史数据库表
INDEX_FACTOR_HIS_TABLE_A = "index_factor_his_a"         # A股标准指数因子历史数据库表

# mysql市场历史因子表
MARKET_FACTOR_HIS_TABLE_HK = "market_factor_his_hk"       # 港股市场因子历史数据库表
MARKET_FACTOR_HIS_TABLE_US = "market_factor_his_us"       # 美股市场因子历史数据库表
MARKET_FACTOR_HIS_TABLE_A = "market_factor_his_a"         # A股市场因子历史数据库表

# mysql涨停开板池，跌停开板池历史因子表
OPEN_PLATE_POOL_FACTOR_TABLE_A = "open_plate_pool_factor_a"         # A股涨停开板池，跌停开板池历史因子表

# mysql竞价分析表历史因子表
AUCTION_ANALYSIS_TABLE_A = "auction_analysis_a"                     # A股竞价分析表历史因子表

# mysql指数竞价走势表
AUCTION_TREND_TABLE_A = "auction_trend_a"                           # A股指数竞价走势表

# 因子输出文件名字
STOCK_FACTOR_OPEN_BASIC_FILE = "stock_factor_open_basic.pkl"        # 输出个股盘中基础因子文件
STOCK_FACTOR_OPEN_QUOTE_FILE = "stock_factor_open_quote.pkl"        # 输出个股盘中行情因子文件
STOCK_FACTOR_OPEN_CAPITAL_FILE = "stock_factor_open_capital.pkl"    # 输出个股盘中资金流向因子文件
STOCK_FACTOR_OPEN_YD_FILE = "stock_factor_open_yd.pkl"              # 输出个股盘中竞价分析异动因子文件
STOCK_FACTOR_CLOSE_FILE = "stock_factor_close.pkl"                  # 输出个股盘后因子文件
STOCK_BLOCK_FACTOR_FILE = "stock_block_factor.pkl"                  # 输出个股板块关联因子文件(这只是个前缀，需要根据板块数据源添加后缀, 如_ths)
INDEX_FACTOR_BEFORE_FILE = "index_factor_before.pkl"                # 输出标准指数盘前因子文件
INDEX_FACTOR_OPEN_FILE = "index_factor_open.pkl"                    # 输出标准指数盘中因子文件
INDEX_FACTOR_CLOSE_FILE = "index_factor_close.pkl"                  # 输出标准指数盘后因子文件
BLOCK_FACTOR_BEFORE_FILE = "block_factor_before.pkl"    # 输出板块指数盘前因子文件(这只是个前缀，需要根据板块数据源添加后缀, 如_ths)
BLOCK_FACTOR_OPEN_FILE = "block_factor_open.pkl"        # 输出板块指数盘中因子文件(这只是个前缀，需要根据板块数据源添加后缀, 如_ths)
BLOCK_FACTOR_CLOSE_FILE = "block_factor_close.pkl"      # 输出板块指数盘后因子文件(这只是个前缀，需要根据板块数据源添加后缀, 如_ths)
MARKET_FACTOR_OPEN_FILE = "market_factor_open.pkl"                   # 输出市场盘中因子文件
MARKET_FACTOR_CLOSE_FILE = "market_factor_close.pkl"                 # 输出市场盘后因子文件

# 计算中心端口
CALC_CENTER_HTTP_PORT = 30238

@Singleton
class Cfg():
    def __init__(self, path):
        self.path = path
        self.conf = {}

    def load_yaml(self):
        # path = CFG_FN
        logging.info(f"conf_path: {self.path}")
        with open(self.path, 'r', encoding='utf-8') as f:
            self.conf = yaml.safe_load(f)
            # config = yaml.load(f, Loader=yaml.FullLoader)
            # config = yaml.load(f.read(), Loader=yaml.FullLoader)
            # yaml.dump(data, f, default_flow_style=False, encoding='utf-8', allow_unicode=True)

        return self.conf


