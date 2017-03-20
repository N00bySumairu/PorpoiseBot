#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @PorpoiseBot -- Euphoria bot responsible for posting images of porpoises (or visually similar animals).
#                 An image is requested using !porpoise
#
import time
import datetime
import io
import json
import random
import re

import basebot

DELAY = 600.0


# Main class. Extends BaseBot as botrulez are not provided.
class PorpoiseBot(basebot.Bot):
    # Name for logging.
    BOTNAME = 'porpoise_bot'

    # Default nick-name.
    NICKNAME = ':whale2:Bot'

    WAT_RE = re.compile('^wat$', re.IGNORECASE)
    PURPOSE_RE_STR = '^what is the purpose of @{normnick}\??$'

    # Constructor. Not particularly interesting.
    def __init__(self, *rooms, **config):
        basebot.Bot.__init__(self, *rooms, **config)

        # Get images
        self.imgs = config.get('imgs')
        self.wat_imgs = config.get('wat_imgs')
        self.kill_text = config.get('kill_text')
        self.kill_no_reason_text = config.get('kill_no_reason_text')

        self.add_command_handler("porpoise", self.porpoise_handler)
        self.add_chat_handler(self.chat_handler)

    # overwrite as basebot.Bot doesn't format the text to be sent with the contents of meta
    # this is needed for the long_help text
    def handle_command(self, cmdline, meta):
        """
        handle_command(cmdline, meta) -> None

        Handle an arbitrary command.
        See BaseBot.handle_command() for details.
        Overridden to implement the botrulez commands.
        """

        # Convenience function for choosing a reply and sending it.
        def reply(text, alttext=None):
            if text is Ellipsis:
                text = alttext
            if text is not None:
                self.send_chat(text.format(**meta), meta['msgid'])

        # Convenience function for checking if the command is specific and
        # matches myself.
        def nick_matches():
            if len(cmdline) != 2:
                return False
            ms = cmdline[1]
            if not ms.startswith('@'):
                return False
            nn = basebot.normalize_nick(ms[1:])
            if nn == normnick:
                return True
            for i in self.aliases:
                if nn == basebot.normalize_nick(i):
                    return True
            return False

        # Call parent class method.
        basebot.BaseBot.handle_command(self, cmdline, meta)
        # Don't continue if no command or explicitly forbidden.
        if not cmdline or not self.do_stdcommands:
            return
        # Used in nick_matches().
        normnick = basebot.normalize_nick(self.eff_nickname or self.nickname or '')
        # Actual commands.
        if cmdline[0] == '!ping':
            if len(cmdline) == 1:
                reply(self.ping_text)
            elif nick_matches():
                reply(self.spec_ping_text, self.ping_text)
        elif cmdline[0] == '!help':
            if len(cmdline) == 1:
                reply(self.short_help)
            elif nick_matches():
                reply(self.long_help, self.short_help)
        elif cmdline[0] == '!uptime':
            if (self.do_gen_uptime and len(cmdline) == 1 or
                        self.do_uptime and nick_matches()):
                if self.started is None:
                    reply("/me Uptime information is N/A")
                else:
                    reply('/me is up since %s (%s)' % (
                        basebot.format_datetime(self.started),
                        basebot.format_delta(time.time() - self.started)))
        elif cmdline[0] == '!kill' and len(cmdline) > 1 and self.nick_matches(cmdline, normnick):
            if len(cmdline) == 2:
                reply(self.kill_no_reason_text)
            elif len(cmdline) > 2:
                reply(self.kill_text)
                io.open('./kill_reason.txt', 'wt') \
                    .write('Time: {:%Y-%m-%d %H:%M}\nRequested by: @{}\nReason: "{}"'
                           .format(datetime.datetime.now(), meta['sender'], " ".join(cmdline[2:])))
                self.close()

    def porpoise_handler(self, cmdline, meta):
        if len(cmdline) == 1:
            self.send_chat(random.choice(self.imgs), meta['msgid'])

    def chat_handler(self, msg, meta):
        normnick = basebot.normalize_nick(self.eff_nickname or self.nickname or '')

        m = self.WAT_RE.match(msg.content)
        if m and random.random() > 0.125:
            self.send_chat(random.choice(self.wat_imgs), meta['msgid'])
            return
        m = re.compile(self.PURPOSE_RE_STR.format(normnick=normnick), re.IGNORECASE).match(msg.content)
        if m:
            self.send_chat(random.choice(self.imgs), meta['msgid'])
            return

    # Convenience function for checking if the command is specific and
    # matches myself. (taken form basebot.Bot.handle_command)
    def nick_matches(self, cmdline, normnick):
        if len(cmdline) < 2:
            return False
        ms = cmdline[1]
        if not ms.startswith('@'):
            return False
        nn = basebot.normalize_nick(ms[1:])
        if nn == normnick:
            return True
        for i in self.aliases:
            if nn == basebot.normalize_nick(i):
                return True
        return False

    # Main method. Hooked to spawn the background thread.
    def main(self):
        basebot.BaseBot.main(self)


# Main function. Calls basebot.run_main()
def main():
    json_config = json.load(io.open("./{}_config.json".format(PorpoiseBot.BOTNAME), 'rt'))
    basebot.run_main(PorpoiseBot, **json_config)


if __name__ == '__main__':
    main()
