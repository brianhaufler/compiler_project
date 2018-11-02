import string

def lexer(contents):
    data = LexerData(contents)

    # Types of states: None, in_comment, in_number, in_letter, in_punctuation

    # Default state
    # If we go into a different state, we call the corresponding function
    #     valid_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890.,;:<>/*[]+-=()}{\t "
    while ((data.char_index < data.stream_length) and not data.error_message):
        data.read_next_char()
        if (data.next_char == "{"):
            handle_comments(data)
        elif (data.next_char.isalpha()):
            handle_letters(data)
        elif (data.next_char.isdigit()):
            handle_numbers(data)
        elif (data.next_char == "}"):
            data.set_error("Unexpected }")
            break
        # data.valid_punctuation = ".,;:<>/*[]+-=()}{
        elif (data.next_char in data.valid_punctuation):
            handle_punctuation(data)
        elif (data.next_char == "\n"):
            # Helps keep track of overall program line number
            data.line_number += 1
        # data.valid_whitespace = " \t\n"
        elif (data.next_char in data.valid_whitespace):
            pass
        else:
            data.set_error("Invalid character " + data.next_char)
            print(data.next_char)
            print("Invalid char " + str(data.line_number))

    if (data.error_message):
        # for token in data.token_array:
        #     print(token)
        print("Error: " + data.error_message + " on line " + str(data.line_number))
    else:
        data.token_array.append(['ENDOFFILE', None])
        # for token in data.token_array:
        #     print(token)

    return data.token_array



# data.valid_punctuation = ".,;:<>/*[]+-=()}{"
def handle_punctuation(data):
    # Read in the valid character
    data.add_to_token()

    if (data.next_char == "."):
        # Check if doubledot
        if (data.peek(1) == "."):
            data.read_next_char()
            data.add_to_token()
            data.finish_token("DOUBLEDOT")
        else:
            data.finish_token("ENDMARKER")
    # Could convert this into a dictionary lookup later
    elif (data.next_char == ","):
        data.finish_token("COMMA")
    elif (data.next_char == ";"):
        data.finish_token("SEMICOLON")
    elif (data.next_char == "("):
        data.finish_token("LEFTPAREN")
    elif (data.next_char == ")"):
        data.finish_token("RIGHTPAREN")
    elif (data.next_char == "["):
        data.finish_token("LEFTBRACKET")
    elif (data.next_char == "]"):
        data.finish_token("RIGHTBRACKET")
    elif (data.next_char == ":"):
        # Check if "=" appears after (would make it an assignop)
        if (data.peek(1) == "="):
            data.read_next_char()
            data.add_to_token()
            data.finish_token("ASSIGNOP")
        else:
            data.finish_token("COLON")
    # Token is one of "<>/*=+-"
    else:
        if (data.next_char == "="):
            data.finish_token("RELOP", 1)
        elif (data.next_char == "<"):
            # Check if <>
            if (data.peek(1) == ">"):
                data.read_next_char()
                data.add_to_token()
                data.finish_token("RELOP", 2)
            # Or if <=
            elif (data.peek(1) == "="):
                data.read_next_char()
                data.add_to_token()
                data.finish_token("RELOP", 5)
            else:
                data.finish_token("RELOP", 3)
        elif (data.next_char ==">"):
            # Check if >=
            if (data.peek(1) == "="):
                data.read_next_char()
                data.add_to_token()
                data.finish_token("RELOP", 6)
            else:
                data.finish_token("RELOP", 4)
        elif (data.next_char == "/"):
            data.finish_token("MULOP", 2)
        elif (data.next_char == "*"):
            data.finish_token("MULOP", 1)
        # Encountered a + or -
        # Need to check previous character to see if
        # ADDOP or UNARYPLUS/MINUS
        else:
            if (data.is_addop()):
                if (data.next_char == "+"):
                    data.finish_token("ADDOP", 1)
                # Char is -
                else:
                    data.finish_token("ADDOP", 2)
            # Must be UNARYMINUS or UNARYPLUS
            else:
                if (data.next_char == "+"):
                    data.finish_token("UNARYPLUS")
                # Char is -
                else:
                    data.finish_token("UNARYMINUS")
    return


def handle_numbers(data):
    # Set initial state
    period_allowed, exponent_allowed, need_digit = True, True, False

    # Default numtype
    num_type = "INTCONSTANT"

    data.add_to_token()
    while (data.char_stream and not data.error_message):
        data.read_next_char()
        if (data.next_char.isdigit()):
            data.add_to_token()
            need_digit = False
        elif (need_digit):
            data.set_error("Expected a digit")
            return
        elif (data.next_char == "."):
            # Check if token is ..
            if (data.peek(1) == "."):
                data.char_index -= 1
                data.finish_token(num_type)
                return
            elif (period_allowed):
                data.add_to_token()
                period_allowed = False
                need_digit = True
                num_type = "REALCONSTANT"
            else:
                data.set_error("Unexpected .")
                return
        elif (data.next_char.upper() == "E"):
            if (exponent_allowed):
                data.add_to_token()
                exponent_allowed = False
                period_allowed = False

                # Check if next char is a + or -. If so, we add to token and skip checking it
                if (data.peek(1) == "+" or data.peek(1) == "-"):
                    data.read_next_char()
                    data.add_to_token()

                need_digit = True
            else:
                data.set_error("Unexpected E")
                return
        elif (data.next_char in data.valid_punctuation or data.next_char in string.whitespace):
            data.char_index -=1
            data.finish_token(num_type)
            return
        # Token ends, but we looked too far ahead. Decrement index to get back to end of token index
        else:
            data.char_index -= 1
            data.finish_token(num_type)
            return
    data.finish_token(num_type)
    return




def handle_letters(data):
    data.add_to_token()
    while (data.char_stream and not data.error_message):
        data.read_next_char()
        if (data.next_char.isalpha() or data.next_char.isdigit()):
            data.add_to_token()
        else:
            data.char_index -= 1
            data.finish_token()
            return
    data.finish_token()
    return



def handle_comments(data):
    while (data.char_stream):
        data.read_next_char()
        if (data.next_char == "\n"):
            data.line_number += 1
        elif (data.next_char == "}"):
            return
    data.set_error("Error, no closing parenthesis")
    return

class LexerData:
    def __init__(self, contents):
        self.char_stream = contents
        self.stream_length = len(self.char_stream)
        self.next_char = ""
        self.line_number = 1
        self.char_index = 0
        self.current_token = []
        self.token_array = []
        self.error_message = ""
        self.max_length = 30

        self.valid_punctuation = ".,;:<>/*[]+-=(){}"
        self.valid_whitespace = " \t\n"
        self.keywords = ["PROGRAM", "BEGIN", "END", "VAR", "FUNCTION", "PROCEDURE",
                         "RESULT", "INTEGER", "REAL", "ARRAY", "OF", "NOT",
                         "IF", "THEN", "ELSE", "WHILE", "DO"]
        self.mulop_addop_keywords = ["DIV", "MOD", "AND", "OR"]


    def read_next_char(self):
        index = self.char_index
        self.char_index += 1
        self.next_char =  self.char_stream[index]

    # Looks at next num characters in string
    # num is how far ahead of the current char we want to look
    # char_index is already at next 1, so need to back up one
    def peek(self, num):
        # stream_length is 1 larger than the index-able length, so -1
        indexable_length = self.stream_length - 1
        peek_index = self.char_index + num - 1

        if ((peek_index) > indexable_length):
            return None
        return self.char_stream[peek_index]


    def finish_token(self, type = None, value = None):
        token = "".join(self.current_token).upper()

        # Ensure that the token isn't over 30 characters
        if (len(token) > self.max_length):
            self.set_error("Token length too long")
            return

        # Check if token is keyword
        if (token in self.keywords):
            self.token_array.append([token, None])
        elif (token in self.mulop_addop_keywords):
            if (token == "DIV"):
                self.token_array.append(["MULOP", 3])
            elif (token == "MOD"):
                self.token_array.append(["MULOP", 4])
            elif (token == "AND"):
                self.token_array.append(["MULOP", 5])
            # token = OR
            else:
                self.token_array.append(["ADDOP", 3])
        # Value only takes a value if the character is a RELOP, MULOP, ADDOP
        elif (value):
            self.token_array.append([type, value])
        elif (type in ["INTCONSTANT", "REALCONSTANT"]):
            self.token_array.append([type, token])
        elif (type):
            self.token_array.append([type, None])
        else:
            # Default type is IDENTIFIER
            self.token_array.append(["IDENTIFIER", token])
        self.current_token = []


    def add_to_token(self):
        self.current_token.append(self.next_char)

    def set_error(self, message):
        self.error_message = message

    # Check if previous token is RIGHTPAREN, RIGHTBRACKET, IDENTIFIER, INTCONSTANT, or REALCONSTANT
    def is_addop (self):
        if (self.token_array == []):
            return False

        # Tokens in form of [type, value]
        previous_type = self.token_array[-1][0]
        if (previous_type in ["RIGHTPAREN", "RIGHTBRACKET", "IDENTIFIER", "INTCONSTANT", "REALCONSTANT"]):
            return True

        # Otherwise
        return False