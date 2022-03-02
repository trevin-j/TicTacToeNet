'''
Module for debug logging.
'''

class dLog:
    '''
    A class for logging messages to the console.
    Has 3 separate log levels.
    '''

    LOGLEVEL_DEBUG = 0
    LOGLEVEL_INFO = 1
    LOGLEVEL_WARNING = 2
    LOGLEVEL_ERROR = 3
    LOGLEVEL_QUIET = 4

    def __init__(self, loglevel=LOGLEVEL_ERROR):
        self._loglevel = loglevel
        self._debug = False

    # Logging methods
    def log_debug(self, message):
        if self._loglevel <= dLog.LOGLEVEL_DEBUG:
            print("[DEBUG]: " + message)

    def log_info(self, message):
        if self._loglevel <= dLog.LOGLEVEL_INFO:
            print("[INFO]: " + message)
            
    def log_warning(self, message):
        if self._loglevel <= dLog.LOGLEVEL_WARNING:
            print("[WARNING]: " + message)

    def log_error(self, message):
        if self._loglevel <= dLog.LOGLEVEL_ERROR:
            print("[ERROR]: " + message)
