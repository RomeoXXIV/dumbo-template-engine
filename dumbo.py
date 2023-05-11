import argparse
import os
import sys

import dumbo_core.dumbo_transformers as dt
from lark import Lark


def main(data_file, template_file):
    lark_parser = Lark.open("dumbo_core/dumbo.lark", parser='lalr', rel_to=__file__)

    global_symbol_table = dt.SymbolTable()

    data_tree = lark_parser.parse(data_file)
    data_tree_parser = dt.DumboBlocTransformer(global_symbol_table, dt.IntermediateCodeInterpreter())
    data_tree_parser.transform(data_tree)

    template_tree = lark_parser.parse(template_file)
    template_tree_parser = dt.DumboTemplateTransformer(global_symbol_table)
    out = template_tree_parser.transform(template_tree)
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a file from a template and data.")
    parser.add_argument("data_file", help="The path to the data file")
    parser.add_argument("template_file", help="The path to the model file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode")

    args = parser.parse_args()

    # Vérifier si les fichiers spécifiés existent (lien symbolique non valide ici)
    if not os.path.isfile(args.template_file) and not os.path.isfile(args.data_file):
        print(f"Error: the template file '{args.template_file}' and the data file '{args.data_file}' do not exist.",
              file=sys.stderr)
        sys.exit(3)
    if not os.path.isfile(args.data_file):
        print(f"Error: the data file '{args.data_file}' does not exist.", file=sys.stderr)
        sys.exit(2)
    if not os.path.isfile(args.template_file):
        print(f"Error: the template file '{args.template_file}' does not exist.", file=sys.stderr)
        sys.exit(1)

    with open(args.data_file, "r") as f:
        data = f.read()

    with open(args.template_file, "r") as f:
        template = f.read()

    if args.verbose:
        print("Welcome to Dumbo Template Engine!\n")
        print(f"Data File: {args.data_file}")
        print(f"Template File: {args.template_file}")

    output = main(data, template)

    if args.verbose:
        print("\n######## OUTPUT ########\n")

    print(output)
