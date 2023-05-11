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
    A class used to represent a variable in Dumbo code.

    Attributes:
    ----------
    _name : str
        the name of the variable.
    _vtype : str
        the type of the variable.
    _value : Any
        the value of the variable.
    """

    def __init__(self, name, vtype, value):
        self._name = name
        self._vtype = vtype
        self._value = value

    def get_name(self):
        return self._name

    def get_type(self):
        return self._vtype

    def get_value(self):
        return self._value

    def __eq__(self, o):
        if isinstance(o, Variable):
            return self._value == o.get_value() and self._vtype == o.get_type()
        return self._value == o

    def __str__(self):
        if self._vtype == LIST:
            return "(" + ",".join(self._value) + ")"
        return f"{self._value}"

    def __repr__(self):
        return f"{{{self._name} := {self._value} ({self._vtype})}}"


class Iterable(Variable):
    """
    A class used to represent an iterable object, such as a list. Inherits from the Variable class.

    Specific Attributes:
    -------------------
    index : int
        The current index of the iterable object.

    Specific Methods:
    ----------------
    increment_index()
        Increment the current index by 1.
    get_next_value()
        Get the next value in the iterable based on the current index.
    get_value(index=None)
        Get the value at the specified index, or at the current index if none is provided.
    """

    EOL = "EOL"  # End Of List

    def __init__(self, name, vtype, value):
        super().__init__(name, vtype, value)
        self.index = 0

    def increment_index(self):
        """Increment the current index by 1."""
        self.index += 1

    def get_next_value(self):
        """Get the next value in the iterable based on the current index."""
        try:
            result = self.get_value(index=self.index + 1)
        except IndexError:
            result = Iterable.EOL
        return result

    def get_value(self, index=None):
        """
        Get the value at the specified index, or at the current index if none is provided.

        Parameters
        ----------
        index : int, optional
            The index of the value to get (default is None).

        Raises
        ------
        IndexError
            If the index is out of range.
        """
        if index:
            if index < len(self._value):
                return self._value[index]
            else:
                raise IndexError("list index out of range")

        if self.index < len(self._value):
            return self._value[self.index]
        else:
            raise IndexError("list index out of range")

    def __str__(self):
        return "(" + ",".join(self._value) + ")"

    def __repr__(self):
        return f"{{{self._name} := {self._value[self.index]}, list size = {len(self._value)}, " \
               f"list content = {self._value}, current index = {self.index}}}"


class SymbolTable:
    """
        A class used to represent a symbol table.

        Attributes:
        ----------
        parent : SymbolTable, optional
            The parent symbol table, None for the global scope.
        _table : dict
            A dictionary with variable names as keys and Variable objects as values.
        _next : list
            A list of subscopes (nested symbol tables).

        Methods:
        -------
            add_content(newc: Variable)
                Adds a new variable to the symbol table.
            add_depth(newd: SymbolTable)
                Adds a new nested scope (subscope) to the symbol table.
            get(k: str)
                Retrieves a variable from the symbol table or its parent scopes.
            change_value(k: str, newc: Variable)
                Changes the value of a variable in the symbol table or its parent scopes.
            get_localScope()
                Returns a list of variable names in the current scope.
            get_subscope()
                Returns the first subscope (nested symbol table) of the current scope.
            remove_scope(scope: SymbolTable)
                Removes a subscope (nested symbol table) from the current scope.
            __contains__(o: str)
                Checks if a variable name exists in the symbol table or its parent scopes.
        """

    def __init__(self, parent=None):
        self.parent = parent
        self._table = {}  # key: variable name, value: Variable
        self._next = []  # list of subscopes

    def add_variable(self, new_variable):
        """
        Adds a new variable to the symbol table.

        Parameters:
        ----------
        variable : Variable
            The variable to add to the symbol table.
        """
        self._table.update({new_variable.get_name(): new_variable})

    def add_subscope(self, new_subscope):
        """
        Adds a new nested scope (subscope) to the symbol table.

        Parameters:
        ----------
        new_subscope : SymbolTable
            The nested symbol table (subscope) to add.
        """
        self._next.append(new_subscope)

    def get(self, k):
        """
        Retrieves a variable from the symbol table or its parent scopes.

        Parameters:
        ----------
        k : str
            The variable name to retrieve.

        Returns:
        -------
        Variable
            The retrieved variable.
        """
        if k in self._table.keys():
            return self._table[k]
        elif self.parent:
            return self.parent.get(k)
        else:
            raise NameError(f"'{k}' not in symbol table")

    def change_value(self, k, new_variable):
        """
        Changes the value of a variable in the symbol table or its parent scopes.

        Parameters:
        ----------
        k : str
            The variable name to change.
        new_variable : Variable
            The new variable to replace the old one.
        """
        if k in self._table.keys():
            self._table[k] = new_variable
        elif self.parent:
            self.parent.change_value(k, new_variable)
        else:
            return NameError(f"'{k}' not in symbol table")

    def get_localScope(self):
        """Returns a list of variable names in the current scope."""
        return self._table.keys()

    def get_subscope(self):
        """Returns the first subscope (nested symbol table) of the current scope."""
        return self._next[0]

    def remove_scope(self, scope):
        """Removes a subscope (nested symbol table) from the current scope."""
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
            _ += f"{key} := {value.get_value()} ({value.get_type()})\n"

        _ += "\nsubscopes:\n"
        for elmnt in self._next:
            _ += f"{elmnt}\n"

        _ += "]"

        return _

    def __repr__(self):
        return str(self)