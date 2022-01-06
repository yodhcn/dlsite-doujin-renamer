import logging

import wx
import wx.lib.newevent

# create event type
wxLogEvent, EVT_WX_LOG_EVENT = wx.lib.newevent.NewEvent()


class WxLogHandler(logging.Handler):
    """
    A handler class which sends log strings to a wx object
    https://stackoverflow.com/a/2820928
    """

    def __init__(self, wx_dest: wx.Window):
        """
        Initialize the handler
        @param wx_dest: the destination object to post the event to
        """
        logging.Handler.__init__(self)
        self.__wxDest = wx_dest
        self.level = logging.DEBUG

    def flush(self):
        """
        does nothing for this handler
        """

    def emit(self, record):
        """
        Emit a record.
        """
        try:
            msg = self.format(record)
            evt = wxLogEvent(message=msg, levelno=record.levelno)
            wx.PostEvent(self.__wxDest, evt)
        except (KeyboardInterrupt, SystemExit) as err:
            raise err
        except Exception:
            self.handleError(record)
