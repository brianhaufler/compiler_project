class Quadruples:
    def __init__(self):
        self.quad_list = []
        self.next_quad = 0
        # dummy_quad = [None, None, None, None]
        # # Insert dummy_quad at index 0 of quad_list
        # self.quad_list.insert(self.next_quad, dummy_quad)
        # self.next_quad += 1


    def get_field(self, quad_index, field):
        return self.quad_list[quad_index][field]

    def set_field(self, quad_index, index, field):
        self.quad_list[quad_index][index] = field

    def get_next_quad(self):
        return self.next_quad

    def increment_next_quad(self):
        self.next_quad += 1

    def get_quad(self, index):
        return self.quad_list[index]

    def add_quad(self, quad):
        self.quad_list.insert(self.next_quad, quad.make_quad_array())
        # self.quad_list.insert(self.next_quad, quad)
        self.next_quad += 1

    def print_quads(self):
        quad_label = 1
        print("CODE")
        for quad in self.quad_list:
            if quad[0] != None:
                print_line = str(quad_label) + ":  " + quad[0]

            if (quad[1] != None):
                print_line += " " + quad[1]

            if (quad[2] != None):
                print_line += ", " + quad[2]

            if (quad[3] != None):
                print_line += ", " + quad[3]

            print(print_line)
            quad_label += 1



class Quadruple():
    def __init__(self, op, addr1=None, addr2=None, addr3=None):
        self.op = op
        self.addr1 = addr1
        self.addr2 = addr2
        self.addr3 = addr3
        # self.quad = [op, addr1, addr2, addr3]

    def make_quad_array(self):
        quad_array = [self.op, ]

        if (self.addr1 != None):
            quad_array.append(str(self.addr1))
        else:
            quad_array.append(self.addr1)

        # No addr2 unless addr1
        if (self.addr2 != None):
            quad_array.append(str(self.addr2))
        else:
            quad_array.append(self.addr2)

        if (self.addr3 != None):
            quad_array.append(str(self.addr3))
        else:
            quad_array.append(self.addr3)

        return quad_array
