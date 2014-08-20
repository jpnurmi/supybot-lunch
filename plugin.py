###
# Copyright (c) 2014, J-P Nurmi
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.ircmsgs as ircmsgs
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.schedule as schedule
import supybot.callbacks as callbacks

import bs4
import time
import string
import urllib2
import calendar
import datetime
from dateutil.relativedelta import *

class Lunch(callbacks.Plugin):
    """Add the help for "@plugin help Lunch" here
    This should describe *how* to use this plugin."""

    def __init__(self, irc):
        self.__parent = super(Lunch, self)
        self.__parent.__init__(irc)
        self.irc = irc
        schedule.addPeriodicEvent(self._check, self.registryValue('period'), 'lunch')

    def die(self):
        schedule.removeEvent('lunch')
        self.__parent.die()

    def _check(self):
        menu = self._menu()
        channels = self.registryValue('channels').split(',')
        for channel in channels:
            topic = self.irc.state.channels[channel].topic
            if topic != menu:
                self.irc.queueMsg(ircmsgs.topic(channel, menu))

    def _menu(self, query=None):
        url = self.registryValue('url')
        soup = bs4.BeautifulSoup(urllib2.urlopen(url).read())

        # <table class="iTable ukesmeny">
        #   <thead>
        #     <tr><th>Mandag / Monday</th></tr>
        #     ...
        #   </thead>
        #   <tbody>
        #     <tr><td><p>Fish and chips</p></td></tr>
        #     ...
        #   </tbody>
        # </table>

        table = soup.find('table', attrs={'class': 'iTable ukesmeny'})
        keys = [th.string for th in table.find_all('th')]
        values = []
        for td in table.find_all('td'):
            values.append(', '.join([' '.join(p.stripped_strings) for p in td.find_all('p')]))
        values = dict(zip(keys, values))

        day = query or calendar.day_name[datetime.datetime.today().weekday()]
        for match in [key for key in keys for word in key.split() if len(word) > 1 and word.lower().startswith(day.lower())]:
            if values[match]:
                return '%s: %s - %s' % (match.encode('utf-8'), values[match].encode('utf-8'), url)
        return url

    def lunch(self, irc, msg, args, query):
        """ <day>

        Eurest BI (Oslo) lunch menu for the given day.
        """
        irc.reply(self._menu(query))

    lunch = wrap(lunch, [additional('text')])

Class = Lunch

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
