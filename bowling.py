#!/usr/bin/env python
"haliphax's crappy bowling game"
__author__ = 'haliphax <todd@roadha.us>'

def echo(text, flush=True):
    "helper function for output"

    from sys import stdout

    stdout.write(text.encode('cp437'))

    if flush:
        stdout.flush()


class Bowling(object):
    "class definition"

    def __init__(self):
        "initialize the pin positions"

        from blessed import Terminal

        # setup
        self.term = Terminal()

        if self.term.kind.startswith('ansi'):
            # monkey-patch move_x

            def term_move_x(xpos):
                return '\x1b[{xpos}G'.format(xpos=xpos + 1)

            self.term.move_x = term_move_x

        # pin positions
        self.pinpos = []
        xloc = 0
        yloc = 0

        self.pinpos.append([xloc + 3, yloc + 9])

        for i in range(2, 3 + 1):
            self.pinpos.append([xloc + 2, yloc + 7 + (i - 2) * 4])

        for i in range(4, 6 + 1):
            self.pinpos.append([xloc + 1, yloc + 5 + (i - 4) * 4])

        for i in range(7, 10 + 1):
            self.pinpos.append([xloc, yloc + 3 + (i - 7) * 4])


    def draw_lane(self):
        "draw the lane"

        xloc = 0
        yloc = 0
        term = self.term
        gutter = term.black_on_white(chr(178).decode('cp437')) # gutter char

        # lane
        for i in range(0, 22 + 1):
            echo(term.move(xloc + i, yloc))
            echo(gutter)
            echo(term.on_yellow(' ' * 17))
            echo(gutter)

        # bowler's deck
        echo(term.move(xloc + 23, yloc))
        echo(term.on_yellow(' ' * 19))

        # lane markers
        echo(term.move(xloc + 5, yloc + 3))
        echo(term.black_on_yellow('^  ^  ^  ^  ^'))
        echo(term.move(xloc + 17, yloc + 9))
        echo(term.black_on_yellow('^'))
        echo(term.move(xloc + 18, yloc + 6))
        echo(term.black_on_yellow('^     ^'))
        echo(term.move(xloc + 19, yloc + 3))
        echo(term.black_on_yellow('^           ^'))


    def draw_pins(self, pins):
        "draw the pins"

        term = self.term

        for i in pins:
            echo(term.move(self.pinpos[i - 1][0], self.pinpos[i - 1][1]))
            echo(term.bold_white_on_yellow(chr(173).decode('cp437')))


    def move_bowler(self, spot):
        "move the bowler"

        term = self.term
        xloc = 23
        yloc = 0
        bowler = term.blue_on_yellow(chr(234).decode('cp437')) # bowler char
        # initial position
        echo(term.move(xloc, yloc + spot + 1) + bowler)
        done = False

        while not done:
            oldspot = spot

            with term.cbreak():
                inp = term.inkey(timeout=0.25)

            if (inp in [u'4', u'a', u'h'] or inp.code in [term.KEY_LEFT,]) \
                    and spot > 0:
                spot -= 1
            elif (inp in [u'6', u'd', u'l'] or inp.code in [term.KEY_RIGHT,]) \
                    and spot < 16:
                spot += 1
            elif inp == u'q' or inp.code in [term.KEY_ESCAPE,]:
                return False
            elif inp in [u' ', u'\n', u'\r']:
                done = True

            if inp and spot != oldspot:
                echo(''.join([term.move(xloc, yloc + 1 + oldspot),
                              term.on_yellow(' '), term.move_x(yloc + 1 + spot),
                              bowler]))

        return spot


    def power_swingbar(self):
        "power swing bar"

        term = self.term
        stages = [
                  (25, term.bold_blue),
                  (50, term.bold_green),
                  (75, term.bold_yellow),
                  (100, term.bold_red),
                 ]

        return self.__hswingbar(1, 20, 35, stages, 'WEAK', 'STRONG', False,
                                True)


    def hook_swingbar(self):
        "hook swing bar"

        term = self.term
        stages = [
                  (10, term.bold_red),
                  (25, term.bold_yellow),
                  (40, term.bold_green),
                  (60, term.bold_blue),
                  (76, term.bold_green),
                  (91, term.bold_yellow),
                  (100, term.bold_red),
                 ]

        return self.__hswingbar(4, 20, 35, stages, 'LEFT', 'RIGHT', True, True)


    def __hswingbar(self, xloc, yloc, width=35, stages=None, ltxt='', rtxt='',
                    wait=False, bounce=False):
        "helper for creating horizontal swing bars"

        if stages is None:
            raise Exception('stages not provided')

        width = 35
        llen = len(ltxt)
        rlen = len(rtxt)
        term = self.term
        bar = chr(178).decode('cp437') # bar char
        widthpct = float(width) / 100
        val = 0
        count = 0
        pct = None
        inp = None

        # draw the frame
        echo(term.move(xloc, yloc))
        echo(term.bold(''.join([
            chr(213), ltxt, (chr(205) * (width / 2 - llen)), chr(209),
            (chr(205) * (width / 2 - rlen)), rtxt, chr(184)
            ]).decode('cp437')))
        echo(term.move(xloc + 1, yloc))
        echo(term.bold(''.join([chr(179), (' ' * width), chr(179)
            ]).decode('cp437')))
        echo(term.move(xloc + 2, yloc))
        echo(term.bold(''.join([chr(212), (chr(205) * (width / 2)), chr(207),
            (chr(205) * (width / 2)), chr(190)]).decode('cp437')))

        # swallow anything in the input buffer
        term.inkey(timeout=0.001)

        # are we waiting for input first?
        if wait:
            with term.cbreak():
                while inp not in [u' ', u'\n', u'\r']:
                    inp = term.inkey(timeout=0.25)

        inp = None
        direction = 1
        echo(term.move(xloc + 1, yloc + 1))

        # bar animation
        while inp not in [u' ', u'\n', u'\r']:
            count += direction

            with term.cbreak():
                inp = term.inkey(timeout=0.001)

            # pct has changed enough to move the bar
            if int(widthpct * count / 10) != val:
                val += direction
                pct = int(float(val) / width * 100)

                # moving right (+1) or left (-1)?
                if direction == 1:
                    # display bar in appropriate color for stage
                    for threshold, func in stages:
                        if pct > threshold:
                            continue

                        echo(func(bar))
                        break
                else:
                    # erase the bar
                    echo(term.move_left + ' ' + term.move_left)

                # hit the edge; bounce or stop?
                if pct >= 100:
                    if bounce:
                        direction = -1
                    else:
                        break
                elif pct == 0:
                    break

        return float(widthpct * count / 10 / width * 100) - 1


    def bowl(self, pins, spot, power, hook):
        "throw the ball"

        import random
        from time import sleep

        random.seed()
        term = self.term
        xloc = 23
        yloc = 0
        hookabs = abs(hook - 50) # absolute value of hook pct
        collided = list() # list of pins to track action for
        lasty = None
        i = 1

        while i <= xloc or len(collided) > 0:
            # apply power and hook
            offset = float(pow(i, 1.3 + hookabs / 50)) / power

            # straight throw adjustment
            if hookabs < 2:
                offset = 0
            # dampen hooks <18
            elif hookabs < 18:
                offset = offset * 0.5
            # dampen hooks <35
            elif hookabs < 35:
                offset = offset * 0.75

            # if it's a left hook, offset is negative
            if hook < 51:
                offset = offset * -1

            intoffset = int(offset)
            myx = xloc - i
            myy = max(0, min(yloc + spot + 1 + intoffset, yloc + 18))
            realy = max(0, min(yloc + spot + 1 + offset, yloc + 18))
            # gutter ball?
            edge = spot + intoffset + 1 <= 0 or spot + intoffset >= 17
            delay = 0.15

            # draw the ball; use a while loop with breaks to avoid indent hell
            while 1:
                if xloc - i < 0:
                    break

                if myx >= 0 and myy >= 0:
                    echo(term.move(myx, myy))

                    if edge:
                        echo(term.black_on_white('o')) # in the gutter
                        break

                    echo(term.black_on_yellow('o')) # in the lane

                # no need to check for collision early (pins are far away, duh)
                if i <= 18:
                    break

                # do we have enough power to knock a pin over?
                if power <= 1:
                    break

                # did we collide with a pin?
                for j in pins:
                    px = self.pinpos[j - 1][0]
                    py = self.pinpos[j - 1][1]

                    # check proximity of ball for pin
                    if px == myx and (py == myy or
                            abs(py - (yloc + spot + 1 + offset)) < 2):
                        # @TODO better calculation!
                        # at what angle are we sending the pin?
                        if realy - lasty == 0:
                            slope = 0.25
                        else:
                            slope = realy - lasty

                        # reverse if the pin is opposite the ball
                        if ((offset >= 0 and realy > lasty)
                                or (offset < 0 and realy < lasty)):
                            slope *= -1

                        # add a bit of randomness to the pin scatter
                        slope *= (1 + (0.01 * random.randint(0, 15)))

                        # increase pin action distance per row
                        slope += 1.5 * (3 - myx)

                        # add to list of pins to track action for
                        collided.append([px, py, slope, power])
                        # remove pin
                        pins = [x for x in pins if x != j]
                        # prevent delay in ball anim frame
                        delay = 0
                        echo(term.move(px, py))

                        # show fall-down animation
                        for k in ['-', '\\', '|', '/', '-']:
                            echo(term.bold_white_on_yellow(k))

                            with term.cbreak():
                                sleep(0.03)

                            echo(term.move_left)

                        # erase the pin
                        echo(term.on_yellow(' '))
                        # reduce ball's remaining power
                        power = power * 0.85
                        # can't collide with more than 1 pin per anim frame
                        break

                break

            if delay > 0:
                with term.cbreak():
                    sleep(delay)

            # remember where we were this anim frame for calculating slope
            lasty = realy

            # replace ball with gutter, lane, or streak
            if xloc - i >= 0:
                echo(term.move(myx, myy))

                if edge:
                    echo(term.black_on_white(chr(178).decode('cp437'))) # gutter
                else:
                    if random.randint(1, 5) <= 1:
                        echo(term.bold_black_on_yellow('|')) # streak
                    else:
                        echo(term.on_yellow(' ')) # lane

            # pin action
            for j in range(len(collided)):
                action = collided.pop()
                pinx = action[0]
                piny = action[1]
                pinslope = action[2]
                pinmom = action[3]
                # decrease momentum
                pinmom *= 0.85
                rpiny = pinslope * (1 + (pinmom / 100)) + piny
                piny = int(rpiny)

                # do we have enough momentum to knock over a pin?
                if pinmom > 10:
                    # see if we've hit another pin
                    for k in pins:
                        opx = self.pinpos[k - 1][0]
                        opy = self.pinpos[k - 1][1]

                        # @TODO don't just check proximity; check path, too
                        if abs(opx - pinx) < 2 and (opy == piny
                                or abs(opy - rpiny) < 2):
                            # hit; add to pin action tracker with random scatter
                            scatter = float(random.randint(85, 115)) / 100

                            if random.randint(1, 5) <= 2:
                                scatter *= -1

                            collided.append([opx, opy, pinslope * scatter,
                                            pinmom])
                            # remove pin from play
                            pins = [x for x in pins if x != k]
                            # skip ball animation delay
                            delay = 0
                            echo(term.move(opx, opy))

                            # show pin knock-over animation
                            for l in ['-', '\\', '|', '/', '-']:
                                echo(term.bold_white_on_yellow(l))

                                with term.cbreak():
                                    sleep(0.03)

                                echo(term.move_left)

                            # clean up
                            echo(term.on_yellow(' '))

                pinx -= 1

                # only continue to track pin if it's in play
                if not (pinx < xloc - 23 or piny <= 0 or piny >= 17):
                    collided.append([pinx, piny, pinslope, pinmom])

            i += 1

        return pins


    def run(self):
        "main method; let's bowl!"

        from time import sleep

        # intro
        term = self.term
        echo(term.clear)
        echo(u'\r\n'.join((
            term.bold(__doc__),
            term.bold('=' + ('-' * (len(__doc__) - 2)) + '='),
            '',
            'Move the bowler with 4, LEFT ARROW, H, 6, RIGHT ARROW, or L.',
            'Press Q/ESC while moving the bowler to quit early.',
            'Press SPACE/ENTER to begin filling up your power bar, '
                'and again to stop.',
            'Press SPACE/ENTER to begin filling up your hook bar, '
                'and again to stop.',
            'The stronger your throw, the less effect hook will have',
            '...but you get more pin action.',
            '',
            'Good luck!',
            '',
            term.bold_green('[Press any key to continue]')
            )))

        with term.cbreak():
            term.inkey()

        echo(term.clear)

        # main loop
        framenum = 1
        frames = []
        framescore = []
        message = None

        def new_frame(pins, frames, framescore):
            pins = range(1, 11)
            frames.append(framescore)
            framescore = list()
            return pins, frames, framescore

        while framenum <= 11:
            pins = range(1, 11)
            spot = 8

            # @TODO better (i.e., actual bowling) scorekeeping
            # show the previous frame's score
            if framenum > 1:
                echo(''.join([term.move(6 + framenum, 22),
                              'Frame {frame}: {score}' \
                              .format(frame=framenum - 1,
                                      score=frames[framenum - 2])]))

            # draw the lane
            echo(''.join([term.move(23, 22), term.normal, term.clear_eol]))
            self.draw_lane()

            if framenum == 11:
                break

            for i in range(0, 3):
                if message:
                    echo(''.join([term.move(21, 22), term.normal,
                                   term.clear_eol, term.move_x(22), message]))
                    message = None

                if len(pins):
                    echo(''.join([term.move(23, 22), term.normal,
                                   term.clear_eol, term.move_x(22),
                                   'Frame {0}, Throw {1}'.format(framenum,
                                                                 i + 1)]))
                    # show the pins
                    self.draw_pins(pins)
                    # move the bowler
                    spot = self.move_bowler(spot)

                    if spot is False:
                        return

                    # power
                    power = self.power_swingbar()
                    # hook
                    hook = self.hook_swingbar()
                    # throw the ball
                    hadpins = len(pins)
                    pins = self.bowl(pins, spot, power, hook)
                    framescore.append(hadpins - len(pins))

                pinsleft = len(pins)

                echo(''.join([term.move(22, 24), term.normal, term.clear_eol]))

                # do they get another throw?
                if framenum == 10:
                    if i == 0:
                        if pinsleft:
                            message = 'Pick up the spare!'
                            continue
                        else:
                            message = 'Bonus throw!'
                            pins, frames, framescore = new_frame(pins, frames,
                                                                 framescore)
                            continue
                    elif i == 1:
                        if pinsleft:
                            if framescore[0] == 10:
                                message = 'Bonus throw!'
                                pins, frames, framescore = new_frame(pins,
                                                                     frames,
                                                                     framescore)
                                continue
                            else:
                                pins = []
                        else:
                            message = 'Bonus throw!'
                            pins, frames, framescore = new_frame(pins, frames,
                                                                 framescore)
                            continue
                    else:
                        pins = []
                        framenum = 11
                elif i == 0:
                    if pinsleft:
                        message = 'Pick up the spare!'
                    else:
                        message = 'Nice strike!'
                elif i == 1:
                    if pinsleft:
                        pins = []
                        message = "You'll get 'em next time!"
                    else:
                        message = 'Nice spare!'

                if not pinsleft:
                    # new frame
                    if framenum < 10:
                        pins, frames, framescore = new_frame(pins, frames,
                                                             framescore)
                    else:
                        pins = []
                    framenum += 1
                    break

        # exit
        self.show_scores(frames)
        with term.cbreak():
            term.inkey(5)

        echo(term.normal)
        echo(term.move(term.height - 1, 0))


# fire it up, holmes
b = Bowling()

with b.term.hidden_cursor():
    b.run()
