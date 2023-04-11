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
        self.symbolTable = symbolTable

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

                        to_add += str(item.get()) + " "
                    self._output_buffer += to_add + "\n"
                else:
                    while to_print.get_type() == REF:
                        to_print = self.symbolTable.get(to_print.get())

                    self._output_buffer += str(to_print.get()) + "\n"

                self.index += 1

            elif task.get_type() == AExpression.VAR:
                if DEBUG:
                    print("DEBUG: VARIABLE ASSIGNMENT")
                variable = task.get_content()
                #ajout d'une variable dans la mémoire si elle n'y est pas encore
                self.symbolTable.change_value(variable.get_name(), variable)

                self.index += 1

            elif task.get_type() == AExpression.FOR:
                if DEBUG:
                    print("DEBUG: BEGINNING FOR LOOP")

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
                    #on regarde les instructions suivantes (et on réinitialise l'index de la variable de la boucle for)
                    if DEBUG:
                        print("DEBUG: ENDING FOR LOOP")
                    loop_var.index = 0
                    self.index += 1

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