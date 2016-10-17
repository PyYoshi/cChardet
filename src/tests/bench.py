#!/usr/bin/env python
# coding: utf-8

import time

import cchardet
import chardet


def main():
    do_times = 100
    path = r'tests/testdata/wikipediaJa_One_Thousand_and_One_Nights_SJIS.txt'
    with open(path, 'rb') as f:
        msg = f.read()

        # Test chardet
        result_chardet = 0
        for i in range(do_times):
            start_chardet = time.time()
            chardet.detect(msg)
            result_chardet += (time.time() - start_chardet)
        print('chardet:', 1 / (result_chardet / do_times), 'call(s)/s')

        # Test cchardet
        result_cchardet = 0
        for i in range(do_times):
            start_cchardet = time.time()
            cchardet.detect(msg)
            result_cchardet += (time.time() - start_cchardet)
        print('cchardet:', 1 / (result_cchardet / do_times), 'call(s)/s')

if __name__ == '__main__':
    main()
