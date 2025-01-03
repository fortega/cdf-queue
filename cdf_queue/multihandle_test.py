from multihandle import default_debug_rule, HandleArg, HandleData, flag_required_rule, RuleErrorFound, NoActiveRule, multi_rule_handle, debug_handle
from pytest import raises


def test_debug_rule():
    rule = default_debug_rule
    handle_arg = HandleArg(
        client=None
    )
    error_list = rule.error_list(handle_arg)
    assert len(error_list) == 0, f"Error not expected: {error_list}"

    is_active = rule.is_active(handle_arg)
    assert is_active, "Debug should be always active"

    result = rule.handle(handle_arg)

    assert list(result.keys()) == ['data', "function_call_info", "secrets_key"]


def test_flag_active_required_list():

    @flag_required_rule(flag="flag1", required=["name"])
    def rule(handle_arg: HandleArg) -> HandleData:
        return {}

    handle_arg = HandleArg(
        client=None,
        data={"flag1": True, "name": "None"}
    )

    error_list = rule.error_list(handle_arg)
    assert len(error_list) == 0, f"Error not expected: {error_list}"

    is_active = rule.is_active(handle_arg)
    assert is_active, "Debug should be always active"

    result = rule.handle(handle_arg)

    assert result == {}


def test_multi_handle():
    handle_arg = HandleArg(
        client=None,
        data={"flag1": True, "name": None}
    )

    with raises(NoActiveRule):
        multi_rule_handle(
            handle_arg=handle_arg
        )

    flag2_required_rule_debug = flag_required_rule(
        flag="flag2", required=["name"])(debug_handle)
    with raises(NoActiveRule):
        multi_rule_handle(
            flag2_required_rule_debug,
            handle_arg=handle_arg
        )

    flag1_required_rule_debug = flag_required_rule(
        flag="flag1", required=["name"])(debug_handle)
    with raises(RuleErrorFound):
        multi_rule_handle(
            flag1_required_rule_debug,
            handle_arg=handle_arg,
        )
