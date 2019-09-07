from typing import List, Optional, Tuple, Union, Set

import libcst as cst

from tornado_async_transformer.helpers import (
    with_added_imports,
    name_or_attribute_matches,
    name_or_attribute_matches_one_of,
)


class TransformError(Exception):
    """
    Error raised upon encountering a known error while attempting to transform
    the tree.
    """


class TornadoAsyncTransformer(cst.CSTTransformer):
    """
    A libcst transformer that replaces the legacy @gen.coroutine/yield
    async syntax with the python3.7 native async/await syntax.

    This transformer doesn't remove any tornado imports from modified
    files.
    """

    # TODO: @tornado.gen.coroutine, @tornado.gen.Return

    def __init__(self) -> None:
        self.coroutine_stack: List[bool] = []
        self.required_imports: Set[str] = set()

    def leave_Module(self, node: cst.Module, updated_node: cst.Module) -> cst.Module:
        if not self.required_imports:
            return updated_node

        imports = [
            self.make_simple_package_import(required_import)
            for required_import in self.required_imports
        ]

        return with_added_imports(updated_node, imports)

    def visit_Call(self, node: cst.Call) -> Optional[bool]:
        if self.is_gen_task_call(node):
            raise TransformError(
                "gen.Task (https://www.tornadoweb.org/en/branch2.4/gen.html#tornado.gen.Task) from tornado 2.4.1 is unsupported by this codemod. This file has not been modified. Manually update to supported syntax before running again."
            )

        return True

    def leave_Call(self, node: cst.Call, updated_node: cst.Call) -> cst.Call:
        if not self.in_coroutine(self.coroutine_stack):
            return updated_node

        if self.is_gen_sleep_call(updated_node):
            self.required_imports.add("asyncio")
            return updated_node.with_changes(
                func=cst.Attribute(value=cst.Name("asyncio"), attr=cst.Name("sleep"))
            )

        return updated_node

    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        self.coroutine_stack.append(self.is_coroutine(node))
        # always continue to visit function
        return True

    def leave_FunctionDef(
        self, node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        leaving_coroutine = self.coroutine_stack.pop()
        if not leaving_coroutine:
            return updated_node

        return updated_node.with_changes(
            decorators=[
                decorator
                for decorator in updated_node.decorators
                if not self.is_coroutine_decorator(decorator)
            ],
            asynchronous=cst.Asynchronous(),
        )

    def leave_Raise(
        self, node: cst.Raise, updated_node: cst.Raise
    ) -> Union[cst.Return, cst.Raise]:
        if not self.in_coroutine(self.coroutine_stack):
            return updated_node

        if not self.is_gen_return(updated_node):
            return updated_node

        return_value, whitespace_after = self.pluck_gen_return_value(updated_node)
        return cst.Return(
            value=return_value,
            whitespace_after_return=whitespace_after,
            semicolon=updated_node.semicolon,
        )

    def leave_Yield(
        self, node: cst.Yield, updated_node: cst.Yield
    ) -> Union[cst.Await, cst.Yield]:
        if not self.in_coroutine(self.coroutine_stack):
            return updated_node

        if not isinstance(updated_node.value, cst.BaseExpression):
            return updated_node

        if isinstance(updated_node.value, (cst.List, cst.ListComp)):
            self.required_imports.add("asyncio")
            expression = self.pluck_asyncio_gather_expression_from_yield_list_or_list_comp(
                updated_node
            )

        elif isinstance(updated_node.value, (cst.Dict, cst.DictComp)):
            raise TransformError(
                "Yielding a dict of futures (https://www.tornadoweb.org/en/branch3.2/releases/v3.2.0.html#tornado-gen) added in tornado 3.2 is unsupported by the codemod. This file has not been modified. Manually update to supported syntax before running again."
            )

        elif isinstance(updated_node.value, cst.Call):
            if name_or_attribute_matches(updated_node.value.func, ["dict"]):
                raise TransformError(
                    "Yielding a dict of futures (https://www.tornadoweb.org/en/branch3.2/releases/v3.2.0.html#tornado-gen) added in tornado 3.2 is unsupported by the codemod. This file has not been modified. Manually update to supported syntax before running again."
                )
            expression = updated_node.value

        else:
            expression = updated_node.value

        return cst.Await(
            expression=expression,
            whitespace_after_await=updated_node.whitespace_after_yield,
            lpar=updated_node.lpar,
            rpar=updated_node.rpar,
        )

    @staticmethod
    def is_gen_sleep_call(node: cst.Call) -> bool:
        if name_or_attribute_matches(node.func, ["gen", "sleep"]):
            return True

        return False

    @staticmethod
    def pluck_asyncio_gather_expression_from_yield_list_or_list_comp(
        node: cst.Yield
    ) -> cst.BaseExpression:
        return cst.Call(
            func=cst.Attribute(value=cst.Name("asyncio"), attr=cst.Name("gather")),
            args=[cst.Arg(value=node.value, star="*")],
        )

    @staticmethod
    def is_gen_task_call(node: cst.Call) -> bool:
        if name_or_attribute_matches(node.func, ["gen", "Task"]):
            return True

        return False

    @staticmethod
    def in_coroutine(coroutine_stack: List[bool]) -> bool:
        if not coroutine_stack:
            return False

        return coroutine_stack[-1]

    @staticmethod
    def pluck_gen_return_value(
        node: cst.Raise
    ) -> Tuple[Union[cst.BaseExpression, None], cst.SimpleWhitespace]:
        if TornadoAsyncTransformer.is_gen_return_call(node) and len(node.exc.args):
            return node.exc.args[0].value, node.whitespace_after_raise

        # if there's no return value, we don't preserve whitespace after 'raise'
        return None, cst.SimpleWhitespace("")

    @staticmethod
    def is_gen_return(node: cst.Raise) -> bool:
        return TornadoAsyncTransformer.is_gen_return_call(
            node
        ) or TornadoAsyncTransformer.is_gen_return_statement(node)

    @staticmethod
    def is_gen_return_statement(node: cst.Raise) -> bool:
        return name_or_attribute_matches_one_of(
            node.exc, [["tornado", "gen", "Return"], ["gen", "Return"], ["Return"]]
        )

    @staticmethod
    def is_gen_return_call(node: cst.Raise) -> bool:
        if not isinstance(node.exc, cst.Call):
            return False

        return name_or_attribute_matches_one_of(
            node.exc.func, [["tornado", "gen", "Return"], ["gen", "Return"], ["Return"]]
        )

    @staticmethod
    def is_coroutine_decorator(decorator: cst.Decorator) -> bool:
        return name_or_attribute_matches_one_of(
            decorator.decorator,
            [["tornado", "gen", "coroutine"], ["gen", "coroutine"], ["coroutine"]],
        )

    @staticmethod
    def is_coroutine(function_def: cst.FunctionDef) -> bool:
        return any(
            (
                TornadoAsyncTransformer.is_coroutine_decorator(decorator)
                for decorator in function_def.decorators
            )
        )

    @staticmethod
    def make_simple_package_import(package: str) -> cst.Import:
        assert not "." in package, "this only supports a root package, e.g. 'import os'"
        return cst.Import(names=[cst.ImportAlias(name=cst.Name(package))])
