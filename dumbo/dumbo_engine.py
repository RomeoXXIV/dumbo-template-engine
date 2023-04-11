#from variable import *
from intermediate_code import *
from lark import Transformer

class DumboBlocTransformer(Transformer):
    def __init__(self, symbolTable, pseudoCodeHandler, DEBUG = False, *args, **kwargs):
        super(DumboBlocTransformer, self).__init__(*args, **kwargs)
        self._output_buffer = ""
        self.current_scope = symbolTable
        self.inter = pseudoCodeHandler

        #only for debug purpose
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

        var = Variable("__ANON__", LIST, items[0])
        return var

    def string(self, items):
        if self.DEBUG:
            print("string", self.counter)
            self.counter+=1

        result = items[0].replace("'","")
        var = Variable("__ANON__", STRING, result)
        return var

    def dumbo_bloc(self, items):
        if self.DEBUG:
            print("dumbo_bloc", self.counter)
            self.counter+=1

        return self.inter.execute(self.current_scope)

    def print_expression(self, items):
        if self.DEBUG:
            print("print_expression", self.counter)
            self.counter+=1

        #self._output_buffer += str(items[0].get()) + "\n"
        var = items[0]
        if items[0].get_name() != "__ANON__":
            var = Variable("__ANON__", REF, var.get_name())
        self.inter.add_instr(Printing(var))
        return None

    def for_loop_expression(self, items):
        if self.DEBUG:
            print("for_loop_expression", self.counter)
            self.counter+=1

        index_and_var_name, expression_list = items
        index, loop_var = index_and_var_name

        self.inter.add_instr(EndFor((index, loop_var.get_name())))

        return None #pas besoin de renvoyer quoi que ce soit, l'expression est terminée

    def loop_variable_assignment(self, items):
        if self.DEBUG:
            print("loop_variable_assignment", self.counter)
            self.counter+=1

        loop_var, iterable = items

        #initialisation de la variable de la boucle
        loop_var = Iterable(loop_var.get_name(), FOR_LIST, [Variable(None,None,None)])

        #check si la variable existe déjà dans la table des symboles
        #sinon, l'y ajouter
        if not loop_var.get_name() in self.current_scope:
            self.current_scope.add_content(loop_var)

        index = self.inter.add_instr(ForLoop((loop_var, iterable)))

        return (index, loop_var)

    def string_expression(self, items):
        if self.DEBUG:
            print("string_expression", self.counter)
            self.counter+=1

        for item in items:
            item_type = item.get_type()
            if item_type == None:
                raise NameError(f"name '{item.get_name()}' is not defined")

        if len(items) > 1:
            new_items = []
            for item in items:
                if item.get_name() != "__ANON__":
                    new_items.append(Variable("__ANON__", REF, item.get_name()))
                else:
                    new_items.append(item)
            return Variable("__ANON__", STRING_CONCAT, new_items)

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

        if var.get_name() != "__ANON__":
            #var est un nom de variable qui est déjà référencé dans la table de symbole => référence
            new_var = Variable(items[0].get_name(), REF, var.get_name())
        else:
            #var est une variable anonyme donc on fait une assignation et pas une référence
            if var.get_type() == FOR_LIST:
                new_var = Iterable(items[0].get_name(), None, None)
            else:
                new_var = Variable(items[0].get_name(), None, None)
            new_var._type = var.get_type()
            new_var._value = var.get()

        #ajout de var dans le scope actuel si elle n'est pas encore dans la table des symboles
        if not new_var.get_name() in self.current_scope:
            self.current_scope.add_content(new_var)

        self.inter.add_instr(VariableAssignment(new_var))

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
            return Variable("__ANON__", INT, 0)
        return Variable("__ANON__", INT, int("".join(items)))

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

    def if_then_expression(self, items):
        if self.DEBUG:
            print("if_then_expression", self.counter)
            self.counter += 1

        comparison, expression_list = items

        #Add end if expression
        self.inter.add_instr(EndIf())

        return None

    def if_verification(self, items):
        if self.DEBUG:
            print("if_verification", self.counter)
            self.counter += 1

        print("comparison:", items)
        self.inter.add_instr(If(items[0]))

        return None

    def boolean_expression(self, items):
        if self.DEBUG:
            print("boolean_expression", self.counter)
            self.counter += 1

        print("items:", items)

        if len(items) > 1:
            if items[0] == "(":
                return items[1]

            b1, boolean_operator, b2 = items

            if boolean_operator == "or":
                print(b1.get() or b2.get())
                return Variable("__ANON__", BOOL, b1.get() or b2.get())
            else:
                print(b1.get() and b2.get())
                return Variable("__ANON__", BOOL, b1.get() and b2.get())

        if items[0] == "true":
            print("True", True)
            return Variable("__ANON__", BOOL, True)
        elif items[0] == "false":
            print("False", False)
            return Variable("__ANON__", BOOL, False)

        return items[0]

    def comparison_expression(self, items):
        if self.DEBUG:
            print("comparison_expression", self.counter)
            self.counter += 1

        decimal1, comparison_operator, decimal2 = items

        if comparison_operator == "<":
            return Variable("__ANON__", BOOL, decimal1.get() < decimal2.get())
        elif comparison_operator == ">":
            return Variable("__ANON__", BOOL, decimal1.get() > decimal2.get())
        elif comparison_operator == "=":
            return Variable("__ANON__", BOOL, decimal1.get() == decimal2.get())
        elif comparison_operator == "<=":
            return Variable("__ANON__", BOOL, decimal1.get() <= decimal2.get())
        elif comparison_operator == ">=":
            return Variable("__ANON__", BOOL, decimal1.get() >= decimal2.get())
        else:
            #comparison_operator == "!="
            return Variable("__ANON__", BOOL, decimal1.get() != decimal2.get())

class DumboTemplateTransformer(Transformer):
    def __init__(self, globalSymbolTable, DEBUG = False, *args, **kwargs):
        super(DumboTemplateTransformer, self).__init__(*args, **kwargs)
        self.symbolTable = globalSymbolTable

        #only for debug purpose
        self.DEBUG = DEBUG
        self.counter = 0

    def start(self, items):
        if self.DEBUG:
            print("start", self.counter)
            self.counter += 1

        return items[0]

    def programme(self, items):
        if self.DEBUG:
            print("programme", self.counter)
            self.counter += 1

        print("items:", items)

        #concat les items pour avoir la sortie
        return "".join(items)

    def txt(self, items):
        if self.DEBUG:
            print("txt", self.counter)
            self.counter += 1

        #texte à retranscrire
        return items[0].value #retourner le texte à afficher

    def dumbo_bloc(self, items):
        if self.DEBUG:
            print("dumbo_bloc", self.counter)
            self.counter += 1

        #dumbo bloc à parser
        new_scope = SymbolTable(parent = self.symbolTable)
        self.symbolTable.add_depth(new_scope)
        pseudoCode = PseudoCode()
        dumbo_bloc_content = DumboBlocTransformer(new_scope, pseudoCode, DEBUG = self.DEBUG)
        dumbo_bloc_content.transform(items[0])

        return pseudoCode.execute(new_scope)
