from typing import List, Optional, Tuple, Union, Set

import libcst as cst

from tornado_native_async_transformer.helpers import with_added_imports


class TransformError(Exception):
    """
    Error raised upon encountering a known error while attempting to transform
    the tree.
    """


class TornadoNativeAsyncTransformer(cst.CSTTransformer):
    """
    A libcst transformer that replaces the legacy @gen.coroutine/yield
    async syntax with the python3.7 native async/await syntax.

    This transformer doesn't remove any tornado imports from modified
    files.
    """

    # TODO: @tornado.gen.coroutine, @tornado.gen.Return
    # TODO: gen.sleep

    def __init__(self):
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
                for decorator in node.decorators
                if not self.is_coroutine_decorator(decorator)
            ],
            asynchronous=cst.Asynchronous(),
        )

    def leave_Raise(
        self, node: cst.Raise, updated_node: cst.Raise
    ) -> Union[cst.Return, cst.Raise]:
        if not self.in_coroutine(self.coroutine_stack):
            return updated_node

        if not self.is_gen_return(node):
            return updated_node

        return_value, whitespace_after = self.pluck_gen_return_value(node)
        return cst.Return(
            value=return_value,
            whitespace_after_return=whitespace_after,
            semicolon=node.semicolon,
        )

    def leave_Yield(
        self, node: cst.Yield, updated_node: cst.Yield
    ) -> Union[cst.Await, cst.Yield]:
        if not self.in_coroutine(self.coroutine_stack):
            return updated_node

        if not isinstance(node.value, cst.BaseExpression):
            return updated_node

        if isinstance(node.value, (cst.List, cst.ListComp)):
            self.required_imports.add("asyncio")
            expression = self.pluck_asyncio_gather_expression_from_yield_list_or_list_comp(
                node
            )

        elif isinstance(node.value, (cst.Dict, cst.DictComp)):
            raise TransformError(
                "Yielding a dict of futures (https://www.tornadoweb.org/en/branch3.2/releases/v3.2.0.html#tornado-gen) added in tornado 3.2 is unsupported by the codemod. This file has not been modified. Manually update to supported syntax before running again."
            )

        elif isinstance(node.value, cst.Call):
            if (
                isinstance(node.value.func, cst.Name)
                and node.value.func.value == "dict"
            ):
                raise TransformError(
                    "Yielding a dict of futures (https://www.tornadoweb.org/en/branch3.2/releases/v3.2.0.html#tornado-gen) added in tornado 3.2 is unsupported by the codemod. This file has not been modified. Manually update to supported syntax before running again."
                )
            expression = node.value

        else:
            expression = node.value

        return cst.Await(
            expression=expression,
            whitespace_after_await=node.whitespace_after_yield,
            lpar=node.lpar,
            rpar=node.rpar,
        )

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
        if (
            isinstance(node.func, cst.Attribute)
            and isinstance(node.func.value, cst.Name)
            and node.func.value.value == "gen"
            and node.func.attr.value == "Task"
        ):
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
        if TornadoNativeAsyncTransformer.is_gen_return_call(node) and len(
            node.exc.args
        ):
            return node.exc.args[0].value, node.whitespace_after_raise

        # if there's no return value, we don't preserve whitespace after 'raise'
        return None, cst.SimpleWhitespace("")

    @staticmethod
    def is_gen_return(node: cst.Raise) -> bool:
        is_gen_return_checks = [
            TornadoNativeAsyncTransformer.is_gen_return_call,
            TornadoNativeAsyncTransformer.is_gen_return_statement,
        ]
        return any(
            is_gen_return_check(node) for is_gen_return_check in is_gen_return_checks
        )

    @staticmethod
    def is_gen_return_statement(node: cst.Raise) -> bool:
        if not isinstance(node.exc, cst.Attribute):
            return False

        return node.exc.value.value == "gen" and node.exc.attr.value == "Return"

    @staticmethod
    def is_gen_return_call(node: cst.Raise) -> bool:
        if not isinstance(node.exc, cst.Call):
            return False

        # raise gen.Return()
        if (
            isinstance(node.exc.func, cst.Attribute)
            and node.exc.func.value.value == "gen"
            and node.exc.func.attr.value == "Return"
        ):
            return True

        # raise Return()
        if isinstance(node.exc.func, cst.Name) and node.exc.func.value == "Return":
            return True

        return False

    @staticmethod
    def is_coroutine_decorator(decorator: cst.Decorator) -> bool:
        # @gen.coroutine
        if (
            isinstance(decorator.decorator, cst.Attribute)
            and decorator.decorator.value.value == "gen"
            and decorator.decorator.attr.value == "coroutine"
        ):
            return True

        # @coroutine
        if (
            isinstance(decorator.decorator, cst.Name)
            and decorator.decorator.value == "coroutine"
        ):
            return True

        return False

    @staticmethod
    def is_coroutine(function_def: cst.FunctionDef) -> bool:
        return any(
            (
                TornadoNativeAsyncTransformer.is_coroutine_decorator(decorator)
                for decorator in function_def.decorators
            )
        )

    @staticmethod
    def make_simple_package_import(package: str) -> cst.Import:
        assert not "." in package, "this only supports a root package, e.g. 'import os'"
        return cst.Import(names=[cst.ImportAlias(name=cst.Name(package))])
