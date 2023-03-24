DUMBO = r"""
"""

DUMBO_OLD = r"""
programme: txt
         | txt programme
         | dumbo_bloc
         | dumbo_bloc programme

    txt: /(?:(?!{{).\n?)+/

    dumbo_bloc: "{{" expressions_list? "}}"

    expressions_list: (expression ";")+

    expression: print
              | for_loop
              | condition
              | assignation

    print: "print" string_expression

    for_loop: "for" variable "in" (string_list | variable) "do" expressions_list "endfor"

    condition: "if" (expression_element | boolean_expression | comparison_expression) "do" expressions_list "endif"

    assignation: variable ":=" string_expression
               | variable ":=" string_list
               | variable ":=" number
               | variable ":=" operator_expression
               | variable ":=" boolean_expression
               | variable ":=" comparison_expression

    string_expression: string
                    | variable
                    | string_expression "." string_expression

    string_list: "(" string_list_interior ")"

    string_list_interior: string
                        | string"," string_list_interior

    boolean_expression: expression_element boolean_operator (expression_element | boolean_expression)

    operator_expression: expression_element operator (expression_element | operator_expression)

    comparison_expression: expression_element comparator (expression_element | operator_expression | comparison_expression)

    expression_element: variable
                      | number
                      | boolean

    variable: /[^\d\W]\w*/

    string: /'(.*?)'/

    number: SIGNED_INT

    SIGNED_INT: ["+" | "-"] INT

    INT: "0" | DIGIT_WITHOUT_ZERO DIGIT*

    DIGIT: "0".."9"

    DIGIT_WITHOUT_ZERO: "1".."9"

    boolean: "true" -> true
            | "false" -> false

    boolean_operator: "or" -> or
                    | "and" -> and

    operator: "+" -> add
            | "-" -> sub
            | "*" -> mul
            | "/" -> div
            | "%" -> mod

    comparator: "<" -> less
              | ">" -> greater
              | "=" -> equals
              | "!=" -> not_equals
              | "<=" -> less_or_equals
              | ">=" -> greater_or_equals

    %import common.WS
    %ignore WS
"""
