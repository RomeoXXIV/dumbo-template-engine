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


class SymbolTable:
    """
    Structure de données représentant une table de symbole
    """
    def __init__(self):
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
        return self._table[k]

    def __contains__(self, o):
        return o in self._table

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
        self.stack = []
        self._output_buffer = ""

    def add_instr(self, instr):
        self.stack.append(instr)
        self.index +=1
        return self.index

    def execute(self):
        return self.stack

class AExpression:
    PRINT = "PRINT"
    VAR = "VAR"
    FOR = "FOR"
    JUMP = "JUMP"

    def get_type(self):
        return self._type

    def execute(self):
        pass

class Printing(AExpression):
    def __init__(self, content):
        self._type = AExpression.PRINT
        self.content = content

class VariableAssignment(AExpression):
    def __init__(self, content):
        self._type = AExpression.VAR
        self.variable = content

class ForLoop(AExpression):
    def __init__(self, content):
        self._type = AExpression.FOR
        self.var, self.expressions = content

class Jump(AExpression):
    def __init__(self, content):
        self._type = AExpression.JUMP
        self.content = content


# Création d'un transformateur, ébauche du projet
class ArithmeticTransformer(Transformer):
    def __init__(self, *args, **kwargs):
        super(ArithmeticTransformer, self).__init__(*args, **kwargs)
        self.counter = 0
        self._output_buffer = ""
        self.symbolTable = SymbolTable()
        self.inter = IntermediateCodeHandler()

    def expression_list(self, items):
        return items

    def expression(self, items):
        return items

    def arithmetic_expression(self, items):
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
        print("string_list_interior", self.counter)
        self.counter+=1
        result = [items[0]]
        if len(items) > 1:
            result += items[1]
        return result

    def string_list(self, items):
        print("string_list", self.counter)
        self.counter+=1
        var = Variable("__ANON__", Variable.LIST, items[0])
        return var

    def string(self, items):
        print("string", self.counter)
        self.counter+=1
        result = items[0].replace("'","")
        var = Variable("__ANON__", Variable.STRING, result)
        return var

    def dumbo_bloc(self, items):
        print("dumbo_bloc", self.counter)
        self.counter+=1
        #create new scope
        return items

    def print_expression(self, items):
        print("print_expression", self.counter)
        self.counter+=1
        #self._output_buffer += str(items[0].get()) + "\n"
        result = f"print({str(items[0].get())})"
        self.inter.add_instr(Printing(str(items[0].get())))
        return result

    def for_loop_expression(self, items):
        print("for_loop_expression", self.counter)
        self.counter+=1
        loop_var, expression_list = items

        self.inter.add_instr(ForLoop(expression_list))

        return "None"

    def loop_variable_assignment(self, items):
        print("loop_variable_assignment", self.counter)
        self.counter+=1
        loop_var, iterable = items

        loop_var._type = Variable.FOR_LIST
        loop_var._value = iterable.get()

        self.symbolTable.add_content(loop_var)

        return "items"

    def string_expression(self, items):
        print("string_expression", self.counter)
        self.counter+=1
        if len(items) > 1:
            new_items = []
            for item in items:
                if item.get_type():
                    new_items.append(item.get())
                else:
                    raise NameError(f"name '{item.get_name()}' is not defined")

            return Variable("__ANON__", Variable.STRING, " ".join(new_items))

        return items[0]

    def variable(self, items):
        print("variable", items[0], self.counter)
        self.counter+=1
        if items[0] in self.symbolTable:
            return self.symbolTable.get(items[0])
        return Variable(items[0], None, None)

    def assignment_expression(self, items):
        print("assignment_expression", self.counter)
        self.counter+=1
        var = items[2]
        if not var.get_type():
            raise NameError(f"name '{item.get_name()}' is not defined")
        var._name = str(items[0].get_name())
        #add var in scope
        self.symbolTable.add_content(var)
        self.inter.add_instr(VariableAssignment(var))
        return "variable"

    def signed_decimal_integer(self, items):
        print("signed_decimal_integer", self.counter)
        self.counter+=1
        if (items[0] == "-"):
            items[1]._value = -items[1].get()
            return items[1]

        return items[1]

    def decimal_integer(self, items):
        print("decimal_integer", self.counter)
        self.counter+=1
        if len(items) == 0:
            # value = 0
            return Variable("__ANON__", Variable.INT, 0)
        return Variable("__ANON__", Variable.INT, int("".join(items)))

    def non_zero_digit(self, items):
        print("non_zero_digit", self.counter)
        self.counter+=1
        return items[0].value

    def digit(self, items):
        print("digit", self.counter)
        self.counter+=1
        if len(items) == 0:
            return "0"
        return items[0]

    def get(self):
        return self._output_buffer

#ouverture du fichier contenant la grammaire et création du parser à partir de cette grammaire
arithmetic_parser = Lark.open("my_grammar.lark", parser='lalr', rel_to=__file__)

#ligne à tester avec la grammaire
input_to_parse = """{{
    a := ('0', '1', '2', '3');
    for i in a do
    print i;
    endfor;
    }}"""
#"{{ print \'Hello World\'; }}" #works
#"{{ 2 + 5 * 3; }}" #doesn't work: on ne peut pas faire simplement un calcul, il manque quelque chose devant (print, assignation de variable, ...)

#parsing de la ligne de test et affichage du résultat
parsing = arithmetic_parser.parse(input_to_parse)
print(parsing.pretty()) #affiche l'arbre du programme donné dans "input_to_parse"
parsed = ArithmeticTransformer()
parsed.transform(parsing)
print("parsed", parsed.get()) #affiche l'output du parsing
