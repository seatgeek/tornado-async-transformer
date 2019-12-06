from functools import singledispatch
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
    return m.matches(line, m.SimpleStatementLine(body=[m.Import() | m.ImportFrom()]))


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
    Attribute(value=Attribute(value=Name(value='tornado',...), attr=Name(value='gen',...),...), attr=Name(value='coroutine',...),...)
    """

    def _make_name_or_attribute(parts: List[str]) -> Union[m.Name, m.Attribute]:
        if not parts:
            raise RuntimeError("Expected a non empty list of strings")

        # just a name, e.g. `coroutine`
        if len(parts) == 1:
            return m.Name(parts[0])

        # a name and attribute, e.g. `gen.coroutine`
        if len(parts) == 2:
            return m.Attribute(value=m.Name(parts[0]), attr=m.Name(parts[1]))

        # a complex attribute, e.g. `tornado.gen.coroutine`, we want to make
        # the attribute with value `tornado.gen` and attr `coroutine`
        value = _make_name_or_attribute(parts[:-1])
        attr = _make_name_or_attribute(parts[-1:])
        assert isinstance(attr, m.Name)
        return m.Attribute(value=value, attr=attr)

    parts = tag.split(".")
    return [_make_name_or_attribute(parts[start:]) for start in range(len(parts))]


def some_version_of(tag: str) -> m.OneOf[m.Union[m.Name, m.Attribute]]:
    """
    Poorly named wrapper around name_attr_possibilities.
    """
    return m.OneOf(*name_attr_possibilities(tag))
