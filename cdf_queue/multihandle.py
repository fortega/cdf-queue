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


class IsActiveMethod:
    @abstractmethod
    def is_active(self, handle_arg: HandleArg) -> bool:
        "returns True if handle should run"
        pass


class AlwaysActiveMethod(IsActiveMethod):
    def is_active(self, handle_arg: HandleArg) -> bool:
        return True


class FlagActiveMethod(IsActiveMethod):
    def __init__(
            self,
            active_flag: str,
    ):
        self.active_flag = active_flag

    def is_active(self, handle_arg: HandleArg) -> bool:
        result = handle_arg.data.get(self.active_flag, False)
        return bool(result)


class ErrorListMethod:
    @abstractmethod
    def error_list(self, handle_arg: HandleArg) -> List[str]:
        "validate handle data and return list of errors"
        pass


class NoErrorListMethod(ErrorListMethod):
    def error_list(self, handle_arg: HandleArg) -> List[str]:
        return []


class RequiredErrorListMethod(ErrorListMethod):
    def __init__(
            self,
            required_list: List[str],
    ):
        self.required_list = required_list

    def error_list(self, handle_arg: HandleArg) -> List[str]:
        not_found_message = [
            f"not found {required}"
            for required in self.required_list
            if (required not in handle_arg.data.keys()) | (handle_arg.data[required] == None)
        ]
        return not_found_message


class HandleMethod(Callable[[HandleArg], HandleData]):
    @abstractmethod
    def handle(self, handle_arg: HandleArg) -> HandleData:
        "handle client request"
        pass

    def __call__(self, handle_arg: HandleArg) -> HandleData:
        return self.handle(handle_arg)


class DebugHandleMethod(HandleMethod):
    def handle(self, handle_arg: HandleArg) -> HandleData:
        result = {
            "data": handle_arg.data,
            "function_call_info": handle_arg.function_call_info,
            "secrets_keys": handle_arg.secrets.keys() if isinstance(handle_arg.secrets, Dict) else {},
        }
        return result


class HandleRule(IsActiveMethod, ErrorListMethod, HandleMethod):
    pass


class DebugRule(AlwaysActiveMethod, NoErrorListMethod, DebugHandleMethod):
    pass


class FlagActiveRequiredList(FlagActiveMethod, RequiredErrorListMethod, HandleMethod):
    def __init__(
            self,
            f: Callable[[HandleArg], HandleData],
            active_flag: str = None,
            required_list: List[str] = None,
    ):
        self.f = f
        self.required_list = required_list
        self.active_flag = active_flag

    def handle(self, handle_arg: HandleArg) -> HandleData:
        result = self.f(handle_arg)
        return result


def flag_active_required_list(
    active_flag: str,
    required_list: List[str],
) -> HandleRule:
    def op(f: Callable[[HandleArg], HandleData]):
        result = FlagActiveRequiredList(
            f=f,
            active_flag=active_flag,
            required_list=required_list,
        )
        return result
    return op
