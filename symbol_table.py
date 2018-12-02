

class SymbolTable():
    def __init__(self, size):
        self.table = {}
        self.size = size

    def lookup(self, key):
        if key in self.table:
            return self.table[key]
        else:
            return None

    def insert(self, key, value):
        # Don't need to lookup. If key is already in the table, then
        # it simply changes the key's table value to our parameter value
        self.table[key] = value

    def size(self):
        return len(self.table)

    def dump_table(self):
        print(self.table)
        for entry in self.table:
            print(entry + ": " + str(self.table[entry].__dict__))


class SymbolTableEntry():
    def __init__(self, isVariable=False, isProcedure=False, isFunction=False, isFunctionResult=False,
                 isParameter=False, isArray=False, isReserved=False):
        self.isVariable = isVariable
        self.isProcedure = isProcedure
        self.isFunction = isFunction
        self.isFunctionResult = isFunctionResult
        self.isParameter = isParameter
        self.isArray = isArray
        self.isReserved = isReserved

    def print_entry(self):
        print(self.__dict__)


class ArrayEntry(SymbolTableEntry):
    def __init__(self, name, address, token_type, upper_bound, lower_bound, is_global):
        SymbolTableEntry.__init__(self, isArray=True)
        self.name = name
        self.address = address
        self.type = token_type
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound
        self.is_global = is_global


class ConstantEntry(SymbolTableEntry):
    def __init__(self, name, token_type, is_global):
        SymbolTableEntry.__init__(self)
        self.name = name
        self.type = token_type
        self.is_global = is_global

class FunctionEntry(SymbolTableEntry):
    def __init__(self, name, number_of_parameters, parameter_info, result, is_global):
        SymbolTableEntry.__init__(self, isFunction=True)
        self.name = name
        self.number_of_parameters = number_of_parameters
        self.parameter_info = parameter_info
        self.result = result
        self.is_global = is_global

class ProcedureEntry(SymbolTableEntry):
    def __init__(self, name, number_of_parameters, parameter_info, is_global):
        SymbolTableEntry.__init__(self, isProcedure=True)
        self.name = name
        self.number_of_parameters = number_of_parameters
        self.parameter_info = parameter_info
        self.is_global = is_global

class VariableEntry(SymbolTableEntry):
    def __init__(self, name, address, type, is_global):
        SymbolTableEntry.__init__(self, isVariable=True)
        self.name = name
        self.address = address
        self.type = type
        self.is_global = is_global

class IODeviceEntry(SymbolTableEntry):
    def __init__(self, name):
        SymbolTableEntry.__init__(self)
        self.name = name

class SymbolTableError():
    def __init__(self):
        self.error = "Tried to insert name into table where it already exists"
