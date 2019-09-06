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
