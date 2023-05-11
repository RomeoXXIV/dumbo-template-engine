#!/usr/bin/python3
# encoding: utf-8

from dumbo_transformers import *
from lark import Lark

def main(data_file, template_file):
    # Vérifier si les fichiers spécifiés existent (lien symbolique non valide ici)
    if not os.path.isfile(template_file) and not os.path.isfile(data_file):
        print(f"Error: the template file '{template_file}' and the data file '{data_file}' do not exist.",
              file=sys.stderr)
        sys.exit(3)
    if not os.path.isfile(data_file):
        print(f"Error: the data file '{data_file}' does not exist.", file=sys.stderr)
        sys.exit(2)
    if not os.path.isfile(template_file):
        print(f"Error: the template file '{template_file}' does not exist.", file=sys.stderr)
        sys.exit(1)

    print("Welcome to Dumbo Template Engine!\n")
    print(f"Data File: {data_file}")
    print(f"Template File: {template_file}")

    with open(data_file, "r") as f:
        data_file = f.read()

    with open(template_file, "r") as f:
        template_file = f.read()

    lark_parser = Lark.open("dumbo.lark", parser='lalr', rel_to=__file__)

    global_symbol_table = SymbolTable()

    data_tree = lark_parser.parse(data_file)
    data_tree_parser = DumboBlocTransformer(global_symbol_table, IntermediateCodeInterpreter())
    data_tree_parser.transform(data_tree)

    template_tree = lark_parser.parse(template_file)
    template_tree_parser = DumboTemplateTransformer(global_symbol_table)
    output = template_tree_parser.transform(template_tree)

    return output


if __name__ == "__main__":
    import argparse
    import os
    import sys

    parser = argparse.ArgumentParser(description="Generate a file from a template and data.")
    parser.add_argument("data_file", help="The path to the data file")
    parser.add_argument("template_file", help="The path to the model file")

    args = parser.parse_args()

    print("\n######## OUTPUT ########\n")
    print(main(args.data_file, args.template_file))
