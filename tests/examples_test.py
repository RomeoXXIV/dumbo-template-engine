import pytest
from dumbo.dumbo import main


def test_main():
    data_files = [f"tests/examples/data_t{i}.dumbo" for i in range(1, 4)]
    template_files = [f"tests/examples/template{i}.dumbo" for i in range(1, 4)]
    outputs = [f"tests/examples/output{i}.html" for i in range(1, 4)]
    for data_file, template_file, output in zip(data_files, template_files, outputs):
        with open(output, "r") as f:
            output = f.read()
        assert main(data_file, template_file) == output
