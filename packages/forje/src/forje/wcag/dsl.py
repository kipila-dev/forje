from forje.dsl import Module

__all__ = ["module"]

module = Module(name="wcag").export_starlark(package=__name__, resource_name="dsl.star")
