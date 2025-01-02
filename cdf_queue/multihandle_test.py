from multihandle import DebugRule, HandleArg, HandleData, flag_active_required_list

def test_debug_rule():
    rule = DebugRule()
    handle_arg = HandleArg(
        client=None
    )
    error_list = rule.error_list(handle_arg)
    assert len(error_list) == 0, f"Error not expected: {error_list}"

    is_active = rule.is_active(handle_arg)
    assert is_active, "Debug should be always active"

    result = rule.handle(handle_arg)

    print(error_list, is_active, result)


def test_flag_active_required_list():

    @flag_active_required_list(active_flag="flag1", required_list=["name"])
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
    
    
