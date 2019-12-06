from functools import reduce, singledispatch
from typing import List, Sequence, Union

import libcst as cst
from libcst import matchers as m


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


def name_attr_possibilities(tag: str) -> List[Union[m.Name, m.Attribute]]:
    """
    Let's say we want to find all instances of coroutine decorators in our code. The torando coroutine
    decorator can be imported and used in the following ways:

    ```
    import tornado; @tornado.gen.coroutine
    from tornado import gen; @gen.coroutine
    from tornado.gen import coroutine; @coroutine
    ```

    If we want to see if a decorator is a coroutine decorator, and we don't want the overhead of knowing
    all of the module's imports, we can check if a decorator matches one of the following options to be
    fairly confident it's a coroutine:
    - tornado.gen.coroutine
    - gen.coroutine
    - coroutine

    This doesn't account for renamed imports (since we're not import aware) but does a decent enough job.
    Another option is to only match against the final Name in a Name, Attribute or nested Attribute, but
    there doesn't seem to be a majorly simpler way to do that atm with libcst and this way we get some
    extra protection from considering @this.is.not.a.coroutine a match for @tornado.gen.coroutine.

    # We run this function on "tornado.gen.coroutine"
    >>> tornado_gen_coroutine, gen_coroutine, coroutine = name_attr_possibilities("tornado.gen.coroutine")

    # We have just the matcher Name "coroutine"
    >>> coroutine
    Name(value='coroutine',...)

    # We have an attribute "gen.coroutine"
    >>> gen_coroutine
    Attribute(value=Name(value='gen',...), attr=Name(value='coroutine',...),...)

    # We have a nested attribute "tornado.gen.coroutine"
    >>> tornado_gen_coroutine
    Attribute(value=Name(value='tornado',...), attr=Attribute(value=Name(value='gen',...), attr=Name(value='coroutine',...),...))
    """
    def reducer(accumulator: List[Union[m.Name, m.Attribute]], current: str) -> List[Union[m.Name, m.Attribute]]:
        if not accumulator:
            return [m.Name(current)]

        return [m.Attribute(value=m.Name(current), attr=accumulator[0])] + accumulator

    return reduce(reducer, reversed(tag.split(".")), [])
