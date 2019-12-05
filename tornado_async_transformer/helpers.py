from functools import singledispatch
from typing import List, Sequence, Union

import libcst as cst


def with_added_imports(
    module_node: cst.Module, import_nodes: Sequence[Union[cst.Import, cst.ImportFrom]]
) -> cst.Module:
    """
    Adds new import `import_node` after the first import in the module `module_node`.
    """
    updated_body: List[Union[cst.SimpleStatementLine, cst.BaseCompoundStatement]] = []
    added_import = False
    for line in module_node.body:
        updated_body.append(line)
        if not added_import and _is_import_line(line):
            for import_node in import_nodes:
                updated_body.append(cst.SimpleStatementLine(body=tuple([import_node])))
            added_import = True

    if not added_import:
        raise RuntimeError("Failed to add imports")

    return module_node.with_changes(body=tuple(updated_body))


def _is_import_line(
    line: Union[cst.SimpleStatementLine, cst.BaseCompoundStatement]
) -> bool:
    return (
        isinstance(line, cst.SimpleStatementLine)
        and len(line.body) == 1
        and isinstance(line.body[0], (cst.Import, cst.ImportFrom))
    )


def name_or_attribute_matches_one_of(
    node: cst.BaseExpression, parts_options: Sequence[Sequence[str]]
) -> bool:
    return any(name_or_attribute_matches(node, parts) for parts in parts_options)


@singledispatch
def name_or_attribute_matches(node: cst.BaseExpression, parts: Sequence[str]) -> bool:
    """
    Returns true of a Name or Attribute node matches some list of parts, such
    as "tornado.gen.coroutine." Returns False if node isn't a Name or Attribute.
    """
    return False


@name_or_attribute_matches.register(cst.Name)
def name_matches(node: cst.Name, parts: Sequence[str]) -> bool:
    if not len(parts) == 1:
        return False

    return bool(node.value == parts[0])


@name_or_attribute_matches.register(cst.Attribute)
def attribute_matches(node: cst.Attribute, parts: Sequence[str]) -> bool:
    if not len(parts) >= 2:
        return False

    if not name_or_attribute_matches(node.attr, parts[-1:]):
        return False

    return name_or_attribute_matches(node.value, parts[:-1])
