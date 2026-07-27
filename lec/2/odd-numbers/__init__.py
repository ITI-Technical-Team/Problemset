import check50
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import scratch_helper


@check50.check()
def exists():
    """project.sb3 exists"""
    import glob
    if not glob.glob("*.sb3"):
        raise check50.Failure("No .sb3 file found.")


@check50.check(exists)
def valid_sb3():
    """file is a valid Scratch project"""
    try:
        scratch_helper.get_project()
    except Exception as e:
        raise check50.Failure("Could not read project.sb3. Make sure it is a valid Scratch file.")


@check50.check(valid_sb3)
def has_blocks():
    """project contains code blocks"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if len(blocks) < 1:
        raise check50.Failure("Project seems empty (no blocks found).")


@check50.check(valid_sb3)
def set_is_outside_loop():
    """variable is initialized BEFORE (outside) the repeat loop, not inside it"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    loop_opcodes = {"control_repeat", "control_repeat_until", "control_forever"}

    def get_all_inside_block_ids(container_block_id):
        """Walk all blocks nested inside a container block."""
        inside = set()
        container = blocks.get(container_block_id)
        if not container:
            return inside
        for key in ("SUBSTACK", "SUBSTACK2"):
            inp = container.get("inputs", {}).get(key)
            if not inp:
                continue
            curr = inp[1] if isinstance(inp[1], str) else None
            visited = set()
            while curr and curr in blocks and curr not in visited:
                visited.add(curr)
                inside.add(curr)
                cb = blocks[curr]
                for nested_key in ("SUBSTACK", "SUBSTACK2"):
                    nested_inp = cb.get("inputs", {}).get(nested_key)
                    if nested_inp and isinstance(nested_inp[1], str):
                        inside |= get_all_inside_block_ids(curr)
                curr = cb.get("next")
        return inside

    for b_id, b in blocks.items():
        if b.get("opcode") in loop_opcodes:
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                inside_ids = get_all_inside_block_ids(b_id)
                for inner_id in inside_ids:
                    inner_block = blocks.get(inner_id, {})
                    if inner_block.get("opcode") == "data_setvariableto":
                        raise check50.Failure(
                            "Variable initialization (set block) is inside the repeat loop.",
                            help="Move the 'set [oddNumber] to [1]' block to BEFORE the repeat loop. If it is inside, the variable resets to 1 on every iteration and the sprite will say 1 five times instead of odd numbers."
                        )


@check50.check(valid_sb3)
def has_repeat_loop():
    """project contains a repeat loop connected to an event block"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    loop_opcodes = ["control_repeat", "control_repeat_until", "control_forever"]
    for b_id, b in blocks.items():
        if b.get("opcode") in loop_opcodes:
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                return
    raise check50.Failure(
        "Counting loop is missing.",
        help="Add a 'repeat [5]' loop connected under the green flag to count the 5 odd numbers."
    )


@check50.check(valid_sb3)
def has_variable_initialization():
    """project initializes a variable before the loop"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    for b_id, b in blocks.items():
        if b.get("opcode") == "data_setvariableto":
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                return
    raise check50.Failure(
        "Did not find variable initialization.",
        help="Use 'set [oddNumber] to [1]' attached under the green flag event block, before the repeat loop."
    )


@check50.check(valid_sb3)
def initializes_to_one():
    """variable is initialized to 1 (first odd number)"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    for b_id, b in blocks.items():
        if b.get("opcode") == "data_setvariableto":
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                val_str = scratch_helper.get_block_input_value(b, "VALUE", blocks)
                if val_str is not None:
                    try:
                        val = int(float(val_str))
                        if val == 1:
                            return
                    except ValueError:
                        pass
    raise check50.Failure(
        "Variable is not initialized to 1.",
        help="Use 'set [oddNumber] to [1]' to start counting from the first odd number."
    )


@check50.check(valid_sb3)
def say_inside_loop():
    """say block is inside the loop"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    loop_opcodes = ["control_repeat", "control_repeat_until", "control_forever"]
    for b_id, b in blocks.items():
        if b.get("opcode") in loop_opcodes:
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                inputs = b.get("inputs", {})
                if "SUBSTACK" in inputs:
                    curr = scratch_helper.get_block_input_value(b, "SUBSTACK", blocks)
                    visited = set()
                    while curr and curr in blocks and curr not in visited:
                        visited.add(curr)
                        cb = blocks[curr]
                        if cb.get("opcode", "") in ("looks_say", "looks_sayforsecs"):
                            return
                        curr = cb.get("next")
    raise check50.Failure(
        "Missing say block inside the loop.",
        help="Put a 'say [oddNumber] for [1] seconds' block inside the repeat loop."
    )


@check50.check(valid_sb3)
def change_inside_loop():
    """variable increments by 2 inside the loop"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    loop_opcodes = ["control_repeat", "control_repeat_until", "control_forever"]
    for b_id, b in blocks.items():
        if b.get("opcode") in loop_opcodes:
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                inputs = b.get("inputs", {})
                if "SUBSTACK" in inputs:
                    curr = scratch_helper.get_block_input_value(b, "SUBSTACK", blocks)
                    visited = set()
                    while curr and curr in blocks and curr not in visited:
                        visited.add(curr)
                        cb = blocks[curr]
                        if cb.get("opcode", "") == "data_changevariableby":
                            val_str = scratch_helper.get_block_input_value(cb, "VALUE", blocks)
                            if val_str is not None:
                                try:
                                    val = int(float(val_str))
                                    if val == 2:
                                        return
                                    else:
                                        raise check50.Failure(
                                            f"Variable increments by {val} instead of 2.",
                                            help="Use 'change [oddNumber] by [2]' inside the loop to skip to the next odd number."
                                        )
                                except ValueError:
                                    pass
                        curr = cb.get("next")
    raise check50.Failure(
        "Missing 'change by 2' block inside the loop.",
        help="Put a 'change [oddNumber] by [2]' block inside the repeat loop to move to the next odd number."
    )


@check50.check(valid_sb3)
def repeat_five_times():
    """repeat loop runs exactly 5 times (for 5 odd numbers: 1, 3, 5, 7, 9)"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    for b_id, b in blocks.items():
        if b.get("opcode") == "control_repeat":
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                times_str = scratch_helper.get_block_input_value(b, "TIMES", blocks)
                if times_str is not None:
                    try:
                        times = int(float(times_str))
                        if times == 5:
                            return
                        else:
                            raise check50.Failure(
                                f"Repeat count is {times} instead of 5.",
                                help="Use 'repeat [5]' to say exactly 5 odd numbers: 1, 3, 5, 7, 9."
                            )
                    except ValueError:
                        pass
