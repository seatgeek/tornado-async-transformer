from typing import NamedTuple, Tuple

import libcst
import pytest

from tornado_native_async_transformer import TornadoNativeAsyncTransformer

from tests.collector import TestCase, collect_test_cases


@pytest.mark.parametrize("test_case", collect_test_cases())
def test_python_module(test_case: TestCase) -> None:
    source_tree = libcst.parse_module(test_case.before)
    visited_tree = source_tree.visit(TornadoNativeAsyncTransformer())
    assert visited_tree.code == test_case.after
