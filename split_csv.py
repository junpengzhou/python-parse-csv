#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
High-performance CSV splitter - supports 100GB+ files.
Compatible with Python 3.6+

Usage:
    python split_csv.py <input_csv> [chunk_size]
Example:
    python split_csv.py /data/redis8/rdb/dump_prefix.csv 5000
"""

import os
import sys
import time

READ_BUF = 128 * 1024 * 1024  # 128MB read buffer
WRITE_BUF = 64 * 1024 * 1024  # 64MB write buffer


def split_csv(input_file, chunk_size=5000):
    # 校验csv文件存在并是文件
    if not os.path.isfile(input_file):
        print("Error: file not found: {}".format(input_file))
        sys.exit(1)

    # 打印csv文件信息
    file_size = os.path.getsize(input_file)
    print("Input : {}".format(input_file))
    print("Size  : {:.2f} GB ({:,} bytes)".format(file_size / (1024 ** 3), file_size))
    print("Chunk : {} rows per file".format(chunk_size))
    print("-" * 60)

    base, ext = os.path.splitext(input_file)
    start_time = time.time()
    total_rows = 0
    file_count = 0

    # 开启输入流开始作业
    with open(input_file, 'rb', buffering=READ_BUF) as f_in:
        header = f_in.readline()

        eof = False
        while not eof:
            lines = []
            for _ in range(chunk_size):
                line = f_in.readline()
                if not line:
                    eof = True
                    break
                lines.append(line)

            if not lines:
                break

            file_count += 1
            start_row = total_rows + 1
            total_rows += len(lines)

            out_path = "{}_{}-{}{}".format(base, start_row, total_rows, ext)

            # 切割形成输出
            with open(out_path, 'wb', buffering=WRITE_BUF) as f_out:
                f_out.write(header)
                f_out.writelines(lines)

            del lines

            if file_count % 100 == 0 or eof:
                elapsed = time.time() - start_time
                pos = f_in.tell()
                progress = pos / file_size * 100 if file_size > 0 else 100
                speed = pos / (1024 ** 2) / elapsed if elapsed > 0 else 0
                print("[{:5.1f}%] {} files | {:,} rows | {:.1f} MB/s | {:.0f}s elapsed".format(
                    progress, file_count, total_rows, speed, elapsed))

    elapsed = time.time() - start_time
    speed = file_size / (1024 ** 2) / elapsed if elapsed > 0 else 0
    print("-" * 60)
    print("Completed! {} files, {:,} total rows".format(file_count, total_rows))
    print("Time: {:.1f}s | Avg Speed: {:.1f} MB/s".format(elapsed, speed))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python {} <csv_file> [chunk_size]".format(sys.argv[0]))
        print("  chunk_size: rows per file, default 5000")
        sys.exit(1)

    csv_file = sys.argv[1]
    rows = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    split_csv(csv_file, rows)
