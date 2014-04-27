# Plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2014 ph03n1x
# ph03n1x9000@hotmail.com
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# Changelog
#   04/20/2014 - 1.0.1 - ph03n1x
#   - Made admin unkickable unless he is ci
#   03/01/2014 - 1.0.0 - Walker
#   - Combined ThorN's pingwatch and Walker's pingkicker plugins
#   

__author__  = 'Walker, ph03n1x'
__version__ = '1.0.1'



import b3, time, thread
import b3.events
import b3.plugin
import b3.cron

#--------------------------------------------------------------------------------------------------
class PingInfo:
    _1stPingTime = 0
    _2ndPingTime = 0
#--------------------------------------------------------------------------------------------------
class BadpingyPlugin(b3.plugin.Plugin):
    _interval = 0
    _maxPing = 0
    _maxPingDuration = 0
    _ignoreTill = 0
    _cronTab = None
    _maxCiPing = 500
    _minLevel = 20
    _clientvar_name = 'ping_info'

    def onStartup(self):
        self.registerEvent(b3.events.EVT_GAME_EXIT)
        # dont check pings on startup
        self._ignoreTill = self.console.time() + 120

    def onLoadConfig(self):
        self._interval = self.config.getint('settings', 'interval')
        self._maxPing = self.config.getint('settings', 'max_ping')
        self._maxPingDuration = self.config.getint('settings', 'max_ping_duration')
        self._max_level = self.config.getint('settings', 'max_level_checked')
        self._minLevel = self.config.getint('commands', 'ci')

        if self._cronTab:
            # remove existing crontab
            self.console.cron - self._cronTab

        self._cronTab = b3.cron.PluginCronTab(self, self.check, '*/%s' % self._interval)
        self.console.cron + self._cronTab
        self._adminPlugin = self.console.getPlugin('admin')
        self._adminPlugin.registerCommand(self, 'ci', self._minLevel, self.cmd_ci)

    def onEvent(self, event):
        if event.type == b3.events.EVT_GAME_EXIT:
            # ignore ping watching for 2 minutes
            self._ignoreTill = self.console.time() + 120

    def get_ping_info(self, client):
        # get the PingInfo stats
        if not client.isvar(self, self._clientvar_name):
            # initialize the default PingInfo object
            client.setvar(self, self._clientvar_name, PingInfo())
            
        return client.var(self, self._clientvar_name).value

    def check(self):
        if self.isEnabled() and (self.console.time() > self._ignoreTill):        
            for cid,ping in self.console.getPlayerPings().items():
                #self.console.verbose('ping %s = %s', cid, ping)
                if ping > self._maxPing:
                    client = self.console.clients.getByCID(cid)
                    if client:
                        if client.maxLevel < self._max_level: #kick if not admin
                            if pingInfo._1stPingTime > 0:
                                if  self.console.time() - pingInfo._1stPingTime >= self._maxPingDuration and self.console.time() - pingInfo._2ndPingTime < (self._interval + 3):
                                    # Max ping duration has gone by and he hasn't missed a ping interval. Kicking time!
                                    client.kick(self.getMessage('public_ping_kick_message', { 'ping' : ping }))
                                elif self.console.time() - pingInfo._2ndPingTime > (self._interval + 3) :
                                    # There is a gap between ping measures, maybe it was a ping spike. Reset counters
                                    pingInfo._1stPingTime = self.console.time()
                                    pingInfo._2ndPingTime = self.console.time()
                                    if ping != 999:
                                        client.message(self.getMessage('first_ping_warning'))
                                    else:
                                        # Ping is still too high, but not longer than max ping duration.
                                        pingInfo._2ndPingTime = self.console.time()
                                        if ping != 999:
                                            client.message(self.getMessage('reminder_ping_warning'))
                            else:
                                # Ping is too high, this is the first time.
                                pingInfo._1stPingTime = self.console.time()
                                pingInfo._2ndPingTime = self.console.time()
                                if ping != 999:
                                    client.message(self.getMessage('first_ping_warning'))
                        elif client.maxLevel >= self._max_level: # If admin kick for ci, but allow high ping.
                            if client.var(self, 'highping', 0).value > 0:
                                self.console.verbose('set high ping check %s = %s (%s)', cid, ping, client.var(self, 'highping', 0).value)
                                if self.console.time() - client.var(self, 'highping', 0).value > self._maxPingDuration:
                                    if ping == 999:
                                        client.kick('^7Connection interupted') # kick if ci for too long.
                                        self.console.say('^7%s ^7ping detected as Connection Interrupted (CI)' % client.name)
                                    else:
                                        #client.kick('^7Ping too high %s' % ping)
                                        self.console.say('^7%s ^7ping detected as too high %s' % (client.name, ping))
                            else:
                                self.console.verbose('set ping watch %s = %s', cid, ping)
                                client.setvar(self, 'highping', self.console.time())

    def cmd_ci(self, data, client=None, cmd=None):
        """\
        <player> - Kick a player that has an interrupted connection
        """

        m = self._adminPlugin.parseUserCmd(data)
        if not m:
            client.message('^7Invalid parameters, you must supply a player name')
            return False
        
        sclient = self._adminPlugin.findClientPrompt(m[0], client)
        if sclient:
            for cid,ping in self.console.getPlayerPings().items():
                if cid == sclient.cid:
                    if ping > self._maxCiPing:
                        sclient.kick(self._adminPlugin.getReason('ci'), 'ci', client)
                    else:
                        client.message('^7%s ^7is not CI' % sclient.exactName)
                    break
                            
                            
                        

