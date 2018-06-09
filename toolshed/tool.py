from __future__ import print_function


class Tool(object):
    verbosity = 1


    def write(self, msg, end='\n', verbosity=1):
        """Output text to standard output

        `msg` is only output if `self.verbosity` is greater than or equal
        to `verbosity`.

        Arguments:
            msg {string} -- Message to be output

        Keyword Arguments:
            end {string} -- String ending character to be used rather than
                            a carriage return (default: {'\n'})
            verbosity {integer} -- What verbosity level the tool must
                                   be running at for the message to be
                                   output (default: {1})
        """
        if self.verbosity >= verbosity:
            print(msg, end=end)
