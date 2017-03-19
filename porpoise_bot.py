#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @PorpoiseBot -- Euphoria bot responsible for posting images of porpoises (or visually similar animals).
#                 An image is requested using !porpoise
#
import json
import random
import threading

import re

import io

import datetime

import basebot

DELAY = 600.0


# Main class. Extends BaseBot as botrulez are not provided.
class PorpoiseBot(basebot.BaseBot):

    # Name for logging.
    BOTNAME = 'porpoise_bot'

    # Default nick-name.
    NICKNAME = ':whale2:Bot'

    # Constructor. Not particularly interesting.
    def __init__(self, *args, **kwds):
        basebot.BaseBot.__init__(self, *args, **kwds)
        self.cond = threading.Condition(self.lock)
        self.request_sender = None
        self.requested = False
        self.request = None
        self.request_type = None
        self.start_time = datetime.datetime.utcnow()
        self.should_stop = False

        # Load json config
        json_config = json.load(io.open("./{}_config.json".format(self.BOTNAME), 'rt'))
        self.imgs = json_config['imgs']
        self.wat_imgs = json_config['wat_imgs']
        self.short_help = json_config['short_help']
        self.long_help = json_config['long_help']
        self.pong = json_config['pong']
        # pattern, type, probability
        self.requests = [('^!help\s+@§nickname§\s*$', 'long_help', 1),
                         ('^!help\s*$', 'short_help', 1),
                         ('^!ping(?:\s+@§nickname§)?\s*$', 'ping', 1),
                         ('^!uptime\s+@§nickname§\s*$', 'uptime', 1),
                         ('^!kill\s+@§nickname§\s+(.+?)\s*$', 'kill', 1),
                         ('^!kill\s+@§nickname§\s*$', 'kill_err_no_msg', 1),
                         ('^!porpoise\s*$', 'porpoise', 1),
                         ('^what\s+is\s+the\s+purpose\s+of\s+@§nickname§\s*$', 'porpoise', 1),
                         ('^wat\s*$', 'wat', 0.125)]
        self.response_to = {'short_help':
                                lambda: self.short_help.replace('§nickname§', self.nickname),
                            'long_help':
                                lambda: self.long_help.replace('§nickname§', self.nickname),
                            'ping':
                                lambda: self.pong.replace('§nickname§', self.nickname),
                            'porpoise':
                                lambda: random.choice(self.imgs),
                            'wat':
                                lambda: random.choice(self.wat_imgs),
                            'uptime':
                                lambda: self.uptime(),
                            'kill':
                                lambda: '/me sees themselves out... :(',
                            'kill_err_no_msg':
                                lambda: '@{} If you wish to remove this bot please do so this way: !kill @{} <reason>'.format(self.request.sender.name, self.nickname)}

    # Chat handler. Informs the background thread about new messages.
    def handle_chat(self, msg, meta):
        if msg.sender.name == self.nickname:
            return
        for pattern, request_type, probability in self.requests:
            pattern = pattern.replace('§nickname§', self.nickname)
            match = re.fullmatch(pattern, msg.content, re.IGNORECASE)
            if match is not None:
                if probability > random.random():
                    self.requested = True
                    self.request_type = request_type
                    if request_type == 'kill':
                        io.open('./kill_reason.txt', 'wt')\
                            .write('Time: {:%Y-%m-%d %H:%M}\nRequested by: @{}\nReason: "{}"'
                                   .format(datetime.datetime.now(), msg.sender.name, match.group(1)))
        with self.cond:
            if self.requested:
                self.request = msg
                self.request_sender = msg.id
                self.cond.notifyAll()

    def uptime(self):
        _delta = (datetime.datetime.utcnow() - self.start_time)
        delta = {
            'days': _delta.days,
            'hour': int(_delta.seconds / (60*60) % 24),
            'minute': int(_delta.seconds / 60 % 60),
            'second': _delta.seconds
        }
        return ('/me has been up since {start:%Y-%m-%d %H:%M:%sZ} ' +
                '({delta[days]} days, {delta[hour]:0>2}:{delta[minute]:0>2}:{delta[second]:0>2})')\
            .format(start=self.start_time, delta=delta)

    def waiter(self):
        with self.cond:
            while not self.should_stop:
                self.cond.wait(DELAY)
                if self.requested:
                    self.send_chat(self.response_to[self.request_type](), self.request_sender)
                    if self.request_type == 'kill':
                        self.close()
                        self.should_stop = True
                    self.request_sender = None
                    self.requested = False
                    self.request_type = None

    # Main method. Hooked to spawn the background thread.
    def main(self):
        basebot.spawn_thread(self.waiter)
        basebot.BaseBot.main(self)


# Main function. Calls basebot.run_main()
def main():
    basebot.run_main(PorpoiseBot)

if __name__ == '__main__':
    main()
