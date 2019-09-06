from typing import NamedTuple, Tuple

import libcst
import pytest

from tornado_native_async_transformer import (
    TornadoNativeAsyncTransformer,
    TransformError,
)

from tests.collector import (
    ExceptionCase,
    collect_exception_cases,
    TestCase,
    collect_test_cases,
)


@pytest.mark.parametrize("test_case", collect_test_cases())
def test_python_module(test_case: TestCase) -> None:
    source_tree = libcst.parse_module(test_case.before)
    visited_tree = source_tree.visit(TornadoNativeAsyncTransformer())
    assert visited_tree.code == test_case.after


@pytest.mark.parametrize("exception_case", collect_exception_cases())
def test_unsupported_python_module(exception_case: ExceptionCase) -> None:
    source_tree = libcst.parse_module(exception_case.source)

    with pytest.raises(TransformError) as exception:
        visited_tree = source_tree.visit(TornadoNativeAsyncTransformer())

    assert exception_case.expected_error_message in str(exception.value)
