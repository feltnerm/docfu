# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import logging

from logging import Formatter, getLogger, StreamHandler, DEBUG
from logging.handlers import SMTPHandler

# colorful logging taken from:
# https://github.com/getpelican/pelican/blob/0548b6/pelican/log.py

RESET_TERM = '\033[0;m'

COLOR_CODES = {
    'red': 31,
    'yellow': 33,
    'cyan': 36,
    'white': 37,
    'bgred': 41,
    'bggrey': 100,
}


def ansi(color, text):
    """ Wrap text in an ansi escape sequence."""
    code = COLOR_CODES[color]
    return '\033[1;{0}m{1}{2}'.format(code, text, RESET_TERM)


class EmailFormatter(Formatter):
    """
    Convert a `logging.LogRecord' object into an email.
    """

    def format(self, record):
        return '''
        Message type:       %(levelname)s
        Location:           %(pathname)s:%(lineno)d
        Module:             %(module)s
        Function:           %(funcName)s
        Time:               %(asctime)s

        Message

        %(message)s
        ''' % record.getMessage()


class ANSIFormatter(Formatter):
    """ Convert a `logging.LogRecord` object into colored text, using ANSI
    escape sequences."""

    def format(self, record):
        msg = record.getMessage()
        if record.levelname == 'INFO':
            return ansi('cyan', '-> ') + msg
        elif record.levelname == 'WARNING':
            return ansi('yellow', record.levelname) + ': ' + msg
        elif record.levelname == 'ERROR':
            return ansi('red', record.levelname) + ': ' + msg
        elif record.levelname == 'CRITICAL':
            return ansi('bgred', record.levelname) + ': ' + msg
        elif record.levelname == 'DEBUG':
            return ansi('bggrey', record.levelname) + ': ' + msg
        else:
            return ansi('white', record.levelname) + ': ' + msg


class TextFormatter(Formatter):
    """
    Convert a `logging.LogRecord' object into text.
    """

    def format(self, record):
        if not record.levelname or record.levelname == 'INFO':
            return record.getMessage()
        else:
            return record.levelname + ': ' + record.getMessage()


def init(level=None, logger=getLogger(), handler=StreamHandler(), development=True):
    logging.basicConfig(level=level, datefmt='%m-%d %H:%M')
    logger = logging.getLogger()

    if (os.isatty(sys.stdout.fileno())
            and not sys.platform.startswith('win')):
        fmt = ANSIFormatter()
    else:
        fmt = TextFormatter()
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    if level:
        logger.setLevel(level)

    if not development:
        logger.info("Setting up email handler for production-mode.")
        fmt = EmailFormatter()
        smtpHandler = SMTPHandler('127.0.0.1', 'docfu@docs.fineuploader.com',
            ['alerts@fineuploader.com'], 'ALERT docfu error!')
        smtpHandler.setFormatter(fmt)
        smtpHandler.setLevel(logging.ERROR)
        logger.addHandler(smtpHandler)

    return logger

# test
if __name__ == '__main__':
    init(level=DEBUG)
    root_logger = logging.getLogger()
    root_logger.debug('debug')
    root_logger.info('info')
    root_logger.warning('warning')
    root_logger.error('error')
    root_logger.critical('critical')
