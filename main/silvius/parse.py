# Parser, based on John Aycock's SPARK examples

from spark import GenericParser
from spark import GenericASTBuilder
from errors import GrammaticalError
from ast import AST, printAST


class CoreParser(GenericParser):

#------------------------------------------------------------------------------------------------------

    def __init__(self, start):
        GenericParser.__init__(self, start)

    def typestring(self, token):
        return token.type

    def error(self, token):
        print("")

        raise GrammaticalError("Unexpected token `%s' (word number %d)" %
                               (token, token.wordno))

#------------------------------------------------------------------------------------------------------

    def p_chained_commands(self, args):
        '''
            chained_commands ::= single_command
            chained_commands ::= chain_start
            chained_commands ::= single_command chained_commands

        '''

        if (len(args) == 1):
            return AST('chain', None, [args[0]])
        else:
            args[1].children.insert(0, args[0])
            return args[1]

#--------------------------

    def p_single_command(self, args):
        '''
            single_command ::= letter
            single_command ::= sky_letter
            single_command ::= movement
            single_command ::= character
            single_command ::= editing
            single_command ::= english
            single_command ::= word_sentence
            single_command ::= word_phrase
            single_command ::= window_command
            single_command ::= number
            single_command ::= type_word

        '''
        return args[0]

#--------------------------
    def p_chain_start(self, args):
        '''
            chain_start ::= modifier modifier chain_end
            chain_start ::= modifier chain_end

        '''

        args[0].type = 'modifier'

        return AST('presstogether', None, args)

#--------------------------
    def p_chain_end(self, args):
        '''
            chain_end ::= movement
            chain_end ::= number
            chain_end ::= letter
            chain_end ::= character
            chain_end ::= editing
        '''

        args[0].type = 'modified'

        return args[0]

#--------------------------
    def p_modifier(self, args):

        '''
            modifier ::= control
            modifier ::= alt
            modifier ::= shift
            modifier ::= super
            modifier ::= mod
        '''
        value = {
            'control': 'ctrl',
            'alt': 'alt',
            'shift': 'shift',
            'super': 'super',
            'mod': 'super'
        }

        val = value[args[0].type]
        return AST('modified', [val])


    def p_window_command(self, args):
        '''
            window_command ::= window   direction
        '''
        #        print(args[0])
        #        print(args[1])
        return AST('repeat', [args[1]], [AST('movement', [args[0]])])

    def p_direction(self, args):
        '''
            direction ::=   up
            direction ::=   down
        '''
        if len(args) > 0:
            return args[0]
        else:
            return None

    def p_editing(self, args):
        '''
            editing ::= slap repeat
            editing ::= scratch repeat
            editing ::= backspace repeat
            editing ::= enter repeat
            editing ::= delete repeat
        '''
        value = {
            'slap': 'Return',
            'scratch': 'BackSpace',
            'backspace': 'BackSpace',
            'enter': 'Return',
            'delete' : 'Delete'
        }

        if args[1] != None:
            return AST('repeat', [args[1]],
                       [AST('raw_char', [value[args[0].type]])])
        else:
            return AST('raw_char', [value[args[0].type]])

#--------------------------

    def p_movement(self, args):
        '''
            movement ::= up repeat
            movement ::= down repeat
            movement ::= left repeat
            movement ::= right repeat
            movement ::= pageup
            movement ::= pagedown
            movement ::= home
            movement ::= end
        '''
        value = {
            'up': 'Up',
            'down': 'Down',
            'left': 'Left',
            'right': 'Right',
            'pageup': 'Prior',
            'pagedown': 'Next',
            'home': 'Home',
            'end': 'End'
        }
        if len(args) > 1 and args[1] != None:
            return AST('repeat', [args[1]], [AST('movement', [args[0].type])])
        else:
            return AST('movement', [value[args[0].type]])

        # tmp = []

        # if args[1] != None:
        #     print("repeat")
        #     print(args)
        #     print(args[1].type)
        #     print(args[1].meta[0])

        #     for i in range(0,args[1].meta[0]):
        #         tmp.append(AST('movement', [value[args[0].type]]))

        #     return tmp
        # else:
        #    return append(AST('movement', [value[args[0].type]]))


#--------------------------

    def p_repeat(self, args):
        '''
            repeat ::=
            repeat ::= number
        '''
        if len(args) > 0:
            return args[0]
        else:
            return None

    def p_number(self, args):
        '''
            number ::= zero
            number ::= one
            number ::= two
            number ::= three
            number ::= four
            number ::= five
            number ::= six
            number ::= seven
            number ::= eight
            number ::= nine
        '''
        value = {
            'zero': 0,
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
            'six': 6,
            'seven': 7,
            'eight': 8,
            'nine': 9
        }
        #        AST('char', [ args[0].type[0] ])
        #        print("type:")
        #        print(args[0].type)
        #        print(value[args[0].type])

        return AST('num', [value[args[0].type]])

#--------------------------

    def p_sky_letter(self, args):
        '''
            sky_letter ::= sky letter
        '''
        #        print("p_sky_letter")
        #        print(args)
        ast = args[1]
        ast.meta[0] = ast.meta[0].upper()
        return ast

#--------------------------

    def p_letter(self, args):
        '''
            letter ::= alpha
            letter ::= bravo
            letter ::= charlie
            letter ::= delta
            letter ::= echo
            letter ::= foxtrot
            letter ::= golf
            letter ::= hotel
            letter ::= india
            letter ::= juliet
            letter ::= kilo
            letter ::= lima
            letter ::= mike
            letter ::= november
            letter ::= oscar
            letter ::= papa
            letter ::= quebec
            letter ::= romeo
            letter ::= sierra
            letter ::= tango
            letter ::= uniform
            letter ::= victor
            letter ::= whiskey
            letter ::= whisky
            letter ::= x-ray
            letter ::= expert
            letter ::= yankee
            letter ::= zulu
        '''

        #if (args[0].type == 'expert'): args[0].type = 'x'
        return AST('char', [args[0].type[0]])

#--------------------------

    def p_character(self, args):
        '''
            character ::= escape
            character ::= act
            character ::= colon
            character ::= singlequote
            character ::= doublequote
            character ::= equal
            character ::= space
            character ::= tab
            character ::= bang
            character ::= hash
            character ::= dollar
            character ::= percent
            character ::= carrot
            character ::= ampersand
            character ::= star
            character ::= late
            character ::= rate
            character ::= minus
            character ::= underscore
            character ::= plus
            character ::= backslash
            character ::= dot
            character ::= slash
            character ::= question
            character ::= along
            character ::= comma
            character ::= las
            character ::= bas

        '''
        value = {
            'escape': 'Escape',
            'act': 'Escape',
            'colon': 'colon',
            'singlequote': 'apostrophe',
            'doublequote': 'quotedbl',
            'equal': 'equal',
            'space': 'space',
            'tab': 'Tab',
            'bang': 'exclam',
            'hash': 'numbersign',
            'dollar': 'dollar',
            'percent': 'percent',
            'carrot': 'caret',
            'ampersand': 'ampersand',
            'star': 'asterisk',
            'late': 'parenleft',
            'rate': 'parenright',
            'minus': 'minus',
            'underscore': 'underscore',
            'plus': 'plus',
            'backslash': 'backslash',
            'dot': 'period',
            'slash': 'slash',
            'question': 'question',
            'along': 'alt',
            'comma': 'comma',
            'las' : 'bracketleft',
            'bas' : 'bracketright'
        }
        return AST('raw_char', [value[args[0].type]])

#--------------------------
    def p_type_word(self, args):

        '''
            type_word ::= python
            type_word ::= sudo
            type_word ::= top
            type_word ::= for

            type_word ::= python
            type_word ::= define
            type_word ::= if
            type_word ::= for
            type_word ::= in
        '''

        # print("Word: %s" % args[0].type)

        return AST('type_word', [args[0].type])

#--------------------------
#--------------------------

#
#    def p_english(self, args):
#        '''
#            english ::= word ANY
#        '''
#        return AST('sequence', [ args[1].extra ])
#
#    def p_word_sentence(self, args):
#        '''
#            word_sentence ::= sentence word_repeat
#        '''
#        if(len(args[1].children) > 0):
#            args[1].children[0].meta = args[1].children[0].meta.capitalize()
#        return args[1]
#
#    def p_word_phrase(self, args):
#        '''
#            word_phrase ::= phrase word_repeat
#        '''
#        return args[1]
#
#    def p_word_repeat(self, args):
#        '''
#            word_repeat ::= ANY
#            word_repeat ::= ANY word_repeat
#        '''
#        if(len(args) == 1):
#            return AST('word_sequence', None,
#                [ AST('null', args[0].extra) ])
#        else:
#            args[1].children.insert(0, AST('null', args[0].extra))
#            return args[1]


class SingleInputParser(CoreParser):
    def __init__(self):
        CoreParser.__init__(self, 'single_input')

    def p_single_input(self, args):
        '''
            single_input ::= END
            single_input ::= chained_commands END
        '''
        if len(args) > 0:
            return args[0]
        else:
            return AST('')


def parse(tokens):
    parser = SingleInputParser()
    return parser.parse(tokens)
