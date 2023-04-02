import argparse
import os
import sys


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

    print("Welcome to Dumbo Template Engine!")
    print(f"Data File: {data_file}")
    print(f"Template File: {template_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a file from a template and data.")
    parser.add_argument("data_file", help="The path to the data file")
    parser.add_argument("template_file", help="The path to the model file")

    args = parser.parse_args()

    main(args.data_file, args.template_file)
