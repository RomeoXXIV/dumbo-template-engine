from lark import Lark, Transformer

class Variable:
    """
    Structure de donnée permettant de représenter les objets variable dans un code Dumbo
    """
    INT = "INTERGER"
    DOUBLE = "DOUBLE"
    FLOAT = "FLOAT"
    STRING = "STRING"
    CHAR = "CHARACTER"
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

# Création d'un transformateur, ébauche du projet
class ArithmeticTransformer(Transformer):
    def __init__(self, *args, **kwargs):
        super(ArithmeticTransformer, self).__init__(*args, **kwargs)
        self._output_buffer = ""
        self.symbolTable = SymbolTable()

    def arithmetic_expression(self, items):
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

    def string(self, items):
        result = items[0].replace("'","")
        return result

    def term(self, items):
        if len(items) == 1:
            return items[0]
        elif items[1] == "*":
            return items[0] * items[2]
        else:
            return items[0] / items[2]

    def dumbo_bloc(self, items):
        #create new scope
        return items

    def print_expression(self, items):
        self._output_buffer += items[0] + "\n"
        return items[0]

    def string_expression(self, items):
        if len(items) > 1:
            return " ".join(items)

        return items[0]

    def variable(self, items):
        if items[0] in self.symbolTable:
            return str(self.symbolTable.get(items[0]).get())
        return items[0]

    def assignment_expression(self, items):
        var = Variable(str(items[0]), None, items[2])
        #print(var)
        #add var in scope
        self.symbolTable.add_content(var)
        return var

    def signed_decimal_integer(self, items):
        if (items[0] == "-"):
            return -items[1]

        return items[1]

    def decimal_integer(self, items):
        if len(items) == 0:
            # value = 0
            return 0
        return int("".join(items))

    def non_zero_digit(self, items):
        return items[0].value

    def digit(self, items):
        if len(items) == 0:
            return "0"
        return items[0]

    def get(self):
        return self._output_buffer

#ouverture du fichier contenant la grammaire et création du parser à partir de cette grammaire
arithmetic_parser = Lark.open("../dumbo/dumbo.lark", parser='lalr', rel_to=__file__)

#ligne à tester avec la grammaire
input_to_parse = """{{
    a := 2+5*3;
    print \'2 + 5 * 3 = \' . a;
    print \'test\';
    }}"""
#"{{ print \'Hello World\'; }}" #works
#"{{ 2 + 5 * 3; }}" #doesn't work: on ne peut pas faire simplement un calcul, il manque quelque chose devant (print, assignation de variable, ...)

#parsing de la ligne de test et affichage du résultat
parsing = arithmetic_parser.parse(input_to_parse)
#print(parsing.pretty()) #affiche l'arbre du programme donné dans "input_to_parse"
parsed = ArithmeticTransformer()
parsed.transform(parsing)
print(parsed.get()) #affiche l'output du parsing
