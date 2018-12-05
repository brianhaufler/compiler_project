import symbol_table

def parser(token_array, semantic_actions_class):
    # Goal is at the top of the stack
    data = ParseData(['ENDOFFILE', "<Goal>"])

    # Print variables
    iteration = 1
    dump_msg = ""

    # parser_local_table = symbol_table.SymbolTable(50)

    # Runs until parse stack is empty
    while(data.stack):
        # print(data.stack)
        # print(token_array)
        # print(data.token_history)
        dump_msg += ">>-  " + str(iteration) + "  -<<\n" + "Stack ::==> " + str(data.stack) + "\n"
        symbol = data.stack.pop()
        next_token = token_array[0][0]
        # Is symbol terminal?
        if (symbol in data.terminals_index):
            # Does symbol match?
            if (symbol == next_token):
                # Pop token and add to token history
                data.token_history.append(token_array.pop(0))
                production_msg = "* MATCH *    {consume tokens}"
            # No it doesn't
            else:
                return "Error: Unexpected " + str(next_token)
        # Symbol is semantic action
        elif (isinstance(symbol, int)):
            semantic_actions_class.execute(symbol, data.peek_prev_token())
            production_msg = "# SEMANTIC ACTION #      [" + str(symbol) + "]"

        # Symbol is non-terminal
        else:
            # Symbol isn't also EOF, so we fail
            if (next_token == "ENDOFFILE"):
                return "Error"

            column_index = data.non_terminals_index[symbol]
            row_index = data.terminals_index[next_token]
            production_num = data.parse_table[row_index][column_index]

            # No valid production
            if (production_num == 999):
                return "Error: Unexpected " + str(next_token)
            # Empty production
            elif (production_num < 0):
                production_msg = "@ EPSILON @   [ " + str(production_num) + " ] " + symbol + " ::= @ EPSILON @"
                pass
            # Valid production. Find production and push onto stack
            else:
                production = data.rhs_table[production_num]
                data.stack += production
                production_msg = "$ PUSH $   [ " + str(production_num) + " ] " + symbol + " ::= " + str(production)
        dump_msg += "Popped " + str(symbol) + " with token " + str(next_token) + " -> " + production_msg + "\n"

        if (data.print_parse_trace):
            print(dump_msg)
        dump_msg = ""
        iteration += 1

    # print(semantic_actions_class.actions_tested)

    print("! Accept !")

    semantic_actions_class.quadruples.print_quads()


def dump_stack(parse_data):
    print(parse_data.stack)


class ParseData:
    def __init__(self, initial_stack):
        self.print_parse_trace = True
        self.stack = initial_stack
        self.token_history = []
        # Used to index into parse table
        self.non_terminals_index = {
            "<program>": 0, "<identifier-list>":1, "<declarations>":2, "<sub-declarations>":3, "<compound-statement>":4,
            "<identifier-list-tail>":5, "<declaration-list>":6, "<type>":7, "<declaration-list-tail>":8, "<standard-type>":9,
            "<array-type>":10, "<subprogram-declaration>":11, "<subprogram-head>":12, "<arguments>":13, "<parameter-list>":14,
            "<parameter-list-tail>":15, "<statement-list>":16, "<statement>":17, "<statement-list-tail>":18, "<elementary-statement>":19,
            "<expression>":20, "<else-clause>":21, "<es-tail>":22, "<subscript>":23, "<parameters>":24, "<expression-list>":25,
            "<expression-list-tail>":26, "<simple-expression>":27, "<expression-tail>":28, "<term>":29, "<simple-expression-tail>":30, "<sign>":31,
            "<factor>":32, "<term-tail>":33, "<factor-tail>":34, "<actual-parameters>":35, "<Goal>":36, "<constant>":37
        }
        # Used to index into parse table
        self.terminals_index = {
            "PROGRAM":0, "BEGIN":1, "END":2, "VAR":3, "FUNCTION":4, "PROCEDURE":5, "RESULT":6,
            "INTEGER":7, "REAL":8, "ARRAY":9, "OF":10, "IF":11, "THEN":12, "ELSE":13,
            "WHILE":14, "DO":15, "NOT":16,"IDENTIFIER":17, "INTCONSTANT":18, "REALCONSTANT":19, "RELOP":20,
            "MULOP":21, "ADDOP":22, "ASSIGNOP":23, "COMMA":24, "SEMICOLON":25, "COLON":26, "LEFTPAREN":27,
            "RIGHTPAREN":28, "LEFTBRACKET":29, "RIGHTBRACKET":30, "UNARYMINUS":31, "UNARYPLUS":32, "DOUBLEDOT":33, "ENDMARKER":34, "ENDOFFILE": None
        }
        self.parse_table = [
            [1,  999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999, 65,999],
            [999,999, -6,-16, 25,999,999,999, -9,999,999,999,999,999,999,999, 26, 29,999, 35,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,-28,999,999, 33, 37, 39, 41,999,999,999,-47,999,-51,999,999,-54, 60, 62,999,999],
            [999,999,  5,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999],
            [999,999, -6, 15,999,999,999,999, -9,999,999, 17, 18,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999],
            [999,999, -6, 15,999,999,999,999, -9,999,999, 17, 19,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999],
            [999,999,999,999,999,999,999, 10,999, 12,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999],
            [999,999,999,999,999,999,999, 10,999, 13,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999],
            [999,999,999,999,999,999,999, 11,999,999, 14,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999, 26, 30,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999, 39,999,999,999,999,-47,999,-51,999,999,-54, 60, 62,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999, 32, 37, 39, 41,999,999,999,-47,999,-51,999,999,-54, 60, 62,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999, 26, 31,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999, 39,999,999,999,999,-47,999,-51,999,999,-54, 60, 62,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999, 45,999,999,999,999, 42,999, 48,999, 52,999,999, 58,999,999,999,999,999],
            [999,  2,999,999,999,999,  7,999,  8,999,999,999,999,999, 22,999, 26, 29,999, 34, 45,999,999,999,999, 42,999, 48,999, 52,999,999, 55,999,999,999,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999, 45,999,999,999,999, 42,999, 48,999, 52,999,999, 56,999,999,999,999, 66],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999, 45,999,999,999,999, 42,999, 48,999, 52,999,999, 56,999,999,999,999, 67],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999, 39,999,999,999,999, 46,999,-51,999,999,-54, 60, 62,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999, 39,999,999,999,999,999,999,999,999,999, 53, 60, 62,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999, 39,999,999,999,999,999,999, 50,999,999,-54, 60, 62,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999, 36, 39,999,999,999,999,999,999,999,999,999,999,999,999,999,999],
            [999,999,999,999,999,  3,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999, 39,999,999, 43,999,-47,999,-51,999,999,-54, 60, 62,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,-21,999, 23,999,999, 27,999,999, 33, 37, 39, 41,999,999,999,-47,999,-51,999,999,-54, 60, 62,999,999],
            [999,999,999,999,999, -4,999,999,999,999,999,999,999,-21,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999, 20,999,999,999,999,999,999, 45,999, 37,999, 40, 42,999, 48,999, 52,999,999, 57,999, 59, 61,999,999],
            [999,999,999,999,999, -4,999,999,999,999,999,999,999,999,999,-24,999,999,999,999,999,999,999, 39,999,999,-44,999,-47,999,-51,999,999,-54, 60, 62,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999, 36, 38,999,999,999,999,999,999,999,999,999,999, 60,999,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999, 39,999,999,999,999,-47,999,-51,999,999,-54, 60, 62,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999, 45,999,999,999,999, 42,999, 49,999,999,999, 64,999,999,999,999,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999, 45,999,999,999,999, 42,999, 49,999,999,999, 63,999,999,999,999,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999],
            [999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999,999]
        ]

        # Formatted as a python stack. So each production is ordered backwards
        self.rhs_table = {
            1: [55, "<compound-statement>", 56, "<sub-declarations>", "<declarations>", "SEMICOLON", 9, "RIGHTPAREN", "<identifier-list>", "LEFTPAREN", 13, "IDENTIFIER", "PROGRAM"],
            2: ["<identifier-list-tail>", 13, "IDENTIFIER"],
            3: ["<identifier-list-tail>", 13, "IDENTIFIER", "COMMA"],
            4: [],
            5: [2, "<declaration-list>", 1, "VAR"],
            6: [],
            7: ["<declaration-list-tail>", "SEMICOLON", 3, "<type>", "COLON", "<identifier-list>"],
            8: ["<declaration-list-tail>", "SEMICOLON", 3, "<type>", "COLON", "<identifier-list>"],
            9: [],
            10: ["<standard-type>"],
            11: ["<array-type>"],
            12: [4, "INTEGER"],
            13: [4, "REAL"],
            14: ["<standard-type>", "OF", "RIGHTBRACKET", 7, "INTCONSTANT", "DOUBLEDOT", 7, "INTCONSTANT", "LEFTBRACKET", "ARRAY", 6],
            15: ["<sub-declarations>", "<subprogram-declaration>"],
            16: [],
            17: [11, "<compound-statement>", 5, "<declarations>", "<subprogram-head>", 1],
            18: [16, "SEMICOLON", "<standard-type>", "RESULT", "COLON", "<arguments>", 15, "IDENTIFIER", "FUNCTION"],
            19: ["SEMICOLON", "<arguments>", 17, "IDENTIFIER", "PROCEDURE"],
            20: [20, "RIGHTPAREN", "<parameter-list>", 19, "LEFTPAREN"],
            21: [],
            22: ["<parameter-list-tail>", 21, "<type>", "COLON", "<identifier-list>"],
            23: ["<parameter-list-tail>", 21, "<type>", "COLON", "<identifier-list>", "SEMICOLON"],
            24: [],
            25: ["END", "<statement-list>", "BEGIN"],
            26: ["<statement-list-tail>", "<statement>"],
            27: ["<statement-list-tail>", "<statement>", "SEMICOLON"],
            28: [],
            29: ["<elementary-statement>"],
            30: ["<else-clause>", "<statement>", "THEN", 22, "<expression>", "IF"],
            31: [26, "<statement>", "DO", 25, "<expression>", 24, "WHILE"],
            32: [28, "<statement>", 27, "ELSE"],
            33: [29],
            34: ["<es-tail>", 30, "IDENTIFIER"],
            35: ["<compound-statement>"],
            36: [31, "<expression>", "ASSIGNOP", "<subscript>", 53],
            37: ["<parameters>", 54],
            38: [33, "RIGHTBRACKET", "<expression>", "LEFTBRACKET", 32],
            39: [34],
            40: [51, "RIGHTPAREN", "<expression-list>", "LEFTPAREN", 35],
            41: [36],
            42: ["<expression-list-tail>", 37, "<expression>"],
            43: ["<expression-list-tail>", 37, "<expression>", "COMMA"],
            44: [],
            45: ["<expression-tail>", "<simple-expression>"],
            46: [39, "<simple-expression>", 38, "RELOP"],
            47: [],
            48: ["<simple-expression-tail>", "<term>"],
            49: ["<simple-expression-tail>", 41, "<term>", 40, "<sign>"],
            50: ["<simple-expression-tail>", 43, "<term>", 42, "ADDOP"],
            51: [],
            52: ["<term-tail>", "<factor>"],
            53: ["<term-tail>", 45, "<factor>", 44, "MULOP"],
            54: [],
            55: ["<factor-tail>", 46, "IDENTIFIER"],
            56: [46, "<constant>"],
            57: ["RIGHTPAREN", "<expression>", "LEFTPAREN"],
            58: [47, "<factor>", "NOT"],
            59: ["<actual-parameters>"],
            60: [48, "<subscript>"],
            61: [50, "RIGHTPAREN", "<expression-list>", "LEFTPAREN", 49],
            62: [52],
            63: ["UNARYPLUS"],
            64: ["UNARYMINUS"],
            65: ["ENDMARKER", "<program>"],
            66: ["INTCONSTANT"],
            67: ["REALCONSTANT"]
        }

    def peek_prev_token(self):
        return self.token_history[-1]



