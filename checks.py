import typing as t
T = t.TypeVar("T")
def check_type(variable: T,
               variable_name: str,
               required_type: t.Union[type, t._UnionGenericAlias]) -> None:
    if not isinstance(variable, required_type):
        raise TypeError(
            f"'{variable_name}' should be of type "
            f"{required_type}, not {type(variable)}"
        )