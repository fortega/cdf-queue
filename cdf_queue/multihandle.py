from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from cognite.client import CogniteClient

HandleData = Dict[str, Any]


@dataclass
class HandleArg:
    client: CogniteClient
    data: Optional[HandleData] = None
    secrets: Optional[HandleData] = None
    function_call_info: Optional[HandleData] = None


IsActiveFunction = Callable[[HandleArg], bool]
ErrorListFunction = Callable[[HandleArg], List[str]]
HandleFunction = Callable[[HandleArg], HandleData]


@dataclass
class HandleRule:
    is_active: IsActiveFunction
    error_list: ErrorListFunction
    handle: HandleFunction


def always_is_active(_): return True
def empty_error_list(_): return []


def default_rule(handle: HandleFunction) -> HandleRule:
    result = HandleRule(
        is_active=always_is_active,
        error_list=empty_error_list,
        handle=handle
    )
    return result


def flag_is_active(flag: str) -> IsActiveFunction:
    def op(handle_arg: HandleArg) -> bool:
        result = handle_arg.data.get(flag, False)
        return bool(result)
    return op


def required_error_list(required: List[str]) -> ErrorListFunction:
    def op(handle_arg: HandleArg) -> List[str]:
        not_found_message = [
            f"not found {key}"
            for key in required
            if (key not in handle_arg.data.keys()) | (handle_arg.data[key] == None)
        ]
        return not_found_message
    return op


def flag_required_rule(
        flag: str,
        required: List[str],
) -> Callable[[HandleFunction], HandleRule]:
    def deco(handle: HandleFunction) -> HandleRule:
        is_active = flag_is_active(flag=flag)
        error_list = required_error_list(required)
        result = HandleRule(
            is_active=is_active,
            error_list=error_list,
            handle=handle,
        )
        return result

    return deco


def debug_handle(handle_arg: HandleArg) -> HandleData:
    result = {
        "data": handle_arg.data,
        "function_call_info": handle_arg.function_call_info,
        "secrets_key": handle_arg.secrets.keys() if isinstance(handle_arg.secrets, Dict) else {},
    }
    return result


default_debug_rule = default_rule(debug_handle)

NoActiveRule = Exception
RuleErrorFound = Exception


def multi_rule_handle(*rules: HandleRule, handle_arg: HandleArg) -> HandleData:
    for rule in rules:
        if rule.is_active(handle_arg):
            error_list = rule.error_list(handle_arg)
            if len(error_list) == 0:
                result = rule.handle(HandleData)
                return result
            else:
                raise RuleErrorFound(*error_list)
        else:
            continue
    raise NoActiveRule("no active rule")
