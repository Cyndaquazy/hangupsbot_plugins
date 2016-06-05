"""timing plugin"""
import asyncio
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import logging
import plugins
import re

logger = logging.getLogger(__name__)

#parse strings:
pstrs_justTime   = ["%I:%M %p",             "%I:%M:%S %p",             "%H:%M",                "%H:%M:%S"               ,
                    "%I:%M %p %z",          "%I:%M:%S %p %z",          "%H:%M %z",             "%H:%M:%S %z"            ]

pstrs_dateTime   = ["%m/%d/%y %I:%M %p",    "%m/%d/%y %I:%M:%S %p",    "%m/%d/%Y %I:%M %p",    "%m/%d/%Y %I:%M:%S %p"   ,
                    "%m/%d/%y %H:%M",       "%m/%d/%y %H:%M:%S",       "%m/%d/%Y %H:%M",       "%m/%d/%Y %H:%M:%S"      ,
                    "%m/%d/%y %I:%M %p %z", "%m/%d/%y %I:%M:%S %p %z", "%m/%d/%Y %I:%M %p %z", "%m/%d/%Y %I:%M:%S %p %z",
                    "%m/%d/%y %H:%M %z",    "%m/%d/%y %H:%M:%S %z",    "%m/%d/%Y %H:%M %z",    "%m/%d/%Y %H:%M:%S %z"   ,
                    "%Y-%m-%dT%H:%M:%S%z",  "%Y-%m-%d %H:%M:%S%z",     "%Y-%m-%dT%H:%M:%S",    "%Y-%m-%d %H:%M:%S"      ]

# default timezone -- set via config file
tz_def = None

def _initialize(bot):
    global tz_def
    
    plugin_conf = bot.config.get_by_path(["timeme"])
    
    if not plugin_conf:
        plugin_conf = {"default_tz": [0, 0]}
        bot.config.set_by_path(["timeme"], plugin_conf)
        bot.config.save()
    
    default_tz = plugin_conf["default_tz"]
    tz_def = timezone(timedelta(hours=default_tz[0], minutes=default_tz[1]))

    logger.info("Default timezone offset: {}".format(tz_def))

    plugins.register_handler(_handle_timeme_action, type="message")
    plugins.register_user_command(["timeme"])

def _handle_timeme_action(bot, event, command):
    if event.text.startswith('/timer ') or event.text.startswith('/timeme '):
        full_tokens = re.split('\s+', event.text)
        if len(full_tokens) > 1:
            full_tokens[0] = "timeme"
            yield from asyncio.sleep(0.2)
            yield from command.run(bot, event, *full_tokens)

def timeme(bot, event, *args):
    """
    USAGE: /timeme [timestring] or /timer [timestring].
    
    Calculates the amount of time until or time since the moment represented by the given timestring.
    
    Accepts any timestring of the form
    <b>[12/31/[20]01] 11:59[:59] [AM/PM] [+2359]</b>
    or ISO format:
    <b>2001-12-31 23:59:59[+2359]</b>.
     
    If no date is specified, the current day is assumed; if no timezone offset is specified, then the default from the config file is assumed.
    """
    logger.info("{} sent timer request at {}".format(event.user.full_name, event.timestamp))
    timestring = ' '.join(args)
    
    time_recd = event.timestamp.astimezone(tz_def)
    time_req  = None
    have_time = False
    no_date   = True
    
    for pstr in pstrs_justTime:
        try:
            time_req = datetime.strptime(timestring, pstr)
            have_time = True
            time_req = time_req.replace(time_recd.year, time_recd.month, time_recd.day)
            break
        except ValueError:
            pass
    
    if not have_time:
        for pstr in pstrs_dateTime:
            try:
                time_req = datetime.strptime(timestring, pstr)
                have_time = True
                break
            except ValueError:
                pass
    
    if not time_req:
        yield from bot.coro_send_message(event.conv, "{} is not a recognized time string.".format(timestring))
        yield from bot.coro_send_message(event.conv,
            "I can read time strings like <br /> <b>[01/01/[20]01] 00:00[:00] [AM/PM] [+2359]</b>, <br /> or ISO format: <br /> <b>2001-01-01 00:00:00[+2359]</b>")
        yield from bot.coro_send_message(event.conv, "If no date is provided, then the current day is assumed, and if no timezone offset is provided, {} is assumed.".format(tz_def))
    else:
        if not time_req.tzinfo:
            time_req = time_req.replace(tzinfo=tz_def)
    
        delta = time_req - time_recd
        logger.info("Time Requested: {}\nEvent Time: {}\nDelta: {}".format(time_req, time_recd, delta))
        words = ["There are", "until"]
        days, seconds = delta.days, delta.seconds
        
        if days < 0:
            days += 1
            seconds = 86400 - seconds
            words = ["It has been", "since"]
        
        hrs, temp = divmod(seconds, 3600)
        mins, secs = divmod(temp, 60)
        
        qday = "days"; qhr = "hours"; qmin = "minutes"; qsec = "seconds"
        
        if days == 1:
            qday = qday[:-1]
            
        if hrs == 1:
            qhr = qhr[:-1]
            
        if mins == 1:
            qmin = qmin[:-1]
            
        if secs == 1:
            qsec = qsec[:-1]
       
        quants = ["{} {}".format(days, qday),
                  "{} {}".format(hrs, qhr),
                  "{} {}".format(mins, qmin),
                  "and {} {}".format(secs, qsec)]
        
        msg = "{} {} {} {}".format(words[0], ', '.join(quants), words[1], time_req)
        
        yield from bot.coro_send_message(event.conv, msg)
        
