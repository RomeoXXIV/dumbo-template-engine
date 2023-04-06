from lark import Lark, Transformer

class Variable:
    """
    Structure de donnée permettant de représenter les objets variable dans un code Dumbo
    """
    INT = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    LIST = "LIST"
    FOR_LIST = "FOR_LIST"
    REF = "REFERENCE"

    def __init__(self, name, type, value):
        self._name = name
        self._type = type
        self._value = value

    def get_name(self):
        """
        Retrourne le nom de la variable.
        """
        return self._name

    def get_type(self):
        """
        Retourne le type de la variable
        """
        return self._type

    def get(self):
        """
        Retourne la valeur de la variable
        """
        return self._value

    def __eq__(self, o):
        if isinstance(o, Variable):
            return (self._value == o.get() and self._type == o.get_type())

        return self._value == o

    def __str__(self):
        return f"{self._value}"

    def __repr__(self):
        return f"{{{self._name} := {self._value} ({self._type})}}"

class ListVariable(Variable):
    EOL = "EOL" #End Of List
    def __init__(self, *args):
        super(ListVariable, self).__init__(*args)
        self.index = 0

    def get_index(self, index = None):
        if index:
            if (index < len(self._value)):
                return self._value[index]
            else:
                raise IndexError("list index out of range")
        
        if (self.index < len(self._value)):
            return self._value[self.index]
        else:
            raise IndexError("list index out of range")

    def next(self):
        try:
            result = self.get_index(index = self.index+1)
        except IndexError:
            result = ListVariable.EOL
        return result

    def increment(self):
        self.index+=1

    def __str__(self):
        values = []
        for var in self._value:
            values.append(var.get())

        return str(values)

    def __repr__(self):
        return f"{{{self._name} := {self._value[self.index]}, list size = {len(self._value)}, list content = {self._value}, current index = {self.index}}}"


class SymbolTable:
    """
    Structure de données représentant une table de symbole
    """
    def __init__(self, parent=None):
        self.parent = parent
        self._table = {}
        self._next = []

    def add_content(self, newc):
        """
        Ajout de l'élément newc dans la table de symboles
        """
        self._table.update({newc.get_name():newc})

    def add_depth(self, newd):
        """
        Ajout d'une nouvelle profondeur ou scope dans la table
        """
        self._next.append(newd)

    def get(self, k):
        """
        Récupération d'un élément dans la table
        """
        if k in self._table.keys():
            return self._table[k]
        elif self.parent:
            return self.parent.get(k)
        else:
            raise NameError(f"'{k}' not in symbol table")

    def change_value(self, k, newc):
        if k in self._table.keys():
            self._table[k] = newc
        elif self.parent:
            self.parent.change_value(k, newc)
        else:
            return NameError(f"'{k}' not in symbol table")

    def get_subscope(self):
        #return first subscope
        return self._next[0]

    def remove_scope(self, scope):
        self._next.remove(scope)

    def __contains__(self, o):
        if o in self._table.keys():
            return True
        elif self.parent:
            return o in self.parent
        else:
            return False

    def __str__(self):
        _ = "[\n"

        for key, value in self._table.items():
            _ += f"{key} := {value.get()}\n"

        for elmnt in self._next:
            _ += f"{elmnt}\n"

        _ += "]"

        return _

    def __repr__(self):
        return str(self)


class IntermediateCodeHandler:
    def __init__(self):
        self.index = 0
        self.symbolTable = None
        self.stack = []
        self._output_buffer = ""

    def add_instr(self, instr):
        self.stack.append(instr)
        self.index +=1
        return self.index

    def execute(self, globalSymbolTable, DEBUG=False):
        self.symbolTable = globalSymbolTable

        if DEBUG:
            print("DEBUG MODE IS ON")

        self.index = 0

        while self.index < len(self.stack):
            task = self.stack[self.index]
            
            if DEBUG:
                print("DEBUG:", task)

            if task.get_type() == AExpression.PRINT:
                if DEBUG:
                    print("DEBUG: PRINT STATEMENT")
                #afficher du contenu
                to_print = task.get_content()
                # si la variable à afficher n'est pas anonyme, elle est dans la table des symboles
                # donc il est possible que sa valeur ait été modifiée entre temps => on récupère la bonne valeur
                if to_print.get_name() != "__ANON__":
                    to_print = self.symbolTable.get(to_print.get_name())

                if to_print.get_type() == Variable.FOR_LIST:
                    #gerer differemment les variables for_list
                    self._output_buffer += str(to_print.get_index()) + "\n"
                else:
                    self._output_buffer += str(to_print.get()) + "\n"

                self.index += 1

            elif task.get_type() == AExpression.VAR:
                if DEBUG:
                    print("DEBUG: VARIABLE ASSIGNMENT")
                variable = task.get_content()
                #ajout d'une variable dans la mémoire si elle n'y est pas encore
                self.symbolTable.change_value(variable.get_name(), variable)
                # if not variable.get_name() in self.symbolTable:
                #     self.symbolTable.add_content(variable)
                #     #ça ne devrait pas arriver puisque la table des symboles est sensée être donnée complétée
                # else:
                #     var = self.symbolTable.get(variable.get_name())
                #     var._type = variable.get_type()
                #     var._value = variable.get()

                self.index += 1

            elif task.get_type() == AExpression.FOR:
                if DEBUG:
                    print("DEBUG: BEGINNING FOR LOOP")
                #on récupère le nouveau scope créé par la boucle
                self.symbolTable = self.symbolTable.get_subscope()
                # new_scope = SymbolTable(parent = self.symbolTable)
                # self.symbolTable.add_depth(new_scope)
                # self.symbolTable = new_scope

                #ajouter la loop variable dans ce scope ou check s'il n'existe pas déjà une variable de ce nom
                loop_var = task.get_content()
                self.symbolTable.change_value(loop_var.get_name(), loop_var)
                # if not loop_var.get_name() in self.symbolTable:
                #     new_scope.add_content(loop_var)
                #     #ça ne devrait pas arriver puisque la table des symboles est sensée être donnée complétée
                # else:
                #     var = self.symbolTable.get(loop_var.get_name())
                #     #si la variable était déjà de type "FOR_LIST"
                #     if var.get_type() == Variable.FOR_LIST:
                #         var._value = loop_var.get()
                #         var.index = loop_var.index
                #     #sinon
                #     else:
                #         var = loop_var #pas certain que ca fonctionne

                self.index += 1

            elif task.get_type() == AExpression.ENDFOR:
                if DEBUG:
                    print("DEBUG: ENDING FOR LOOP OR JUMP")
                #deal with scopes
                index, loop_var = task.get_content()
                loop_var = self.symbolTable.get(loop_var.get_name())
                if loop_var.next() != ListVariable.EOL:
                    #On n'a pas encore parcouru toute la liste donc on retourne au début de la boucle
                    loop_var.increment()
                    self.index = index
                else:
                    #on regarde les instructions suivantes (et on réinitialise l'index de la variable de la boucle for)
                    loop_var.index = 0
                    self.index += 1
                    #on sort du scope
                    previous_scope = self.symbolTable
                    self.symbolTable = self.symbolTable.parent
                    self.symbolTable.remove_scope(previous_scope)

        return self._output_buffer


class AExpression:
    PRINT = "PRINT"
    VAR = "VAR"
    FOR = "FOR"
    ENDFOR = "ENDFOR"
    JUMP = "JUMP"

    def __init__(self, type, content):
        self._type = type
        self.content = content

    def get_content(self):
        return self.content

    def get_type(self):
        return self._type

    def __repr__(self):
        return f"{self._type}: {self.content}"

class Printing(AExpression):
    def __init__(self, content):
        super(Printing, self).__init__(AExpression.PRINT, content) #on stocke une variable

class VariableAssignment(AExpression):
    def __init__(self, content):
        super(VariableAssignment, self).__init__(AExpression.VAR, content) #on stocke une variable

class ForLoop(AExpression):
    def __init__(self, content):
        super(ForLoop, self).__init__(AExpression.FOR, content) #on stocke une variable

class EndFor(AExpression):
    def __init__(self, content):
        super(EndFor, self).__init__(AExpression.ENDFOR, content) #index et le nom d'une variable (tuple)

class Jump(AExpression):
    def __init__(self, content):
        super(Jump, self).__init__(AExpression.JUMP, content) #index


# Création d'un transformateur, ébauche du projet
class ArithmeticTransformer(Transformer):
    def __init__(self, globalSymbolTable, DEBUG = False, *args, **kwargs):
        super(ArithmeticTransformer, self).__init__(*args, **kwargs)
        self._output_buffer = ""
        self.symbolTable = globalSymbolTable
        self.current_scope = self.symbolTable
        self.inter = IntermediateCodeHandler()

        self.DEBUG = DEBUG
        self.counter = 0

    def expression_list(self, items):
        return items

    def expression(self, items):
        return items

    def arithmetic_expression(self, items):
        if self.DEBUG:
            print("arithmetic_expression", self.counter)
            self.counter+=1

        if items[0] == "(":
            return items[1]

        result = items[0]
        if len(items) == 1:
            return result

        elif (items[1] == "-"):
            result -= items[2]
        elif (items[1] == "+"):
            result += items[2]
        elif items[1] == "*":
            return items[0] * items[2]
        else:
            return items[0] / items[2]

        return result

    def string_list_interior(self,items):
        if self.DEBUG:
            print("string_list_interior", self.counter)
            self.counter+=1

        result = [items[0]]
        if len(items) > 1:
            result += items[1]
        return result

    def string_list(self, items):
        if self.DEBUG:
            print("string_list", self.counter)
            self.counter+=1

        var = ListVariable("__ANON__", Variable.LIST, items[0])
        return var

    def string(self, items):
        if self.DEBUG:
            print("string", self.counter)
            self.counter+=1

        result = items[0].replace("'","")
        var = Variable("__ANON__", Variable.STRING, result)
        return var

    def dumbo_bloc(self, items):
        if self.DEBUG:
            print("dumbo_bloc", self.counter)
            self.counter+=1

        #create new scope
        return items

    def print_expression(self, items):
        if self.DEBUG:
            print("print_expression", self.counter)
            self.counter+=1

        #self._output_buffer += str(items[0].get()) + "\n"
        result = f"print({str(items[0].get())})"
        self.inter.add_instr(Printing(items[0]))
        return result

    def for_loop_expression(self, items):
        if self.DEBUG:
            print("for_loop_expression", self.counter)
            self.counter+=1

        index_and_var_name, expression_list = items

        self.inter.add_instr(EndFor(index_and_var_name))

        #on sort de la boucle donc on peut revenir dans le scope précédent
        self.current_scope = self.current_scope.parent
        # Par la grammaire, nous pouvons être certain qu'il existe au moins un scope global comme
        # parent du scope de la for loop. On est donc certain qu'il n'est pas nul après changement

        return None #pas besoin de renvoyer quoi que ce soit, l'expression est terminée

    def loop_variable_assignment(self, items):
        if self.DEBUG:
            print("loop_variable_assignment", self.counter)
            self.counter+=1

        loop_var, iterable = items

        #Check iterable est bien iterable
        if not iterable.get_type() == Variable.LIST:
            raise TypeError(f"{iterable.get_name()} ({iterable.get_type()}) not iterable")

        #creer un nouveau scope pour la boucle for
        new_scope = SymbolTable(parent = self.current_scope)
        self.current_scope.add_depth(new_scope)
        self.current_scope = new_scope
        loop_var = ListVariable(loop_var.get_name(), Variable.FOR_LIST, iterable.get())

        #check si la variable existe déjà dans la table des symboles
        #sinon, l'y ajouter
        if not loop_var.get_name() in self.current_scope:
            self.current_scope.add_content(loop_var)

        index = self.inter.add_instr(ForLoop(loop_var))

        return (index, loop_var)

    def string_expression(self, items):
        if self.DEBUG:
            print("string_expression", self.counter)
            self.counter+=1

        if len(items) > 1:
            new_items = []
            for item in items:
                item_type = item.get_type()
                if item_type == Variable.LIST or item_type == Variable.FOR_LIST:
                    new_items.append(str(item))
                elif item_type:
                    new_items.append(str(item.get()))
                else:
                    raise NameError(f"name '{item.get_name()}' is not defined")

            return Variable("__ANON__", Variable.STRING, " ".join(new_items))

        return items[0]

    def variable(self, items):
        if self.DEBUG:
            print("variable", items[0], self.counter)
            self.counter+=1

        if items[0] in self.current_scope:
            return self.current_scope.get(items[0])
        return Variable(items[0], None, None)

    def assignment_expression(self, items):
        if self.DEBUG:
            print("assignment_expression", self.counter)
            self.counter+=1

        var = items[2]
        if not var.get_type():
            raise NameError(f"name '{item.get_name()}' is not defined")
        var._name = str(items[0].get_name())

        #ajout de var dans le scope actuel si elle n'est pas encore dans la table des symboles
        if not var.get_name() in self.current_scope:
            self.current_scope.add_content(var)

        self.inter.add_instr(VariableAssignment(var))

        return None #pas besoin de retourner quoi que ce soit, l'expression est finie

    def signed_decimal_integer(self, items):
        if self.DEBUG:
            print("signed_decimal_integer", self.counter)
            self.counter+=1

        if (items[0] == "-"):
            items[1]._value = -items[1].get()
            return items[1]

        return items[1]

    def decimal_integer(self, items):
        if self.DEBUG:
            print("decimal_integer", self.counter)
            self.counter+=1

        if len(items) == 0:
            return Variable("__ANON__", Variable.INT, 0)
        return Variable("__ANON__", Variable.INT, int("".join(items)))

    def non_zero_digit(self, items):
        if self.DEBUG:
            print("non_zero_digit", self.counter)
            self.counter+=1

        return items[0].value

    def digit(self, items):
        if self.DEBUG:
            print("digit", self.counter)
            self.counter+=1

        if len(items) == 0:
            return "0"
        return items[0]

    def get(self):
        return self.inter.execute(self.symbolTable, DEBUG = self.DEBUG)

#ouverture du fichier contenant la grammaire et création du parser à partir de cette grammaire
arithmetic_parser = Lark.open("../dumbo/dumbo.lark", parser='lalr', rel_to=__file__)

#ligne à tester avec la grammaire
input_to_parse = """{{
    i := ('t', 'e', 's', 't');
    print 'test ' . i ;
    a := ('0', '1', '2', '3');
    for i in a do
        print i;
    endfor;
    }}"""
"""
{{
    a := 'test';
    print a;
}}
"""

#parsing de la ligne de test et affichage du résultat
parsing = arithmetic_parser.parse(input_to_parse)
print(parsing.pretty()) #affiche l'arbre du programme donné dans "input_to_parse"
parsed = ArithmeticTransformer(SymbolTable()) # ArithmeticTransformer(SymbolTable(), DEBUG = True)
parsed.transform(parsing)

print("######## parsed ########\n")

print("\n######## OUTPUT ########\n")

print(parsed.get())
#print("parsed", parsed.get()) #affiche l'output du parsing
