from __future__ import unicode_literals

import logging
import re
import shlex
import subprocess

from rbtools.commands import RB_MAIN


# Regular expression for matching argument replacement
_arg_re = re.compile(r'\$(\d+)')


def replace_arguments(cmd, args):
    """Do parameter substitution for the given command.

    The special variable $* is expanded to contain all filenames.
    """
    def arg_sub(m):
        """Replace a positional variable with the appropriate argument."""
        index = int(m.group(1)) - 1

        try:
            return args[index]
        except IndexError:
            return ''

    did_replacement = False

    for part in shlex.split(cmd):
        if part == '$*':
            did_replacement = True

            for arg in args:
                yield arg
        else:
            part, subs = _arg_re.subn(arg_sub, part)

            if subs != 0:
                did_replacement = True

            yield part

    if not did_replacement:
        for arg in args:
            yield arg


def run_alias(alias, args):
    """Run the alias with the given arguments, after expanding parameters.

    Parameter expansion is done by the replace_arguments function.
    """
    use_shell = alias.startswith('!')

    try:
        if use_shell:
            # If we are using the shell, we must provide our program as a
            # string instead of a sequence.
            cmd = subprocess.list2cmdline(replace_arguments(alias[1:], args))
        else:
            cmd = [RB_MAIN] + list(replace_arguments(alias, args))

        return subprocess.call(cmd, shell=use_shell)
    except ValueError as e:
        logging.error('Could not execute alias "%s"; it was malformed: %s',
                      alias, e)

    return 1
