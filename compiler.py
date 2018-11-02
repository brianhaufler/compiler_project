import sys
import lexer
import parser
import symbol_table

# Global scope
global_store = 0

class SemanticAction():
    def __init__(self):
        self.semantic_stack = []

        # True if in insertion mode in symbol table. False if in search mode in symbol table
        self.insert = True
        # True if in global environment. False if in local environment
        self.is_global = True
        # True if next variable should be treated as array. False if next variable is a simple variable (not array)
        self.array = False
        # Keeps track of number of global variable declarations
        self.global_memory = 0
        # Keeps track of number of local variable declarations
        self.local_memory = 0

        # self.local_table =
        # self.global_table =

        self.create_num = 0

        self.valid_semantic_actions = [
            1, 2, 6, 4, 7, 13, 9, 3
            #4,7,13 then 9 then 3
            # 55 and 56.
            # 30, 40, 42 and 44.
            # 31, 41, 46 and 48.
            # 43 and 45.
        ]
    def execute(self, semantic_action_num, prev_token):
        if (semantic_action_num in self.valid_semantic_actions):

            # Finds semantic_action method within class
            try:
                function_name = "action_" + str(semantic_action_num)
            except:
                print("Error: Semantic_Action " + str(semantic_action_num) + " is not yet implemented")
            method_to_call = getattr(self, function_name)

            # And then calls it
            method_to_call(prev_token)


    def stack_dump(self):
        print(self.semantic_stack)

    def peek_stack_type(self):
        # Returns None if stack is empty, otherwise the type of the top of the stack
        return None if not self.semantic_stack else self.semantic_stack[-1][0]

    def action_1(self, prev_token):
        self.insert = True

    def action_2(self, prev_token):
        self.insert = False

    def action_3(self, prev_token):
        token_type = self.semantic_stack.pop()[0]
        if (self.array):
            upper_bound = int(self.semantic_stack.pop()[1])
            lower_bound = int(self.semantic_stack.pop()[1])
            memory_size = (upper_bound - lower_bound) + 1

            while(self.peek_stack_type() is "IDENTIFIER"):
                id_token = self.semantic_stack.pop()

                # Create new array entry (id) with name = value of token popped
                id_name = id_token[1]
                id_type = token_type
                id_upper_bound = upper_bound
                id_lower_bound = lower_bound

                if (self.is_global):
                    id_address = self.global_memory
                    # Insert id into global symbol table
                    id_entry = symbol_table.ArrayEntry(id_name, id_address, id_type, id_upper_bound, id_lower_bound)
                    global_table.insert(id_name, id_entry)

                    self.global_memory += memory_size
                else:
                    id_address = self.local_memory
                    # Insert id into local symbol table
                    id_entry = symbol_table.ArrayEntry(id_name, id_address, id_type, id_upper_bound, id_lower_bound)
                    parser_local_table.insert(id_name, id_entry)
                    parser_local_table.dump_table()

                    self.local_memory += memory_size

        # Token type is simple variable
        else:
            while(self.peek_stack_type() is "IDENTIFIER"):
                id_token = self.semantic_stack.pop()

                # Create new variable entry (id) with name = value of token popped
                id_name = id_token[1]
                id_type = token_type

                if (self.is_global):
                    id_address = self.global_memory
                    # Insert id into global symbol table
                    id_entry = symbol_table.VariableEntry(id_name, id_address, id_type)
                    global_table.insert(id_name, id_entry)

                    self.global_memory += 1
                else:
                    id_address = self.local_memory
                    # Insert id into local symbol table
                    id_entry = symbol_table.VariableEntry(id_name, id_address, id_type)
                    parser_local_table.insert(id_name, id_entry)
                    parser_local_table.dump_table()

                    self.local_memory += 1


    def action_4(self, prev_token):
        self.semantic_stack.append(prev_token)

    def action_6(self, prev_token):
        self.array = True

    def action_7(self, prev_token):
        if (prev_token[0] != "INTEGER" and prev_token[0] != "INTCONSTANT"):
            print("Error: Token should be an integer identifier")
        self.semantic_stack.append(prev_token)

    def action_9(self, prev_token):
        token_1 = self.semantic_stack.pop()
        token_2 = self.semantic_stack.pop()
        token_3 = self.semantic_stack.pop()

        # Already added INPUT/OUTPUT IO devices to symbol table, so don't need to re-insert

        # Turn token_3 into a procedure entry and add to global symbol table
        token_3_name = token_3[1]
        procedure_entry = symbol_table.ProcedureEntry(token_3_name, 0, [])
        global_table.insert(token_3_name, procedure_entry)

        self.insert = False

        generate("call","main", 0)
        generate("exit")


    def action_13(self, prev_token):
        if (prev_token[0] != "IDENTIFIER"):
            print("Error: Token should be an identifier")
        self.semantic_stack.append(prev_token)

    def action_55(self, prev_token):
        backpatch(global_store, self.global_memory)
        generate("free", self.globalMemory)
        generate("procend")

    def action_56(self, prev_token):
        generate("procbegin", "main")

        generate("alloc", "_")

class Quadruples:
    def __init__(self):
        self.quad_list = []
        self.next_quad = 0
        dummy_quad = [None, None, None, None]
        self.insert(self.next_quad, dummy_quad)
        self.next_quad += 1


    def get_field(self, quad_index, field):
        return self.quad_list[quad_index][field]

    def set_field(self, quad_index, index, field):
        self.quad_list[quad_index][index] = field

    def get_next_quad(self):
        return self.next_quad

    def increment_next_quad(self):
        self.next_quad += 1

    def get_quad(self, index):
        return str(self.quad_list[index])

    def add_quad(self, quad):
        self.quad_list.insert(self.next_quad, quad)
        self.next_quad += 1

    def print_quads(self):
        quad_label = 1
        print("CODE")
        for quad in self.quad_list:
            print(quad_label + ":  " + quad[0])

            if (quad[1] != None):
                print(" " + quad[1])

            if (quad[2] != None):
                print(", " + quad[2])

            if (quad[3] != None):
                print(", " + quad[3])

            print()
            quad_label += 1

    def backpatch(self, index_value, insert_value):
        return


class Quadruple():
    def __init__(self, op, addr1=None, addr2=None, addr3=None):
        self.op = op
        self.addr1 = addr1
        self.addr2 = addr2
        self.addr3 = addr3


# Responsible for checking the type of two ids
# 0 if id_1 and id_2 are integers
# 1 if id_1 and id_2 are reals (aka float)
# 2 if id_1 is real and id_2 is integer
# 3 if id_1 is integer and id_2 is real
def typecheck(id_1, id_2):
    if type(id_1) is int:
        if type(id_2) is int:
            return 0
        # id_2 is real
        else:
            return 3
    # id_1 is real
    else:
        if type(id_2) is int:
            return 2
        # id_2 is real
        else:
            return 1



def create():
    return


def generate(op, addr1 = None, addr2 = None, addr3 = None):

    return





if __name__ == "__main__":

    # Read in file name from command line
    file = sys.argv[1]

    # Read in file contents
    with open(file) as f:
        program_contents = f.read()
    f.close()

    # Initialization of global table
    global_table = symbol_table.SymbolTable(50)


    # Initialization of semantic actions class
    semantic_actions_class = SemanticAction()

    # Prepare reserved entries
    main_entry = symbol_table.ProcedureEntry('MAIN', 0, [])
    read_entry = symbol_table.ProcedureEntry('READ', 0, [])
    write_entry = symbol_table.ProcedureEntry('WRITE', 0, [])
    input_entry = symbol_table.VariableEntry('INPUT', None, None)
    output_entry = symbol_table.VariableEntry('OUTPUT', None, None)

    # Insert entries in global table
    global_table.insert('MAIN', main_entry)
    global_table.insert('READ', read_entry)
    global_table.insert('WRITE', write_entry)
    global_table.insert('INPUT', input_entry)
    global_table.insert('OUTPUT', output_entry)

    # Initialization of constant table
    constant_table = symbol_table.SymbolTable(50)

    # Run lexer
    token_array = lexer.lexer(program_contents)
    # for token in token_array:
    #     print(token)

    # Run parser
    result = parser.parser(token_array, semantic_actions_class)
    print(result)
