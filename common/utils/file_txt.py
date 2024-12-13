import os
from typing import List
import logging

def read_file(file_name) -> List[str]:
    """
    读取文本文件，返回list[str]
    """
    lines = []
    abs_path = os.path.abspath(file_name)
    logging.info(f"read_file: {abs_path}")
    if not os.path.exists(file_name):
        return lines
    with open(file_name, 'r') as f:
        f.readline()
        while line := f.readline():
            # print(line[:-1])
            lines.append(line[:-1])
    return lines


def write_file(file_name, lines: List[str], append: bool):
    """
    写文件， append为True表示追加，否则重新创新
    """
    if append:
        with open(file_name, 'a') as f:
            for line in lines:
                f.write(F"{line}\n")
            f.flush()
    else:
        with open(file_name, 'w') as f:
            for line in lines:
                f.write(F"{line}\n")
            f.flush()
