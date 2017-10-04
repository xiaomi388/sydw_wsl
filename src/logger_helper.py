# coding:utf-8
import os

import logging
from logging import Logger
from logging.handlers import TimedRotatingFileHandler

'''日志管理类'''

#logger level : dubug < info < warning < error < critical

def init_logger(logger_name):
    if logger_name not in Logger.manager.loggerDict:
        logger1 = logging.getLogger(logger_name)
        logger1.setLevel(logging.DEBUG) #设置最低级别
        # logger1.setLevel(logging.DEBUG)
        df = '%Y-%m-%d %H:%M:%S'
        format_str = '[%(asctime)s]: %(name)s %(levelname)s %(lineno)s %(message)s'
        formatter = logging.Formatter(format_str,df)
        # handler all
        handler1 = TimedRotatingFileHandler(os.path.join(os.path.dirname(__file__), 'log','all.log'), when='D', interval=1, backupCount=7)
        handler1.setFormatter(formatter)
        handler1.setLevel(logging.INFO)
        logger1.addHandler(handler1)

        handler2 = TimedRotatingFileHandler(os.path.join(os.path.dirname(__file__), 'log','error.log'), when='D', interval=1, backupCount=7)
        handler2.setFormatter(formatter)
        handler2.setLevel(logging.WARNING)
        logger1.addHandler(handler2)

        #console = logging.StreamHandler()
        #console.setLevel(logging.DEBUG)
        ##set log print format
        #console.setFormatter(formatter)
        # 将定义好的console日志handler添加到root logger
        #logger1.addHandler(console)

    logger1 = logging.getLogger(logger_name)
    return logger1

logger = init_logger('runtime-log')

if __name__ == '__main__':
    logger.debug('test-of-debug')
    logger.info('test-of-info')
    logger.warn('test-of-warn')
    logger.error('test-of-warn')
