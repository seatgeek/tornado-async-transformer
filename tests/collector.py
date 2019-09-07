import ast
import os
from typing import Any, List, NamedTuple, Tuple

import pytest


class TestCase(NamedTuple):
    before: str
    after: str


def collect_test_cases() -> Tuple[Any, ...]:
    root_test_cases_directory = os.path.join(os.path.dirname(__file__), "test_cases")

    test_cases: List = []
    for root, _, files in os.walk(root_test_cases_directory):
        if not {"before.py", "after.py"} <= set(files):
            continue

        test_case_name = os.path.basename(root).replace("_", " ")

        with open(os.path.join(root, "before.py")) as before_file:
            before = before_file.read()

        with open(os.path.join(root, "after.py")) as after_file:
            after = after_file.read()

        test_cases.append(
            pytest.param(TestCase(before=before, after=after), id=test_case_name)
        )

    return tuple(test_cases)


class ExceptionCase(NamedTuple):
    source: str
    expected_error_message: str


def collect_exception_cases() -> Tuple[Any, ...]:
    root_exception_cases_directory = os.path.join(
        os.path.dirname(__file__), "exception_cases"
    )

    # all .py files in the top-levl of exception cases directory
    python_files = [
        os.path.join(root_exception_cases_directory, file)
        for file in os.listdir(root_exception_cases_directory)
        if file[-3:] == ".py"
    ]

    exception_cases: List = []
    for python_filename in python_files:
        with open(python_filename) as python_file:
            source = python_file.read()

        # the module's docstring is the expected error message
        ast_tree = ast.parse(source)
        docstring = ast.get_docstring(ast_tree)
        expected_error_message = docstring.replace("\n", " ")

        test_case_name = os.path.basename(python_filename).replace("_", " ")

        exception_cases.append(
            pytest.param(
                ExceptionCase(
                    source=source, expected_error_message=expected_error_message
                ),
                id=test_case_name,
            )
        )

    return tuple(exception_cases)
