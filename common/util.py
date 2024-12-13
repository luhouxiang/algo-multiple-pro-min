import datetime
import json
import time
import logging
import os
import portalocker
import configparser
import gzip
import numpy as np
from common.config import LOG_PATH
from line_profiler import LineProfiler
import pandas as pd
from contextlib import contextmanager
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
from functools import wraps
import pickle
import threading
from cachetools import TTLCache

# 全局的定时调度器
# 注意: 这个定时器是单线程调度的,当一个没处理完,又启动了下一个, 下一个就无法启动
# g_scheduler = BackgroundScheduler(timezone='Asia/Shanghai', misfire_grace_time=600)
# logger = logging.getLogger('apscheduler')
# logger.setLevel(logging.WARNING)


def time_cost(func):
    """
    统计函数运行时间的装饰器
    :param func: 函数名称
    :return: 函数本身运行结果
    """

    def inner(*s, **gs):
        start_time = time.time()
        ret = func(*s, **gs)
        end_time = time.time()
        spend_time = np.round(end_time - start_time, 4)
        full_name = func.__module__
        filename = full_name[full_name.rfind('.') + 1:]
        logging.warning("COST TIME:{}({}) {} second.".format(filename, func.__name__, spend_time))
        return ret

    return inner


@contextmanager
def time_ctx(desc):
    """
    统计一段代码的运行时间
    :param desc:对这段代码的说明
    :return: None
    用法:
        with time_ctx("xxx功能"):
            xxx
    """
    start_time = time.time()  # 记录进入with语句块前的时间戳
    yield  # 执行代码块
    end_time = time.time()  # 记录退出with语句块后的时间戳
    spend_time = end_time - start_time  # 计算代码块的运行时间
    logging.warning(f"COST TIME: {desc} {spend_time} second.")


def func_line_time(f):
    """
    查询接口中每行代码执行时间的装饰器
    :param f: 函数名称
    :return: 函数运行结果
    """

    @wraps(f)
    def decorator(*args, **kwargs):
        lp = LineProfiler()
        lp_wrap = lp(f)
        func_return = lp_wrap(*args, **kwargs)
        lp.print_stats()
        return func_return

    return decorator


def my_lock(func):
    """
    对函数进行加锁的装饰器,一定要定义_mutex类变量或者是实例变量,同样有效,增加这个包装的原因是要减少函数的嵌套层次
    :param func: 函数名
    :return: 函数运行结果
    """

    def inner(self, *args, **kwargs):
        with self._mutex:
            return func(self, *args, **kwargs)

    return inner


def get_datetime():
    """
    获取当前的年月日 时分秒,方便用于文件命名
    :param:
    :return: datetime
    """
    return datetime.datetime.now().strftime('%Y%m%d_%H%M%S.%f')


@contextmanager
def file_locker(filename, filetype='r'):
    """
    文件锁, 通过操作系统的文件锁来保证多进程不出问题
    :param filename: 文件名
    :param filetype: 文件打开方式
    :return: None
    用法:
        with file_locker("xxxx.lock"):
            xxx
    """
    try:
        f = open(filename, filetype)
        portalocker.lock(f, portalocker.LOCK_EX)
        yield f
    except Exception as e:
        raise e
    finally:
        portalocker.unlock(f)


@contextmanager
def auto_file_locker(filename):
    """
    文件锁, 用来替代file_locker, 它能够自动创建.lock锁文件,
    .lock命名方式为【.__xxx.lock】
    :param filename: 文件名
    :return: None
    用法:
        with auto_file_locker("xxx_file"):
            xxx
    """
    try:
        dir_name = os.path.dirname(filename)
        base_name = os.path.basename(filename)
        lock_file_name = ".__" + base_name + ".lock"
        lock_file_path = os.path.join(dir_name, lock_file_name)

        if not os.path.exists(lock_file_path):
            with open(lock_file_path, 'w') as file:
                pass

        f = open(lock_file_path, 'r')
        portalocker.lock(f, portalocker.LOCK_EX)
        yield f
    except Exception as e:
        logging.exception(e)
    finally:
        portalocker.unlock(f)


@contextmanager
def sqlite3_conn(filename, *args, **argv):
    """
    sqlite3 连接自动释放
    :param filename: sqlite文件名
    :param args:
    :param argv:
    :return: None
    用法:
        with sqlite3_conn("xxxx.db", check_same_thread=False) as conn:
            df = pd.read_sql(sql, conn)
    """
    try:
        conn = sqlite3.connect(filename, *args, **argv)
        yield conn
    except Exception as e:
        raise e
    finally:
        conn.close()


class AutoSaveDict(dict):
    """
    修改后够自动保存的Dict
    构造的时候,需要传一个文件名进去
    """

    def __init__(self, filename, *args, **kwargs):
        self.filename = filename
        super().__init__(*args, **kwargs)
        try:
            if not os.path.exists(filename):
                with open(filename, 'w') as f:
                    json.dump({}, f)

            with open(filename) as f:
                data = json.load(f)
                self.update(data)
        except Exception as e:
            logging.exception(e)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._save_to_file()

    def __delitem__(self, key):
        super().__delitem__(key)
        self._save_to_file()

    def _save_to_file(self):
        with open(self.filename, 'w') as f:
            json.dump(self, f)


def compress_file(src, dst, level):
    """
    将源文件压缩,生成目标文件
    :param src: 源文件
    :param dst: 压缩后的目标文件
    :param level: 压缩等级(压缩级别越高,压缩比就越高,但同时也会消耗更多的CPU时间和内存)
    :return: None
    """
    with open(src, 'rb') as f_in, gzip.open(dst, 'wb', compresslevel=level) as f_out:
        f_out.write(f_in.read())


def decompress_file(filename):
    """
    解压文件到原有目录,保留源文件
    :param filename: 文件名
    :return: None
    """
    file_out, _ = os.path.splitext(filename)  # 这里得到非压缩文件名
    with gzip.open(filename, 'rb') as f_in, open(file_out, 'wb') as f_out:
        f_out.write(f_in.read())


def remove_file_if_exists(file_path):
    """
    如果文件存在,则删除文件
    :param file_path: 文件名
    :return: None
    """
    if os.path.exists(file_path):
        os.remove(file_path)


def read_config(filename, section, option):
    """
    从ini格式的配置文件中读取配置
    :param filename: 配置文件名
    :param section: 指定某个section
    :param option: 指定某一个参数
    :return: 配置信息
    """
    config = configparser.ConfigParser()
    config.read(filename, encoding="utf-8")
    value = config.get(section, option)
    return value


def get_pickle_quote_filename(dt: datetime.datetime, index: int, quote_key: str) -> str:
    """
    获取行情保存的pickle纯文件名
    :param dt: 对应时间戳，只会精确到秒
    :param index: 对应文件索引
    :param quote_key: 文件特殊键值，比如 config.PICKLE_QUOTE_SNAPSHOT_KEY/PICKLE_QUOTE_TICK_KEY
    :return: 合成的文件名，yyyymmdd_HHMMSS.index.quote_key.pkl 的字串
    """
    return f'{dt.strftime("%Y%m%d_%H%M%S")}.{index}.{quote_key}.pkl'


def parse_pickle_quote_filename(filename: str):
    """
    解析行情保存的pickle纯文件名
    :param filename: 合成的文件名，get_pickle_quote_filename 返回的字串
    :return: datetime,index,quote_key 的元组，如果失败，则返回 None,None,None
    """
    ss = filename.split('.')
    if len(ss) != 4:
        return None, None, None
    if ss[-1] != 'pkl':
        return None, None, None
    return datetime.datetime.strptime(ss[0], "%Y%m%d_%H%M%S"), int(ss[1]), str(ss[2])


def create_log_sub_path(path_name: str):
    """
    检查并创建需要保存的日志子目录
    :param path_name: 子目录名字
    :return: None
    """
    sub_path = os.path.join(LOG_PATH, path_name)
    os.makedirs(sub_path, exist_ok=True)
    return sub_path


def time_lag_show(n: float = 0.2):
    """
    # 如果函数被封装函数执行超过n秒，那么给与警告日志
    # 用法:
    # @time_lag_show(0.2)
    # def func():....
    :param n: 超过n秒才告警日志
    :return: 封装函数
    """

    def _warp_f(func):
        def inner(*s, **gs):
            start_time = time.time()
            ret = func(*s, **gs)
            end_time = time.time()
            spend_time = end_time - start_time
            if spend_time > n:
                logging.warning("RUN_LAG:{} {:0.4f} second.".format(func.__name__, spend_time))
            return ret

        return inner

    return _warp_f


def set_df_datatype_to_src(dst_df: pd.DataFrame, src_df: pd.DataFrame, copy_if_chg=True) -> pd.DataFrame:
    """
    设置目标df的同名字段的数据类型为 原始df的数据类型, 并返回修改后的df
    :param dst_df: 目标df
    :param src_df: 源df
    :param copy_if_chg: bool 如果类型变更， 是否复制
    :return: 返回最终的df
    """
    src_dtypes = src_df.dtypes
    dst_dtypes = dst_df.dtypes
    need_convs = {}
    for col in src_dtypes.index.intersection(dst_dtypes.index).to_list():
        if src_dtypes[col] != dst_dtypes[col]:
            need_convs[col] = src_dtypes[col]
    if len(need_convs) > 0:
        return dst_df.astype(need_convs, copy=copy_if_chg)
    return dst_df


def func_cache_with_ttl(cache):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = (func.__name__, args, str(kwargs.items()))
            # 检查缓存中是否存在对应的键
            if cache_key in cache:
                # 返回缓存值
                return cache[cache_key]
            result = func(*args, **kwargs)
            # 将结果存入缓存，并设置对应的过期时间
            cache[cache_key] = result
            return result

        return wrapper

    return decorator


# 下面这两个变量给check_file_modified函数使用
file_modified_dict = {}
file_modified_lock = threading.Lock()


def check_file_modified(file_path):
    """
    传入一个文件,判断该文件是否修改
    函数会把所有调用这个函数的文件名的信息都放入dict,并记录上次访问的时间,如果有更新,则返回True
    如果没有更新,则返回False, 第一次调用时总是返回True
    :param file_path:文件名
    :return: True:已经修改, False:未修改
    """
    with file_modified_lock:
        if file_path not in file_modified_dict:
            try:
                logging.info(f"{file_path} first check. return True.")
                file_modified_dict[file_path] = os.path.getmtime(file_path)
            except Exception as e:
                logging.exception(e)
            return True
        else:
            current_modified_time = os.path.getmtime(file_path)

            if current_modified_time > file_modified_dict[file_path]:
                logging.info(f"{file_path} has been modified. return True.")
                # 在这里执行需要处理的操作
                file_modified_dict[file_path] = current_modified_time  # 更新保存时间
                return True
            else:
                return False


def cache_init_func_result(func):
    """
    返回函数最近调用结果的缓存数据的装饰器
    大数据量耗时初始函数,进行缓存，目录为cached_results,时间为1天，
    如果当天已经调用过这个函数,则直接从文件中返回结果,而不是去请求网络或者是数据库,提升调试时的效率
    这项功能主要给开发的时候使用
    注意,如果数据要刷新,请记得删除缓存
    :param func: 函数名称
    :return: pickle后的数据
    """
    cache_dir = "cached_results"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    def wrapper(*args, **kwargs):
        key = f"{func.__name__}"
        key = key[:200]  # 文件名称不能过长,最大200字符,所以这里如果调用的参数信息量过大,可能会重复
        cache_file = os.path.join(cache_dir, f"{key}.pkl")
        with auto_file_locker(cache_file):
            if os.path.exists(cache_file):
                file_time = os.path.getmtime(cache_file)
                current_time = time.time()
                if current_time - file_time < 3600*6:  # 缓存有效时间为1天
                    with open(cache_file, "rb") as file:
                        result = pickle.load(file)
                    logging.info(f"Result loaded from cache for {func.__name__}")
                    return result

            result = func(*args, **kwargs)

            with open(cache_file, "wb") as file:
                pickle.dump(result, file)
            logging.info(f"Result saved to cache for {func.__name__}")

        return result

    return wrapper


if __name__ == "__main__":
    with file_locker(r"C:\code\dianhuo\data\output\my.lock"):
        df = pd.read_hdf(r"C:\code\dianhuo\data\output\20230303_111802.240251.hdf")
