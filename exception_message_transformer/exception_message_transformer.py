from typing import List, Optional

import libcst as cst


class TransformError(Exception):
    """
    Error raised upon encountering a known error while attempting to transform
    the tree.
    """


class ExceptionMessageTransformer(cst.CSTTransformer):
    """
    Transform e.message to str(e).
    """

    def __init__(self) -> None:
        self.except_name_stack: List[Optional[str]] = []

    def visit_ExceptHandler(self, node: cst.ExceptHandler) -> bool:
        if isinstance(node.name, cst.AsName):
            # I believe an exception AsName can only be name, not a tuple or a list
            if not isinstance(node.name.name, cst.Name):
                raise TransformError(
                    f"Expected ExceptHandler.name.name to be a cst.Name, but is a {type(node.name.name)}"
                )

            self.except_name_stack.append(node.name.name.value)

        else:
            self.except_name_stack.append(None)

        return True

    def leave_ExceptHandler(
        self, node: cst.ExceptHandler, updated_node: cst.ExceptHandler
    ) -> cst.ExceptHandler:
        self.except_name_stack.pop()
        return updated_node

    def leave_Attribute(
        self, node: cst.Attribute, updated_node: cst.Attribute
    ) -> cst.Call:
        if not self.except_name_stack:
            return updated_node

        if not isinstance(node.value, cst.Name) or not isinstance(node.attr, cst.Name):
            return updated_node

        if node.attr.value == "message" and node.value.value in self.except_name_stack:
            return cst.Call(func=cst.Name("str"), args=[cst.Arg(value=node.value)])

        return updated_node
