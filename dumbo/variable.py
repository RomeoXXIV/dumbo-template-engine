INT = "INTEGER"
FLOAT = "FLOAT"
STRING = "STRING"
STRING_CONCAT = "STRING_CONCAT"
MATH_OP = "MATH_OP"
LIST = "LIST"
FOR_LIST = "FOR_LIST"
REF = "REFERENCE"
BOOL = "BOOLEAN"

class Variable:
    """
    Structure de donnée permettant de représenter les objets variable dans un code Dumbo
    """
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
        if self._type == LIST:
            return "(" + ",".join(self._value) + ")"
        return f"{self._value}"

    def __repr__(self):
        return f"{{{self._name} := {self._value} ({self._type})}}"

class Iterable(Variable):
    EOL = "EOL" #End Of List
    def __init__(self, *args):
        super(Iterable, self).__init__(*args)
        self.index = 0

    def get(self, index = None):
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
            result = self.get(index = self.index+1)
        except IndexError:
            result = Iterable.EOL
        return result

    def increment(self):
        self.index+=1

    def __str__(self):
        return "(" + ",".join(self._value) + ")"

    def __repr__(self):
        return f"{{{self._name} := {self._value[self.index]}, list size = {len(self._value)}, list content = {self._value}, current index = {self.index}}}"


class SymbolTable:
    """
    Structure de données représentant une table de symbole
    """
    def __init__(self, parent=None):
        self.parent = parent
        self._table = {} #key: variable name, value: Variable
        self._next = [] #list of subscopes

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

    def get_localScope(self):
        return self._table.keys()

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
        _ = "[scope:\n"

        for key, value in self._table.items():
            _ += f"{key} := {value.get()} ({value.get_type()})\n"

        _ += "\nsubscopes:\n"
        for elmnt in self._next:
            _ += f"{elmnt}\n"

        _ += "]"

        return _

    def __repr__(self):
        return str(self)