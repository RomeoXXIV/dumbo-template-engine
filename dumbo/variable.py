INT = "INTERGER"
FLOAT = "FLOAT"
STRING = "STRING"
LIST = "LIST"
FOR_LIST = "FOR_LIST"
REF = "REFERENCE"

class Var:
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