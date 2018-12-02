import symbol_table
import quadruple
from enum import Enum

class SemanticAction():
    def __init__(self):
        self.semantic_stack = []

        # True if in insertion mode in symbol table. False if in search mode in symbol table
        self.is_insert = True
        # True if in global environment. False if in local environment
        self.is_global = True
        # True if next variable should be treated as array. False if next variable is a simple variable (not array)
        self.is_array = False
        # Keeps track of number of global variable declarations
        self.global_memory = 0
        # Keeps track of number of local variable declarations
        self.local_memory = 0

        # self.local_table =
        self.temp_var_num = 0

        self.local_table = symbol_table.SymbolTable(50)
        self.global_table = symbol_table.SymbolTable(50)

        # Keeps track of alloc statement
        self.global_store = 0
        self.local_store = 0

        self.quadruples = quadruple.Quadruples()

        self.create_num = 0

        # Initialize current function as None
        self.current_function = None

        # Initialization of constant table
        self.constant_table = symbol_table.SymbolTable(50)

        # Parameter count stack, where each element is the number of
        # parameters of a function or procedures
        self.param_count = []

        # Parameter info stack, where each element is a list of symbol
        # table entries representing the parameter info for a function
        # or procedure
        self.param_stack = []

        # Keep track of the current index into the list on the
        # top of param_stack
        self.next_param = 0

        self.valid_semantic_actions = [
            1, 2, 6, 4, 7, 13, 9, 3, 55, 56,
            # 30, 40, 42, 44, 31, 41, 46, 48
            # 31, 41, 46, 48
            30, 40, 42, 44, 31, 41, 46, 43, 45, 48,
            32, 33, 34, 53, 54, 38, 39, 47, 22, 24, 25, 26, 27, 28, 29,
            5, 11,
            15, 16, 17,
            19, 20, 21,
            35, 51, 54, 36, 37,
            49, 50, 52,
            "51READ", "51WRITE"
        ]
        self.actions_tested = []

    def get_temp_var_num(self):
        temp = self.temp_var_num
        self.temp_var_num += 1
        return temp

    def get_opcode(self, operator):
        if (operator[0] == "MULOP"):
            if (operator[1] == 1):
                return "mul"
            elif (operator[1] == 2):
                return "div"
            elif (operator[1] == 3):
                return "DIV"
            elif (operator[1] == 4):
                return "MOD"
            elif (operator[1] == 5):
                return "AND"
            else:
                raise Exception("Not 1-5 MULOP value in get_opcode")
        elif (operator[0] == "ADDOP"):
            if (operator[1] == 1):
                return "add"
            elif (operator[1] == 2):
                return "sub"
            elif (operator[1] == 3):
                return "OR"
            else:
                Exception("Not 1-3 ADDOP value in get_opcode")
        elif (operator[0] == "RELOP"):
            if (operator[1] == 1):
                return "beq" # =
            elif (operator[1] == 2):
                return "bne" # <>
            elif (operator[1] == 3):
                return "blt" # <
            elif (operator[1] == 4):
                return "bgt" # > branch greater than
            elif (operator[1] == 5):
                return "ble" # <=
            elif (operator[1] == 6):
                return "bge" # >=
            else:
                Exception("Not 1-6 RELOP values in get_opcode")
        else:
            raise Exception("Error: Not MULOP, ADDOP, or RELOP in get_opcode")


    def execute(self, semantic_action_num, prev_token):
        if (semantic_action_num in self.valid_semantic_actions):
            # For debugging purposes
            self.actions_tested.append(semantic_action_num)
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

    def peek_stack(self):
        return None if not self.semantic_stack else self.semantic_stack[-1]


    ## --------------------
    ## HELPER FUNCTIONS
    ## --------------------

    # Responsible for checking the type of two ids
    # Takes in two symbol table entries?
    # 0 if id_1 and id_2 are integers
    # 1 if id_1 and id_2 are reals (aka float)
    # 2 if id_1 is real and id_2 is integer
    # 3 if id_1 is integer and id_2 is real
    # Written "INTEGER" or "REAL" is a quick fix.
    # Might need to change it so it's originally inserted as int or float in symbol table
    def typecheck(self, id_1, id_2):
        if id_1.type is int or id_1.type == "INTEGER":
            if id_2.type is int or id_2.type == "INTEGER":
                return 0
            # id_2 is real
            elif id_2.type is float or id_2.type == "REAL":
                return 3
            else:
                raise Exception("Neither int nor real in typecheck")
        # id_1 is real
        elif id_1.type is float or id_1.type == "REAL":
            if id_2.type is int or id_2.type == "INTEGER":
                return 2
            # id_2 is real
            elif id_2.type is float or id_2.type == "REAL":
                return 1
            else:
                raise Exception("Neither int nor real in typecheck")
        else:
            raise Exception("Neither int nor real in typecheck")


    # Inserts insert_value in second field of quadruple at index of index_value in quadruples
    def backpatch(self, index_value, insert_value):
        self.quadruples.set_field(index_value, 1, str(insert_value))

    def backpatch_list(self, index_list, insert_value):
        for num in index_list:
            if (self.quadruples.get_quad(num) == "goto"):
                # set the second field of the quad at num to insert_value
                self.quadruples.set_field(num, 1, str(insert_value))
            else:
                self.quadruples.set_field(num, 3, str(insert_value))



    # Responsible for inserting a new variable entry into the appropriate symbol table
    # and associating it with a valid memory address.
    # Returns a variable entry
    def create(self, name, type):
        new_name = "temp" + str(self.get_temp_var_num())
        if (self.is_global):
            # Store address as negative to distinguish between temporary variables
            address = -1 * self.global_memory
            self.global_memory += 1
            new_entry = symbol_table.VariableEntry(new_name, address, type, self.is_global)
            self.global_table.insert(new_name, new_entry)
        # Local
        else:
            address = -1 * self.local_memory
            self.local_memory += 1
            new_entry = symbol_table.VariableEntry(new_name, address, type, self.is_global)
            self.local_table.insert(new_name, new_entry)
        return new_entry


    def generate(self, op, ste1=None, ste2=None, ste3=None):
        # print(str(op) + str(ste1) + str(ste2) + str(ste3))
        # If the parameter was empty or it was type of "string" then
        # we can't look up the address, so we use the original parameter value.
        # If the parameter isn't None or isn't a string, we change the parameter value to the address
        if (ste1 != None and isinstance(ste1, symbol_table.SymbolTableEntry)):
        # if (ste1 != None and not isinstance(ste1, str) and not isinstance(ste1, int)):
            ste1 = self.get_ste_address(ste1)

        if (ste2 != None and isinstance(ste2, symbol_table.SymbolTableEntry)):
            ste2 = self.get_ste_address(ste2)

        if (ste3 != None and isinstance(ste3, symbol_table.SymbolTableEntry)):
            ste3 = self.get_ste_address(ste3)

        new_quad = quadruple.Quadruple(op, ste1, ste2, ste3)
        self.quadruples.add_quad(new_quad)


    def get_ste_address(self, ste):
        # array entries and variable entries are assigned addresses when initialized
        if (ste.isVariable or ste.isArray):
            # Abs removes the negative from the ste address
            return self.get_ste_prefix(ste) + str(abs(ste.address))
        # Ste is constant entry, which does not have an address.
        # A temporary variable must be created to store it
        else:
            temp = self.create("temp", ste.type)

            # Move constant into the temporary variable
            self.generate("move", ste.name, temp)

            # Abs removes the negative from the ste address
            return self.get_ste_prefix(temp) + str(abs(temp.address))


    # Finds prefix for symbol table entries
    # Used in get_ste_addresss
    def get_ste_prefix(self, ste):
        if (ste.is_global):
            return "_"
        # local
        else:
            entry = self.local_table.lookup(ste.name)
            if (entry is None):
                return "_"
            else:
                if (ste.isParameter):
                    return "^%"
                # ste is not a parameter
                else:
                    return "%"

    # Returns the proper prefix for a parameter
    # To be used when generating code with the opcode "param"
    # "param" is a SymbolTableEntry
    def get_param_prefix(self, param):
        if (self.is_global):
            return "@_"
        # local
        else:
            if (param.isParameter):
                return "%"
            else:
                return "@%"

    ## --------------------
    ## SEMANTIC ACTIONS
    ## --------------------

    def action_1(self, prev_token):
        self.is_insert = True

    def action_2(self, prev_token):
        self.is_insert = False

    def action_3(self, prev_token):
        token_type = self.semantic_stack.pop()[0]
        if (self.is_array):
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
                    id_entry = symbol_table.ArrayEntry(id_name, id_address, id_type, id_upper_bound, id_lower_bound, self.is_global)
                    self.global_table.insert(id_name, id_entry)

                    self.global_memory += memory_size
                else:
                    id_address = self.local_memory
                    # Insert id into local symbol table
                    id_entry = symbol_table.ArrayEntry(id_name, id_address, id_type, id_upper_bound, id_lower_bound, self.is_global)
                    self.local_table.insert(id_name, id_entry)
                    self.local_table.dump_table()

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
                    id_entry = symbol_table.VariableEntry(id_name, id_address, id_type, self.is_global)
                    self.global_table.insert(id_name, id_entry)

                    self.global_memory += 1
                else:
                    id_address = self.local_memory
                    # Insert id into local symbol table
                    id_entry = symbol_table.VariableEntry(id_name, id_address, id_type, self.is_global)
                    self.local_table.insert(id_name, id_entry)
                    self.local_table.dump_table()

                    self.local_memory += 1

        self.is_array = False


    def action_4(self, prev_token):
        self.semantic_stack.append(prev_token)

    def action_5(self, prev_token):
        self.is_insert = False
        id = self.semantic_stack.pop()
        self.generate("PROCBEGIN", id.name)
        self.local_store = self.quadruples.get_next_quad()
        self.generate("alloc", "_")

    def action_6(self, prev_token):
        self.is_array = True

    def action_7(self, prev_token):
        if (prev_token[0] != "INTEGER" and prev_token[0] != "INTCONSTANT"):
            raise Exception("Error: Token should be an integer identifier")
        self.semantic_stack.append(prev_token)

    def action_9(self, prev_token):
        token_1 = self.semantic_stack.pop()
        token_2 = self.semantic_stack.pop()
        token_3 = self.semantic_stack.pop()

        # Already added INPUT/OUTPUT IO devices to symbol table, so don't need to re-insert

        # Turn token_3 into a procedure entry and add to global symbol table
        token_3_name = token_3[1]
        procedure_entry = symbol_table.ProcedureEntry(token_3_name, 0, [], True)
        self.global_table.insert(token_3_name, procedure_entry)
        # self.global_memory += 1

        self.is_insert = False

        self.generate("call","main", 0)
        self.generate("exit")

    def action_11(self, prev_token):
        self.is_global = True
        # Delete local symbol table
        self.local_table = self.local_table = symbol_table.SymbolTable(50)
        self.current_function = None
        self.backpatch(self.local_store, self.local_memory)
        self.generate("free", self.local_memory)
        self.generate("PROCEND")


    def action_13(self, prev_token):
        if (prev_token[0] != "IDENTIFIER"):
            raise Exception("Error: Token should be an identifier")
        self.semantic_stack.append(prev_token)

    def action_15(self, prev_token):
        # Create variable to store result of function
        result = self.create(prev_token[1] + "_RESULT", int)

        # Set result tag of the variable entry class
        result.isFunctionResult = True

        # Create new function entry with name from the token
        # from the parser, and the result variable just created
        id = symbol_table.FunctionEntry(prev_token[1], result)

        self.global_table.insert(id)
        self.is_global = False
        self.local_memory = 0
        self.current_function = id
        self.semantic_stack.append(id)

    # This action sets the type of the function and its result
    def action_16(self, prev_token):
        # type is a token
        type = self.semantic_stack.pop()
        id = self.peek_stack()
        id.type = type[0]

        # Potential problem here
        # Sets the type of the result variable of id
        id.result.type = id.type
        self.current_function = id

    # Create a new procedure entry with the name of the token
    # from the parser
    def action_17(self, prev_token):
        id = symbol_table.ProcedureEntry(prev_token[1])
        self.global_table.insert(id)
        self.is_global = False
        self.local_memory = 0
        self.current_function = id
        self.semantic_stack.append(id)

    # Resets param_count
    def action_19(self, prev_token):
        self.param_count = []
        self.param_count.append(0)

    def action_20(self, prev_token):
        id = self.peek_stack()
        num_params = self.param_count.pop()
        # id is a function entry or a procedure entry
        id.number_of_parameters = num_params

    def action_21(self, prev_token):
        type = self.semantic_stack.pop()

        # if array then pop the upper and lower bounds
        upper_bound = -1
        lower_bound = -1
        if (self.is_array):
            upper_bound = int(self.semantic_stack.pop())
            lower_bound = int(self.semantic_stack.pop())

        # Tokens on the stack, which represent parameters,
        # must be added from the bottom-most id to the top-most
        parameters = []

        # As the ids are popped off the stack, push them onto
        # the new stack to reverse the order
        while (self.peek_stack()[0] == "IDENTIFIER"):
            parameters.append(self.semantic_stack.pop())

        # While parameters isn't empty
        while (parameters):
            param = parameters.pop()
            if (self.is_array):
                var = symbol_table.ArrayEntry(param[1], self.local_memory, type[0], upper_bound, lower_bound)
            else:
                var = symbol_table.VariableEntry(param[1], self.local_memory, type)
            var.isParameter = True
            self.local_table.insert(var)
            # Current function is either procedure or function entry
            self.current_function.parameter_info.append(var)
            self.local_memory += 1
            # Increment top of param_count
            self.param_count.append(self.param_count.pop() + 1)

        self.is_array = False



        return


    def action_22(self, prev_token):
        print(prev_token)
        etype = self.semantic_stack.pop()
        print(etype)
        if (etype != EType.RELATIONAL):
            raise Exception("Etype mismatch error in action_22")
        efalse = self.semantic_stack.pop()
        etrue = self.semantic_stack.pop()
        self.backpatch_list(etrue, self.quadruples.get_next_quad())
        self.semantic_stack.append(etrue)
        self.semantic_stack.append(efalse)

    def action_24(self, prev_token):
        begin_loop = self.quadruples.get_next_quad()
        self.semantic_stack.append(begin_loop)

    def action_25(self, prev_token):
        etype = self.semantic_stack.pop()
        if (etype != EType.RELATIONAL):
            raise Exception("Etype mismatch error in action_25")

        efalse = self.semantic_stack.pop()
        etrue = self.semantic_stack.pop()
        self.backpatch_list(etrue, self.quadruples.get_next_quad())
        self.semantic_stack.append(etrue)
        self.semantic_stack.append(efalse)

    def action_26(self, prev_token):
        efalse = self.semantic_stack.pop()
        etrue = self.semantic_stack.pop()

        # Begin loop pushed onto stack in action_24
        begin_loop = self.semantic_stack.pop()
        self.generate("goto", begin_loop)
        self.backpatch_list(efalse, self.quadruples.get_next_quad())

    def action_27(self, prev_token):
        skip_else = make_list(self.quadruples.get_next_quad())
        self.generate("goto", "_")
        efalse = self.semantic_stack.pop()
        etrue = self.semantic_stack.pop()
        self.backpatch_list(efalse, self.quadruples.get_next_quad())
        self.semantic_stack.append(skip_else)
        self.semantic_stack.append(etrue)
        self.semantic_stack.append(efalse)

    def action_28(self, prev_token):
        efalse = self.semantic_stack.pop()
        etrue = self.semantic_stack.pop()

        # skip_else is pushed onto stack in action_27
        skip_else = self.semantic_stack.pop()
        self.backpatch_list(skip_else, self.quadruples.get_next_quad())

    def action_29(self, prev_token):
        efalse = self.semantic_stack.pop()
        etrue = self.semantic_stack.pop()
        self.backpatch_list(efalse, self.quadruples.get_next_quad())

    def action_30(self, prev_token):
        # print(prev_token)
        # Lookup token by value?
        id = self.global_table.lookup(prev_token[1])

        if (id is None):
            raise Exception("Couldn't find id in action_30")
        self.semantic_stack.append(id)
        self.semantic_stack.append(EType.ARITHMETIC)

    def action_31(self, prev_token):
        etype = self.semantic_stack.pop()
        if (etype != EType.ARITHMETIC):
            raise Exception("Etype mismatch error")

        symbol_table_entry_2 = self.semantic_stack.pop()
        # Offset implemented in later actions
        offset = self.semantic_stack.pop()
        symbol_table_entry_1 = self.semantic_stack.pop()

        typecheck_value = self.typecheck(symbol_table_entry_1, symbol_table_entry_2)

        if (typecheck_value == 3):
            raise Exception("Type mismatch error in action_31")

        if (typecheck_value == 2):
            # No reals in python, so we use float
            temp_entry = self.create("temp", float)
            self.generate("ltof", symbol_table_entry_2, temp_entry)
            if (offset == None):
                self.generate("move", temp_entry, symbol_table_entry_1)
            else:
                self.generate("stor", temp_entry, offset, symbol_table_entry_1)
        else:
            if (offset == None):
                self.generate("move", symbol_table_entry_2, symbol_table_entry_1)
            else:
                self.generate("stor", symbol_table_entry_2, offset, symbol_table_entry_1)


    def action_32(self, prev_token):
        etype = self.semantic_stack.pop()
        id = self.peek_stack()

        if (etype != EType.ARITHMETIC):
            raise Exception("EType mismatch error in action_32")
        if (not id.isArray):
            raise Exception("id is not array error in action_32")

    def action_33(self, prev_token):
        etype = self.semantic_stack.pop()
        if (etype != EType.ARITHMETIC):
            raise Exception("EType mismatch error in action_33")

        id = self.semantic_stack.pop()
        if (id.type != int and id.type != "INTEGER"):
            raise Exception("type mismatch error in action_33")

        array = self.peek_stack()
        temp1 = self.create("temp", int)
        temp2 = self.create("temp", int)
        self.generate("move", array.lower_bound, temp1)
        self.generate("sub", id, temp1, temp2)
        self.semantic_stack.append(temp2)

    def action_34(self, prev_token):
        etype = self.semantic_stack.pop()
        id = self.peek_stack()
        if (id.isFunction):
            self.semantic_stack.append(etype)
            self.execute(52, prev_token)
        else:
            self.semantic_stack.append(None)

    def action_35(self, prev_token):
        etype = self.semantic_stack.pop()
        id = self.peek_stack()
        self.semantic_stack.append(etype)
        self.param_count.append(0)
        self.param_stack.append(id.parameter_info)

    def action_36(self, prev_token):
        etype = self.semantic_stack.pop()
        id = self.semantic_stack.pop()
        if (id.number_of_parameters != 0):
            raise Exception("Wrong number of parameters in action_36")
        self.generate("call", id.name, 0)

    def action_37(self, prev_token):
        etype = self.semantic_stack.pop()
        if (etype != EType.ARITHMETIC):
            raise("Etype mistmatch error")

        id = self.peek_stack()
        # if id is not variable, constant, function result, or array
        if (not (id.isVariable or isinstance(id, symbol_table.ConstantEntry) or id.isFunctionResult or id.isArray)):
            raise Exception("Bad param type error in action_37")

        # increment top of param count
        self.param_count.append(self.param_count.pop() + 1)

        # Find name of procedure/function on the bottom of the stack
        parameters = []
        while (not (self.peek_stack().isProcedure or self.peek_stack().isFunction)):
            parameters.append(self.semantic_stack.pop())

        # func_id is a procedure or function entry
        func_id = self.peek_stack()
        # while parameters isn't empty
        while (parameters):
            self.semantic_stack.append(parameters.pop())

        if (func_id != "READ" and func_id != "WRITE"):
            if (self.param_count[-1] > self.number_of_parameters):
                raise Exception("Wrong number of parameters in action_37")
            param = self.param_stack[-1][self.next_param]
            if (id.type != param.type):
                raise Exception("Bad param type in action_37")
            if (param.isArray):
                if (id.lower_bound != param.lower_bound or id.lower_bound != param.lower_bound):
                    raise Exception("Bad param type in action_37")

            self.next_param += 1

    def action_38(self, prev_token):
        etype = self.semantic_stack.pop()
        if (etype != EType.ARITHMETIC):
            raise Exception("Etype mismatch error in action_39")

        # token should be operator
        self.semantic_stack.append(prev_token)


    def action_39(self, prev_token):
        etype = self.semantic_stack.pop()
        if (etype != EType.ARITHMETIC):
            raise Exception("Etype mismatch error in action_39")
        id2 = self.semantic_stack.pop()

        operator = self.semantic_stack.pop()
        # operator must be replaced with roper TVI code which jump
        # if condition is met
        opcode = self.get_opcode(operator)
        id1 = self.semantic_stack.pop()
        typecheck_value = self.typecheck(id1, id2)

        if (typecheck_value == 2):
            temp = self.create("temp", float)
            self.generate("ltof", id2, temp)
            self.generate(opcode, id1, temp, "_")
        elif (typecheck_value == 3):
            temp = self.create("temp", float)
            self.generate("ltof", id1, temp)
            self.generate(opcode, temp, id2, "_")
        else:
            self.generate(opcode, id1, id2, "_")

        self.generate("goto", "_")
        etrue = make_list(self.quadruples.get_next_quad() - 2)
        efalse = make_list(self.quadruples.get_next_quad() - 1)
        self.semantic_stack.append(etrue)
        self.semantic_stack.append(efalse)
        self.semantic_stack.append(EType.RELATIONAL)

    # Should push a sign (unary plus or minus)
    def action_40(self, prev_token):
        self.semantic_stack.append(prev_token)

    def action_41(self, prev_token):
        etype = self.semantic_stack.pop()
        if (etype != EType.ARITHMETIC):
            raise Exception("Etype mismatch error in action_41")

        id = self.semantic_stack.pop()
        sign = self.semantic_stack.pop()

        # ["UNARYMINUS", None]
        if (sign[0] == "UNARYMINUS"):
            temp_entry = self.create("temp", id.type)
            if (id.type == int):
                self.generate("uminus", id, temp_entry)
            else:
                self.generate("fuminus", id, temp_entry)
            self.semantic_stack.append(temp_entry)
        else:
            self.semantic_stack.append(id)

        self.semantic_stack.append(EType.ARITHMETIC)

    def action_42(self, prev_token):
        etype = self.semantic_stack.pop()
        operator = self.get_opcode(prev_token)
        if (operator == "OR"):
            if (etype != EType.RELATIONAL):
                raise Exception("Etype mismatch error in action_42")
            # Top of stack should be list of integers
            efalse = self.peek_stack()
            self.backpatch_list(efalse, self.quadruples.get_next_quad())
        else:
            if (etype != EType.ARITHMETIC):
                raise Exception("Etype mismatch error in action_42")

        # Token should be an operator
        self.semantic_stack.append(prev_token)

    def action_43(self, prev_token):
        etype = self.semantic_stack.pop()

        if (etype == EType.RELATIONAL):
            e2false = self.semantic_stack.pop()
            e2true = self.semantic_stack.pop()
            operator = self.semantic_stack.pop()
            e1false = self.semantic_stack.pop()
            e1true = self.semantic_stack.pop()

            etrue = merge(e1true, e2true)
            efalse = e2false
            self.semantic_stack.append(etrue)
            self.semantic_stack.append(efalse)
            self.semantic_stack.append(EType.RELATIONAL)

        # etype == Etype.ARITHMETIC
        else:
            id2 = self.semantic_stack.pop()
            # From action 42
            operator = self.semantic_stack.pop()

            # Get TVI opcode associated with the operator token
            opcode = self.get_opcode(operator)

            id1 = self.semantic_stack.pop()
            typecheck_value = self.typecheck(id1, id2)

            if (typecheck_value == 0):
                temp_entry = self.create("temp", int)
                self.generate(opcode, id1, id2, temp_entry)
                self.semantic_stack.append(temp_entry)

            elif (typecheck_value == 1):
                temp_entry = self.create("temp", float)
                self.generate("f" + opcode, id1, id2, temp_entry)
                self.semantic_stack.append(temp_entry)

            elif (typecheck_value == 2):
                temp_entry1 = self.create("temp", float)
                temp_entry2 = self.create("temp", float)
                self.generate("ltof", id2, temp_entry1)
                self.generate("f" + opcode, id1, temp_entry1, temp_entry2)
                self.semantic_stack.append(temp_entry2)

            elif (typecheck_value == 3):
                temp_entry1 = self.create("temp", float)
                temp_entry2 = self.create("temp", float)
                self.generate("ltof", id1, temp_entry11)
                self.generate("f" + opcode, temp_entry1, id2, temp_entry2)
                self.semantic_stack.append(temp_entry2)

            self.semantic_stack.append(EType.ARITHMETIC)


    def action_44(self, prev_token):
        etype = self.semantic_stack.pop()
        if (etype == EType.RELATIONAL):
            efalse = self.semantic_stack.pop()
            etrue = self.semantic_stack.pop()
            if (prev_token[0] == "AND"):
                self.backpatch_list(etrue, self.quadruples.get_next_quad())

            self.semantic_stack.append(etrue)
            self.semantic_stack.append(efalse)

        # Should push an operator
        self.semantic_stack.append(prev_token)

    def action_45(self, prev_token):
        etype = self.semantic_stack.pop()

        if (etype == EType.RELATIONAL):
            e2false = self.semantic_stack.pop()
            e2true = self.semantic_stack.pop()
            operator = self.semantic_stack.pop()
            opcode = self.get_opcode(operator)


            if (opcode == "AND"):
                e1false = self.semantic_stack.pop()
                e1true = self.semantic_stack.pop()

                etrue = e2true
                efalse = merge(e1false, e2false)
                self.semantic_stack.append(etrue)
                self.semantic_stack.append(efalse)
                self.semantic_stack.append(EType.RELATIONAL)
        else:
            id2 = self.semantic_stack.pop()
            # Ex: ["MULOP", 1]
            operator = self.semantic_stack.pop()
            opcode = self.get_opcode(operator)
            id1 = self.semantic_stack.pop()
            typecheck_value = self.typecheck(id1, id2)

            if (typecheck_value != 0 and (opcode == "MOD" or operator == "DIV")):
                # Mod and div require integer operands
                raise Exception("Bad parameter error in action 45")

            if (typecheck_value == 0):
                if (opcode == "MOD"):
                    temp1 = self.create("temp", int)
                    temp2 = self.create("temp", int)
                    temp3 = self.create("temp", int)
                    self.generate("div", id1, id2, temp1)
                    self.generate("mul", id2, temp1, temp2)
                    self.generate("sub", id1, temp2, temp3)
                    self.semantic_stack.append(temp3)
                elif (opcode == "div"):
                    temp1 = self.create("temp", float)
                    temp2 = self.create("temp", float)
                    temp3 = self.create("temp", float)
                    self.generate("ltof", id1, temp1)
                    self.generate("ltof", id2, temp2)
                    self.generate("fdiv", temp1, temp2, temp3)
                    self.semantic_stack.append(temp3)
                else:
                    temp_entry = self.create("temp", int)
                    self.generate(opcode, id1, id2, temp_entry)
                    self.semantic_stack.append(temp_entry)

            elif (typecheck_value == 1):
                temp_entry = self.create("temp", float)
                self.generate("f" + opcode, id1, id2, temp_entry)
                self.semantic_stack.append(temp_entry)

            elif (typecheck_value == 2):
                temp_entry1 = self.create("temp", float)
                temp_entry2 = self.create("temp", float)
                self.generate("ltof", id2, temp_entry1)
                self.generate("f" + opcode, id1, temp_entry1, temp_entry2)
                self.semantic_stack.append(temp_entry2)

            elif (typecheck_value == 3):
                temp_entry1 = self.create("temp", float)
                temp_entry2 = self.create("temp", float)
                self.generate("ltof", id1, temp_entry11)
                self.generate("f" + opcode, temp_entry1, id2, temp_entry2)
                self.semantic_stack.append(temp_entry2)

            self.semantic_stack.append(EType.ARITHMETIC)

    def action_46(self, prev_token):
        token_type = prev_token[0]
        token_value = prev_token[1]
        if (token_type == "IDENTIFIER"):
            # Look for token in global or local symbol table
            if (self.is_global):
                id = self.global_table.lookup(token_value)
            else:
                id = self.local_table.lookup(token_value)
            # if token not found...
            if (id == None):
                raise Exception("Undeclared variable error in action 46")
            self.semantic_stack.append(id)
        elif (token_type == "INTCONSTANT" or token_type == "REALCONSTANT"):
            # Look for token in constant symbol table
            id = self.constant_table.lookup(token_value)

            # if token not found...
            if (id == None):
                if (token_type == "INTCONSTANT"):
                    id = symbol_table.ConstantEntry(token_value, int, self.is_global)
                elif (token_type == "REALCONSTANT"):
                    id = symbol_table.ConstantEntry(token_value, float, self.is_global)
                self.constant_table.insert(token_value, id)

            self.semantic_stack.append(id)

        self.semantic_stack.append(EType.ARITHMETIC)

    def action_47(self, prev_token):
        etype = self.semantic_stack.pop()
        if (etype != EType.RELATIONAL):
            raise Exception("Etype mismatch error in action_47")

        # Swap etrue and efalse on stack
        efalse = self.semantic_stack.pop()
        etrue = self.semantic_stack.pop()
        self.semantic_stack.append(efalse)
        self.semantic_stack.append(etrue)
        self.semantic_stack.append(EType.RELATIONAL)

    # Offset implemented later
    def action_48(self, prev_token):
        offset = self.semantic_stack.pop()
        if (offset != None):
            if (offset.isFunction):
                self.execute(52, prev_token)
            else:
                id = self.semantic_stack.pop()
                temp = self.create("temp", id.type)
                self.generate("load", id, offset, temp)
                self.semantic_stack.append(temp)
        self.semantic_stack.append(EType.ARITHMETIC)

    def action_49(self, prev_token):
        # get etype and id but don't change stack
        etype = self.semantic_stack.pop()
        # id should be a function
        id = self.peek_stack()
        self.semantic_stack.append(etype)

        if (etype != EType.ARITHMETIC):
            raise Exception("EType mismatch error in action_49")
        if (not id.isFunction):
            raise Exception("id is not function error in action_49")

        self.param_count.append(0)
        self.param_stack.append(id.parameter_info)


    def action_50(self, prev_token):
        # The parameters must be generated from the bottom-most to the top-most
        parameters = []

        # for each parameter on the stack
        while (self.peek_stack().isArray or isinstance(self.peek_stack(), symbol_table.ConstantEntry)or self.peek_stack().isVariable):
            parameters.append(self.semantic_stack.pop())

        # generate code for each of the parameters
        while (parameters):
            # this is one place where you will use getParamPrefix()
            self.generate("param", parameters.pop())
            self.local_memory += 1

        etype = self.semantic_stack.pop()
        id = self.semantic_stack.pop()
        num_params = self.param_count.pop()

        if (num_params > id.number_of_parameters):
            raise Exception("Throw wrong number of parameters error")

        self.generate("call", id.name, num_params)
        self.param_stack.pop()
        self.next_param = 0
        temp = self.create("temp", id.result.type)
        self.generate("move", id.result, temp)
        self.semantic_stack.append(temp)
        self.semantic_stack.append(EType.ARITHMETIC)


    def action_51(self, prev_token):
        # get all of the parameters on the stack
        parameters = []
        while (isinstance(self.peek_stack(), symbol_table.ArrayEntry), isinstance(self.peek_stack(), symbol_table.ConstantEntry), isinstance(self.peek_stack(), symbol_table.VariableEntry)):
            parameters.append(self.semantic_stack.pop())

        etype = self.semantic_stack.pop()
        id = self.semantic_stack.pop()

        if (id.name == "READ" or id.name == "WRITE"):
            # replace everything on the stack and call 51WRITE
            self.semantic_stack.append(id)
            self.semantic_stack.append(etype)
            while (parameters):
                self.semantic_stack.append(parameters.pop())
            if (id.name == "READ"):
                self.execute("51READ", prev_token)
            # if is 51WRITE
            else:
                self.execute("51WRITE", prev_token)
        else:
            num_params = self.param_count.pop()
            if (num_params != id.number_of_parameters):
                raise Exception("Throw wrong number of parameters error in action_51")

            while (parameters):
                # This is one place where you will use get_param_prefix
                self.generate("param", parameters.pop())
                self.local_memory += 1

            self.generate("call", id.name, num_params)
            self.param_stack.pop()
            self.next_param = 0

    def action_51READ(self, prev_token):
        # For each parameter on the stack in reverse order
        parameters = []
        while (isinstance(self.peek_stack()), symbol_table.VariableEntry):
            parameters.append(self.semantic_stack.pop())

        while (parameters):
            id = parameters.pop()
            if (id.type == float):
                self.generate("finp", id)
            else:
                self.generate("inp", id)

        etype = self.semantic_stack.pop()
        id = self.semantic_stack.pop()
        self.param_count.pop()

    def action_51WRITE(self, prev_token):
        # For each parameter on the stack in reverse order
        parameters = []
        while (isinstance(self.peek_stack(), symbol_table.ConstantEntry) or isinstance(self.peek_stack(), symbol_table.VariableEntry)):
            parameters.append(self.semantic_stack.pop())

        while (parameters):
            id = parameters.pop()
            if (isinstance(id, symbol_table.ConstantEntry)):
                if (id.type == float):
                    self.generate("finp", id)
                # id type is int
                else:
                    self.generate("inp", id)
            # id is variable entry
            else:
                self.generate("print", "\"" + id.name + " = \"")
                if (id.type == float):
                    self.generate("foutp", id)
                # id type is int
                else:
                    self.generate("outp", id)

        etype = self.semantic_stack.pop()
        id = self.semantic_stack.pop()
        self.param_count.pop()

    def action_52(self, prev_token):
        etype = self.semantic_stack.pop()
        id = self.semantic_stack.pop()
        if (not id.isFunction):
            raise Exception("Id is not function error in action_52")
        if (id.number_of_parameters > 0):
            raise Exception("Wrong number of parameters error in action_52")

        self.generate("call", id.name, 0)
        temp = self.create("temp", id.type)
        self.generate("move", id.result, temp)
        self.semantic_stack.append(temp)
        self.semantic_stack.append(None)

    def action_53(self, prev_token):
        etype = self.semantic_stack.pop()
        id = self.semantic_stack.pop()

        if (id.isFunction):
            # Added in final phase
            if (id != self.currentFunction):
                raise Exception("Illegal procedure error in action_53")
            self.semantic_stack.push(id.getResult())
            self.semantic_stack.push(EType.ARITHMETIC)
            pass
        else:
            self.semantic_stack.append(id)
            self.semantic_stack.append(etype)

    def action_54(self, prev_token):
        etype = self.semantic_stack.pop()
        id = self.peek_stack()
        self.semantic_stack.append(etype)

        if (not id.isProcedure):
            raise Exception("Illegal procedure error in action_54")

    def action_55(self, prev_token):
        self.backpatch(self.global_store, self.global_memory)
        self.generate("free", self.global_memory)
        self.generate("PROCEND")


    def action_56(self, prev_token):
        self.generate("PROCBEGIN", "main")
        self.global_store = self.quadruples.get_next_quad()
        # "_" will be filled in later by backpatch
        self.generate("alloc", "_")


def merge(list1, list2):
    return list1 + list2

def make_list(element):
    return [element]



class EType(Enum):
    ARITHMETIC = 1
    RELATIONAL = 2


