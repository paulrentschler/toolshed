from __future__ import print_function


class Tool(object):
    verbosity = 1


    def write(self, msg, verbosity=1, end='\n'):
        """Output text to standard output

        `msg` is only output if `self.verbosity` is greater than or equal
        to `verbosity`.

        Arguments:
            msg {string} -- Message to be output

        Keyword Arguments:
            verbosity {number} -- Verbosity level necessary to output the
                                  message (default: {1})
            end {string} -- String ending character to be used rather than
                            a carriage return (default: {'\n'})
        """
        if self.verbosity >= verbosity:
            print(msg, end=end)
