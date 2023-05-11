import pytest
from dumbo import main


def test_valide():
    # Notre test pour tester les tests
    assert True


@pytest.mark.parametrize("data_file, template_file, output", [
    (f"examples/data_t{i}.dumbo", f"examples/template{i}.dumbo", f"examples/output{i}.html")
    for i in range(1, 4)
])
def test_output_generation(data_file, template_file, output):
    # Nos tests pour la génération de la sortie finale
    with open(data_file, "r") as f:
        data = f.read()
    with open(template_file, "r") as f:
        template = f.read()
    with open(output, "r") as f:
        out = f.read()
    assert main(data, template) == out

# TODO : Faire le reste des tests

# Vous pouvez ajouter des fonctions de test supplémentaires si nécessaire :
# def test_argument_parsing():
#     pass
#
# def test_data_file_handling():
#     pass
#
# def test_template_file_handling():
#     pass


'''
import unittest
from dumbo import main


class TestDumboTemplateEngine(unittest.TestCase):

    def test_valide(self):
        # Nos tests pour la gestion des arguments
        self.assertEqual(True, True)

    def test_argument_parsing(self):
        # Nos tests pour la gestion des arguments
        pass

    def test_data_file_handling(self):
        # Nos tests pour la gestion des fichiers de données
        pass

    def test_template_file_handling(self):
        # Nos tests pour la gestion des fichiers de templates
        pass

    def test_output_generation(self):
        # Nos tests pour la génération de la sortie finale
        data_files = [f"examples/data_t{i}.dumbo" for i in range(1, 4)]
        template_files = [f"examples/template{i}.dumbo" for i in range(1, 4)]
        outputs = [f"examples/output{i}.html" for i in range(1, 4)]
        for data_file, template_file, output in zip(data_files, template_files, outputs):
            with open(data_file, "r") as f:
                data = f.read()
            with open(template_file, "r") as f:
                template = f.read()
            with open(output, "r") as f:
                out = f.read()
            self.assertEqual(main(data, template), out)


if __name__ == '__main__':
    unittest.main()'''
