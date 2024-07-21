# Custom syntax, adds new keywords.
import re

from pygments.lexer import Lexer, RegexLexer, do_insertions, bygroups, \
    include, default, this, using, words, line_re
from pygments.token import Punctuation, Whitespace, \
    Text, Comment, Operator, Keyword, Name, String, Number, Generic
from pygments.util import shebang_matches

class BatchLexer(RegexLexer):
    """
    Lexer for the DOS/Windows Batch file format.
    """
    name = 'Batchfile'
    aliases = ['batch', 'bat', 'dosbatch', 'winbatch']
    filenames = ['*.bat', '*.cmd', '*.batch', '*.mktsk']
    mimetypes = ['application/x-dos-batch']
    url = 'https://en.wikipedia.org/wiki/Batch_file'
    version_added = '0.7'

    flags = re.MULTILINE | re.IGNORECASE

    _nl = r'\n\x1a'
    _punct = r'&<>|'
    _ws = r'\t\v\f\r ,;=\xa0'
    _nlws = r'\s\x1a\xa0,;='
    _space = rf'(?:(?:(?:\^[{_nl}])?[{_ws}])+)'
    _keyword_terminator = (rf'(?=(?:\^[{_nl}]?)?[{_ws}+./:[\\\]]|[{_nl}{_punct}(])')
    _token_terminator = rf'(?=\^?[{_ws}]|[{_punct}{_nl}])'
    _start_label = rf'((?:(?<=^[^:])|^[^:]?)[{_ws}]*)(:)'
    _label = rf'(?:(?:[^{_nlws}{_punct}+:^]|\^[{_nl}]?[\w\W])*)'
    _label_compound = rf'(?:(?:[^{_nlws}{_punct}+:^)]|\^[{_nl}]?[^)])*)'
    _number = rf'(?:-?(?:0[0-7]+|0x[\da-f]+|\d+){_token_terminator})'
    _opword = r'(?:equ|geq|gtr|leq|lss|neq)'
    _string = rf'(?:"[^{_nl}"]*(?:"|(?=[{_nl}])))'
    _variable = (r'(?:(?:%(?:\*|(?:~[a-z]*(?:\$[^:]+:)?)?\d|'
                 rf'[^%:{_nl}]+(?::(?:~(?:-?\d+)?(?:,(?:-?\d+)?)?|(?:[^%{_nl}^]|'
                 rf'\^[^%{_nl}])[^={_nl}]*=(?:[^%{_nl}^]|\^[^%{_nl}])*)?)?%))|'
                 rf'(?:\^?![^!:{_nl}]+(?::(?:~(?:-?\d+)?(?:,(?:-?\d+)?)?|(?:'
                 rf'[^!{_nl}^]|\^[^!{_nl}])[^={_nl}]*=(?:[^!{_nl}^]|\^[^!{_nl}])*)?)?\^?!))')
    _core_token = rf'(?:(?:(?:\^[{_nl}]?)?[^"{_nlws}{_punct}])+)'
    _core_token_compound = rf'(?:(?:(?:\^[{_nl}]?)?[^"{_nlws}{_punct})])+)'
    _token = rf'(?:[{_punct}]+|{_core_token})'
    _token_compound = rf'(?:[{_punct}]+|{_core_token_compound})'
    _stoken = (rf'(?:[{_punct}]+|(?:{_string}|{_variable}|{_core_token})+)')

    def _make_begin_state(compound, _core_token=_core_token,
                          _core_token_compound=_core_token_compound,
                          _keyword_terminator=_keyword_terminator,
                          _nl=_nl, _punct=_punct, _string=_string,
                          _space=_space, _start_label=_start_label,
                          _stoken=_stoken, _token_terminator=_token_terminator,
                          _variable=_variable, _ws=_ws):
        rest = '(?:{}|{}|[^"%{}{}{}])*'.format(_string, _variable, _nl, _punct,
                                            ')' if compound else '')
        rest_of_line = rf'(?:(?:[^{_nl}^]|\^[{_nl}]?[\w\W])*)'
        rest_of_line_compound = rf'(?:(?:[^{_nl}^)]|\^[{_nl}]?[^)])*)'
        set_space = rf'((?:(?:\^[{_nl}]?)?[^\S\n])*)'
        suffix = ''
        if compound:
            _keyword_terminator = rf'(?:(?=\))|{_keyword_terminator})'
            _token_terminator = rf'(?:(?=\))|{_token_terminator})'
            suffix = '/compound'
        return [
            ((r'\)', Punctuation, '#pop') if compound else
             (rf'\)((?=\()|{_token_terminator}){rest_of_line}',
              Comment.Single)),
            (rf'(?={_start_label})', Text, f'follow{suffix}'),
            (_space, using(this, state='text')),
            include(f'redirect{suffix}'),
            (rf'[{_nl}]+', Text),
            (r'\(', Punctuation, 'root/compound'),
            (r'@+', Punctuation),
            (rf'((?:for|if|rem)(?:(?=(?:\^[{_nl}]?)?/)|(?:(?!\^)|'
             rf'(?<=m))(?:(?=\()|{_token_terminator})))({_space}?{_core_token_compound if compound else _core_token}?(?:\^[{_nl}]?)?/(?:\^[{_nl}]?)?\?)',
             bygroups(Keyword, using(this, state='text')),
             f'follow{suffix}'),
            (rf'(goto{_keyword_terminator})({rest}(?:\^[{_nl}]?)?/(?:\^[{_nl}]?)?\?{rest})',
             bygroups(Keyword, using(this, state='text')),
             f'follow{suffix}'),
            (words((
                    "dir",          # List directory contents
                    "cd",           # Change directory
                    "mkdir",        # Create a new directory
                    "rmdir",        # Remove a directory
                    "del",          # Delete files
                    "copy",         # Copy files
                    "move",         # Move or rename files
                    "xcopy",        # Copy files and directory trees
                    "robocopy",     # Robust file copy
                    "ren",          # Rename a file or directory
                    "type",         # Display the contents of a file
                    "echo",         # Display messages or turn command echoing on or off
                    "pause",        # Pause the execution of a batch file and display a message
                    "cls",          # Clear the screen
                    "attrib",       # Change file attributes
                    "chkdsk",       # Check a disk and display a status report
                    "diskpart",     # Manage disk partitions
                    "tasklist",     # Display a list of currently running processes
                    "taskkill",     # Kill a running process
                    "netstat",      # Display network statistics
                    "ping",         # Send ICMP echo requests to network hosts
                    "ipconfig",     # Display network configuration
                    "systeminfo",   # Display system information
                    "shutdown",     # Shutdown or restart the computer
                    "sfc",          # System File Checker
                    "fc",           # Compare the contents of two files or sets of files
                    "find",         # Search for a text string in a file or files
                    "findstr",      # Search for strings in files
                    "sort",         # Sort input
                    "more",         # Display output one screen at a time
                    "fc",           # Compare the contents of two files or sets of files
                    "assoc",        # Display or modify file extension associations
                    "ftype",        # Display or modify file types used in file extension associations
                    "color",        # Change the console foreground and background colors
                    "set",          # Display, set, or remove environment variables
                    "path",         # Display or set a search path for executable files
                    "date",         # Display or set the date
                    "time",         # Display or set the system time
                    "ver",          # Display the Windows version
                    "vol",          # Display a disk volume label and serial number
                    "exit",         # Exit the command interpreter
                    "noauto",       # Noauto (custom)
                    "title"
                ),
                   suffix=_keyword_terminator), Keyword, f'follow{suffix}'),
            (rf'(call)({_space}?)(:)',
             bygroups(Keyword, using(this, state='text'), Punctuation),
             f'call{suffix}'),
            (rf'call{_keyword_terminator}', Keyword),
            (rf'(for{_token_terminator}(?!\^))({_space})(/f{_token_terminator})',
             bygroups(Keyword, using(this, state='text'), Keyword),
             ('for/f', 'for')),
            (rf'(for{_token_terminator}(?!\^))({_space})(/l{_token_terminator})',
             bygroups(Keyword, using(this, state='text'), Keyword),
             ('for/l', 'for')),
            (rf'for{_token_terminator}(?!\^)', Keyword, ('for2', 'for')),
            (rf'(goto{_keyword_terminator})({_space}?)(:?)',
             bygroups(Keyword, using(this, state='text'), Punctuation),
             f'label{suffix}'),
            (rf'(if(?:(?=\()|{_token_terminator})(?!\^))({_space}?)((?:/i{_token_terminator})?)({_space}?)((?:not{_token_terminator})?)({_space}?)',
             bygroups(Keyword, using(this, state='text'), Keyword,
                      using(this, state='text'), Keyword,
                      using(this, state='text')), ('(?', 'if')),
            (rf'rem(((?=\()|{_token_terminator}){_space}?{_stoken}?.*|{_keyword_terminator}{rest_of_line_compound if compound else rest_of_line})',
             Comment.Single, f'follow{suffix}'),
            (rf'(set{_keyword_terminator}){set_space}(/a)',
             bygroups(Keyword, using(this, state='text'), Keyword),
             f'arithmetic{suffix}'),
            (r'(set{}){}((?:/p)?){}((?:(?:(?:\^[{}]?)?[^"{}{}^={}]|'
             r'\^[{}]?[^"=])+)?)((?:(?:\^[{}]?)?=)?)'.format(_keyword_terminator, set_space, set_space, _nl, _nl, _punct,
              ')' if compound else '', _nl, _nl),
             bygroups(Keyword, using(this, state='text'), Keyword,
                      using(this, state='text'), using(this, state='variable'),
                      Punctuation),
             f'follow{suffix}'),
            default(f'follow{suffix}')
        ]

    def _make_follow_state(compound, _label=_label,
                           _label_compound=_label_compound, _nl=_nl,
                           _space=_space, _start_label=_start_label,
                           _token=_token, _token_compound=_token_compound,
                           _ws=_ws):
        suffix = '/compound' if compound else ''
        state = []
        if compound:
            state.append((r'(?=\))', Text, '#pop'))
        state += [
            (rf'{_start_label}([{_ws}]*)({_label_compound if compound else _label})(.*)',
             bygroups(Text, Punctuation, Text, Name.Label, Comment.Single)),
            include(f'redirect{suffix}'),
            (rf'(?=[{_nl}])', Text, '#pop'),
            (r'\|\|?|&&?', Punctuation, '#pop'),
            include('text')
        ]
        return state

    def _make_arithmetic_state(compound, _nl=_nl, _punct=_punct,
                               _string=_string, _variable=_variable,
                               _ws=_ws, _nlws=_nlws):
        op = r'=+\-*/!~'
        state = []
        if compound:
            state.append((r'(?=\))', Text, '#pop'))
        state += [
            (r'0[0-7]+', Number.Oct),
            (r'0x[\da-f]+', Number.Hex),
            (r'\d+', Number.Integer),
            (r'[(),]+', Punctuation),
            (rf'([{op}]|%|\^\^)+', Operator),
            (r'({}|{}|(\^[{}]?)?[^(){}%\^"{}{}]|\^[{}]?{})+'.format(_string, _variable, _nl, op, _nlws, _punct, _nlws,
              r'[^)]' if compound else r'[\w\W]'),
             using(this, state='variable')),
            (r'(?=[\x00|&])', Text, '#pop'),
            include('follow')
        ]
        return state

    def _make_call_state(compound, _label=_label,
                         _label_compound=_label_compound):
        state = []
        if compound:
            state.append((r'(?=\))', Text, '#pop'))
        state.append((r'(:?)(%s)' % (_label_compound if compound else _label),
                      bygroups(Punctuation, Name.Label), '#pop'))
        return state

    def _make_label_state(compound, _label=_label,
                          _label_compound=_label_compound, _nl=_nl,
                          _punct=_punct, _string=_string, _variable=_variable):
        state = []
        if compound:
            state.append((r'(?=\))', Text, '#pop'))
        state.append((r'({}?)((?:{}|{}|\^[{}]?{}|[^"%^{}{}{}])*)'.format(_label_compound if compound else _label, _string,
                       _variable, _nl, r'[^)]' if compound else r'[\w\W]', _nl,
                       _punct, r')' if compound else ''),
                      bygroups(Name.Label, Comment.Single), '#pop'))
        return state

    def _make_redirect_state(compound,
                             _core_token_compound=_core_token_compound,
                             _nl=_nl, _punct=_punct, _stoken=_stoken,
                             _string=_string, _space=_space,
                             _variable=_variable, _nlws=_nlws):
        stoken_compound = (rf'(?:[{_punct}]+|(?:{_string}|{_variable}|{_core_token_compound})+)')
        return [
            (rf'((?:(?<=[{_nlws}])\d)?)(>>?&|<&)([{_nlws}]*)(\d)',
             bygroups(Number.Integer, Punctuation, Text, Number.Integer)),
            (rf'((?:(?<=[{_nlws}])(?<!\^[{_nl}])\d)?)(>>?|<)({_space}?{stoken_compound if compound else _stoken})',
             bygroups(Number.Integer, Punctuation, using(this, state='text')))
        ]

    tokens = {
        'root': _make_begin_state(False),
        'follow': _make_follow_state(False),
        'arithmetic': _make_arithmetic_state(False),
        'call': _make_call_state(False),
        'label': _make_label_state(False),
        'redirect': _make_redirect_state(False),
        'root/compound': _make_begin_state(True),
        'follow/compound': _make_follow_state(True),
        'arithmetic/compound': _make_arithmetic_state(True),
        'call/compound': _make_call_state(True),
        'label/compound': _make_label_state(True),
        'redirect/compound': _make_redirect_state(True),
        'variable-or-escape': [
            (_variable, Name.Variable),
            (rf'%%|\^[{_nl}]?(\^!|[\w\W])', String.Escape)
        ],
        'string': [
            (r'"', String.Double, '#pop'),
            (_variable, Name.Variable),
            (r'\^!|%%', String.Escape),
            (rf'[^"%^{_nl}]+|[%^]', String.Double),
            default('#pop')
        ],
        'sqstring': [
            include('variable-or-escape'),
            (r'[^%]+|%', String.Single)
        ],
        'bqstring': [
            include('variable-or-escape'),
            (r'[^%]+|%', String.Backtick)
        ],
        'text': [
            (r'"', String.Double, 'string'),
            include('variable-or-escape'),
            (rf'[^"%^{_nlws}{_punct}\d)]+|.', Text)
        ],
        'variable': [
            (r'"', String.Double, 'string'),
            include('variable-or-escape'),
            (rf'[^"%^{_nl}]+|.', Name.Variable)
        ],
        'for': [
            (rf'({_space})(in)({_space})(\()',
             bygroups(using(this, state='text'), Keyword,
                      using(this, state='text'), Punctuation), '#pop'),
            include('follow')
        ],
        'for2': [
            (r'\)', Punctuation),
            (rf'({_space})(do{_token_terminator})',
             bygroups(using(this, state='text'), Keyword), '#pop'),
            (rf'[{_nl}]+', Text),
            include('follow')
        ],
        'for/f': [
            (rf'(")((?:{_variable}|[^"])*?")([{_nlws}]*)(\))',
             bygroups(String.Double, using(this, state='string'), Text,
                      Punctuation)),
            (r'"', String.Double, ('#pop', 'for2', 'string')),
            (rf"('(?:%%|{_variable}|[\w\W])*?')([{_nlws}]*)(\))",
             bygroups(using(this, state='sqstring'), Text, Punctuation)),
            (rf'(`(?:%%|{_variable}|[\w\W])*?`)([{_nlws}]*)(\))',
             bygroups(using(this, state='bqstring'), Text, Punctuation)),
            include('for2')
        ],
        'for/l': [
            (r'-?\d+', Number.Integer),
            include('for2')
        ],
        'if': [
            (rf'((?:cmdextversion|errorlevel){_token_terminator})({_space})(\d+)',
             bygroups(Keyword, using(this, state='text'),
                      Number.Integer), '#pop'),
            (rf'(defined{_token_terminator})({_space})({_stoken})',
             bygroups(Keyword, using(this, state='text'),
                      using(this, state='variable')), '#pop'),
            (rf'(exist{_token_terminator})({_space}{_stoken})',
             bygroups(Keyword, using(this, state='text')), '#pop'),
            (rf'({_number}{_space})({_opword})({_space}{_number})',
             bygroups(using(this, state='arithmetic'), Operator.Word,
                      using(this, state='arithmetic')), '#pop'),
            (_stoken, using(this, state='text'), ('#pop', 'if2')),
        ],
        'if2': [
            (rf'({_space}?)(==)({_space}?{_stoken})',
             bygroups(using(this, state='text'), Operator,
                      using(this, state='text')), '#pop'),
            (rf'({_space})({_opword})({_space}{_stoken})',
             bygroups(using(this, state='text'), Operator.Word,
                      using(this, state='text')), '#pop')
        ],
        '(?': [
            (_space, using(this, state='text')),
            (r'\(', Punctuation, ('#pop', 'else?', 'root/compound')),
            default('#pop')
        ],
        'else?': [
            (_space, using(this, state='text')),
            (rf'else{_token_terminator}', Keyword, '#pop'),
            default('#pop')
        ]
    }
