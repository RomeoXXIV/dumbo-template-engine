from variable import *

class PseudoCode:
    def __init__(self):
        self.index = 0
        self.symbolTable = None
        self.stack = []
        self._output_buffer = ""

    def add_instr(self, instr):
        self.stack.append(instr)
        self.index +=1
        return self.index

    def execute(self, symbolTable, DEBUG=False):
        globalSymbolTable = symbolTable
        self.symbolTable = globalSymbolTable
        while globalSymbolTable.parent:
            globalSymbolTable = globalSymbolTable.parent

        def resolve(v1, op, v2):
            result_v1 = v1.get()
            result_v2 = v2.get()
            _v1 = v1
            _v2 = v2
            while _v1.get_type() == REF:
                _v1 = self.symbolTable.get(result_v1)
                result_v1 = _v1.get()
            if v1.get_type() == MATH_OP:
                result_v1 = resolve(*result_v1)

            while _v2.get_type() == REF:
                _v2 = self.symbolTable.get(result_v2)
                result_v2 = _v2.get()
            if _v2.get_type() == MATH_OP:
                result_v2 = resolve(*result_v2)

            if _v1.get_type() != INT and _v1.get_type() != MATH_OP:
                raise TypeError(f"Can't convert {_v1.get_type()} to {INT}")
            if _v2.get_type() != INT and _v2.get_type() != MATH_OP:
                raise TypeError(f"Can't convert {_v1.get_type()} to {INT}");

            if op == "+":
                return result_v1 + result_v2
            elif op == "-":
                return result_v1 - result_v2
            elif op == "*":
                return result_v1 * result_v2
            #elif op == "/":
            return result_v1 / result_v2

        if DEBUG:
            print("DEBUG MODE IS ON\n")
            print("STACK CONTENT:")
            for task in self.stack:
                print("\t"+ str(task))

        self.index = 0

        while self.index < len(self.stack):
            task = self.stack[self.index]

            if DEBUG:
                print("\nDEBUG:", task)

            if task.get_type() == AExpression.PRINT:
                if DEBUG:
                    print("DEBUG: PRINT STATEMENT")
                #afficher du contenu
                to_print = task.get_content()
                # si la variable à afficher n'est pas anonyme, elle est dans la table des symboles
                # donc il est possible que sa valeur ait été modifiée entre temps => on récupère la bonne valeur
                if to_print.get_name() != "__ANON__":
                    to_print = self.symbolTable.get(to_print.get_name())

                if to_print.get_type() == STRING_CONCAT:
                    to_add = ""
                    for item in to_print.get():
                        while item.get_type() == REF:
                            item = self.symbolTable.get(item.get())

                        to_add += str(item.get())
                    self._output_buffer += to_add
                elif to_print.get_type() == MATH_OP:
                    to_print_content = to_print.get()
                    self._output_buffer += str(resolve(*to_print_content))
                else:
                    while to_print.get_type() == REF:
                        to_print = self.symbolTable.get(to_print.get())

                    self._output_buffer += str(to_print.get())

                #self._output_buffer += "\n"

                self.index += 1

            elif task.get_type() == AExpression.VAR:
                if DEBUG:
                    print("DEBUG: VARIABLE ASSIGNMENT")
                variable = task.get_content()

                #si la variable est une opération arithmétique, on l'évalue
                if variable.get_type() == MATH_OP:
                    #print("before:", repr(variable))
                    variable_content = variable.get()
                    result = resolve(*variable_content)
                    variable = Variable(variable.get_name(), INT, result)
                #print(repr(variable))
                #ajout d'une variable dans la mémoire si elle n'y est pas encore

                # if variable.get_name() in self.symbolTable:
                #     #la variable existe déjà
                #     if variable.get_name() in self.symbolTable.get_scope():
                #         #la variable existe au niveau local
                #         self.symbolTable.change_value(variable.get_name(), variable)
                #     else:
                #         #la variable existe au niveau global donc on crée une nouvelle variable locale du même nom
                #         self.symbolTable.add_content(variable)
                # else:
                #     #la vari

                self.symbolTable.change_value(variable.get_name(), variable)

                self.index += 1

            elif task.get_type() == AExpression.FOR:
                if DEBUG:
                    print("DEBUG: BEGINNING FOR LOOP")

                #on réupère le subscope
                self.symbolTable = self.symbolTable.get_subscope()

                #ajouter la loop variable dans ce scope ou check s'il n'existe pas déjà une variable de ce nom
                loop_var, iterable_var = task.get_content()
                #check si l'itérable est bien itérable
                while iterable_var.get_type() == REF:
                    iterable_var = self.symbolTable.get(iterable_var.get())
                if iterable_var.get_type() != LIST:
                    raise NameError(f"{iterable_var.get_name()} ({iterable_var.get_type()}) not iterable")

                new_loop_var = Iterable(loop_var.get_name(), FOR_LIST, iterable_var.get())

                self.symbolTable.change_value(loop_var.get_name(), new_loop_var)

                self.index += 1

            elif task.get_type() == AExpression.ENDFOR:
                if DEBUG:
                    print("DEBUG: ENDING FOR LOOP OR JUMP")
                #deal with scopes
                index, loop_var_name = task.get_content()
                loop_var = self.symbolTable.get(loop_var_name)
                if loop_var.next() != Iterable.EOL:
                    #On n'a pas encore parcouru toute la liste donc on retourne au début de la boucle
                    if DEBUG:
                        print("DEBUG: JUMP")
                    loop_var.increment()
                    self.index = index
                else:
                    #on regarde les instructions suivantes
                    if DEBUG:
                        print("DEBUG: ENDING FOR LOOP")
                    self.index += 1
                    #on sort du subscope donc on peut le supprimer
                    self.symbolTable = self.symbolTable.parent
                    self.symbolTable.remove_scope(self.symbolTable.get_subscope())

            elif task.get_type() == AExpression.IF:
                if DEBUG:
                    print("DEBUG: IF")

                comparison = task.get_content()
                if comparison.get() == False:
                    self.index += 1
                    while self.stack[self.index].get_type() != AExpression.ENDIF:
                        self.index += 1

                self.index += 1

            elif task.get_type() == AExpression.ENDIF:
                self.index += 1

        return self._output_buffer


class AExpression:
    PRINT = "PRINT"
    VAR = "VAR"
    FOR = "FOR"
    ENDFOR = "ENDFOR"
    JUMP = "JUMP"
    IF = "IF"
    ENDIF = "ENDIF"

    def __init__(self, type, content):
        self._type = type
        self.content = content

    def get_content(self):
        return self.content

    def get_type(self):
        return self._type

    def __repr__(self):
        return f"{self._type}: {repr(self.content)}"

class Printing(AExpression):
    def __init__(self, content):
        super(Printing, self).__init__(AExpression.PRINT, content) #on stocke une variable

class VariableAssignment(AExpression):
    def __init__(self, content):
        super(VariableAssignment, self).__init__(AExpression.VAR, content) #on stocke une variable

class ForLoop(AExpression):
    def __init__(self, content):
        super(ForLoop, self).__init__(AExpression.FOR, content) #on stocke une variable et un itérable (tuple)

    def __repr__(self):
        return f"{self._type}: LOOP VARIABLE = {self.content[0].get_name()}"

class EndFor(AExpression):
    def __init__(self, content):
        super(EndFor, self).__init__(AExpression.ENDFOR, content) #index et le nom d'une variable (tuple)

    def __repr__(self):
        return f"{self._type}: JUMP TO INSTRUCTION {self.content[0]}, INCREMENT {self.content[1]}"

class Jump(AExpression):
    def __init__(self, content):
        super(Jump, self).__init__(AExpression.JUMP, content) #index

class If(AExpression):
    def __init__(self, content):
        super(If, self).__init__(AExpression.IF, content) #variable bool

class EndIf(AExpression):
    def __init__(self, content = None):
        super(EndIf, self).__init__(AExpression.ENDIF, None)

    def __repr__(self):
        return f"{self._type}"