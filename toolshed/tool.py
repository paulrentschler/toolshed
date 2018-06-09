from __future__ import print_function

from argparse import ArgumentParser

import os
import sys


class CommandError(Exception):
    """Indicates a problem while executing a `Command`

    If this exception is raised during the execution of a management
    command, it will be caught and turned into a nicely-printed error
    message to the appropriate output stream (i.e., stderr); as a
    result, raising this exception (with a sensible description of the
    error) is the preferred way to indicate that something has gone
    wrong in the execution of a command.
    """
    pass




class BaseCommand(object):
    """Base functionality for executing the tools from the command line

    Much of this functionality is borrowed from Django's Management Commands.

    The flow is as follows:

    1. The tool loads the command class and calls its `run_from_argv()`
       method.

    2. The `run_from_argv()` method calls `create_parser()` to get
       an `ArgumentParser` for the arguments, parses them, performs
       any environment changes requested by options like
       `pythonpath`, and then calls the `execute()` method,
       passing the parsed arguments.

    3. The `execute()` method attempts to carry out the command by
       calling the `handle()` method with the parsed arguments; any
       output produced by `handle()` will be printed to standard
       output.

    4. If `handle()` or `execute()` raised any exception (e.g.
       `CommandError`), `run_from_argv()` will  instead print an error
       message to `stderr`.

    Thus, the `handle()` method is typically the starting point for
    subclasses; many built-in commands and command types either place
    all of their logic in `handle()`, or perform some additional
    parsing work in `handle()` and then delegate from it to more
    specialized methods as needed.
    """
    # Metadata about this command.
    help = ''


    def __init__(self, stdout=None, stderr=None):
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr


    def add_arguments(self, parser):
        """Entry point for subclassed commands to add custom arguments"""
        pass


    def create_parser(self, prog_name, subcommand):
        """Create and return the `ArgumentParser` to parse arguments"""
        parser = ArgumentParser(
            prog='%s %s' % (os.path.basename(prog_name), subcommand),
            description=self.help or None,
        )
        parser.add_argument(
            '-d', '--dryrun',
            action='store_true',
            default=False,
            dest='dryrun',
            help='Prevents the command from making any permanent changes',
        )
        parser.add_argument(
            '--pythonpath',
            help='A directory to add to the Python path, '
                 'e.g. "/home/djangoprojects/myproject"',
        )
        parser.add_argument(
            '--traceback',
            action='store_true',
            help='Raise on CommandError exceptions',
        )
        parser.add_argument(
            '-v', '--verbosity',
            action='store',
            choices=[0, 1, 2, 3],
            default=1,
            dest='verbosity',
            help='Verbosity level; 0=minimal output, 1=normal output, '
                 '2=verbose output, 3=very verbose output',
            type=int,
        )
        self.add_arguments(parser)
        return parser


    def error(self, msg, end=None, verbosity=1):
        """Output a message to the standard error stream

        Similar to `write` but the message is directed to the terminal's
        strerr stream so that it understands this is an error message
        and can be handled differently.

        Arguments:
            msg {string} -- The message to output to the standard error stream

        Keyword Arguments:
            end {string} -- Override the standard string ending character
                            ('\n') to use something else. Specifying a
                            blank string ('') will keep the next call to
                            `self._error` on the same line in the terminal.
                            (default: {None})
            verbosity {integer} -- What verbosity level the command must be
                                   running at for the message to be output
                                   (default: {1})
        """
        if self.verbosity >= verbosity:
            self.stderr.write(msg, ending=end)
            self.stderr.flush()


    def execute(self, *args, **options):
        """Try to execute this command"""
        if sys.version_info < (3, 3):
            raise CommandError('This script is only for use with '
                               'Python 3.3 or later')

        if options.get('stdout'):
            self.stdout = options['stdout']
        if options.get('stderr'):
            self.stderr = options['stderr']
        self.dryrun = options['dryrun']
        self.verbosity = options['verbosity']

        output = self.handle(*args, **options)
        if output:
            self.stdout.write(output)
        return output


    def handle(self, *args, **options):
        """
        The actual logic of the command. Subclasses must implement
        this method.
        """
        raise NotImplementedError(
            'Subclasses of Command must provide a handle() method'
        )


    def print_help(self, prog_name, subcommand):
        """Print the help message for this command"""
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help()


    def run_from_argv(self, argv):
        """Set up any environment changes, then run the command

        If the command raises a `CommandError`, intercept it and print
        it sensibly to stderr. If the `--traceback` option is present
        or the raised `Exception` is not `CommandError`, raise it.
        """
        self._called_from_command_line = True
        parser = self.create_parser(argv[0], argv[1])
        options = parser.parse_args(argv[2:])
        cmd_options = vars(options)

        # Move positional args out of options to mimic legacy optparse
        args = cmd_options.pop('args', ())
        if options.pythonpath:
            sys.path.insert(0, options.pythonpath)
        try:
            self.execute(*args, **cmd_options)
        except Exception as e:
            if options.traceback or not isinstance(e, CommandError):
                raise
            self.stderr.write('%s: %s' % (e.__class__.__name__, e))
            sys.exit(1)


    def write(self, msg, end=None, verbosity=1):
        """Output a message to the standard output stream

        Similar to `error` but the message is directed to the terminal's
        strout stream so that it understands this is a normal output.

        Arguments:
            msg {string} -- The message to output to the standard output stream

        Keyword Arguments:
            end {string} -- Override the standard string ending character
                            ('\n') to use something else. Specifying a
                            blank string ('') will keep the next call to
                            `self._write` on the same line in the terminal.
                            (default: {None})
            verbosity {integer} -- What verbosity level the command must
                                   be running at for the message to be
                                   output (default: {1})
        """
        if self.verbosity >= verbosity:
            self.stdout.write(msg, ending=end)
            self.stdout.flush()




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
