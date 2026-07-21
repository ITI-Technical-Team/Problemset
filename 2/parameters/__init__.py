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
def has_custom_block():
    """project defines a custom block (function)"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.check_custom_block(blocks):
        raise check50.Failure("Did not find any custom blocks (functions).", help="Create a custom block using 'Make a Block' under My Blocks.")

@check50.check(has_custom_block)
def custom_block_has_single_number_input():
    """custom block accepts exactly one number/text input parameter (n)"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    has_num_arg = scratch_helper.has_opcode(blocks, "argument_reporter_string_number")
    has_bool_arg = scratch_helper.has_opcode(blocks, "argument_reporter_boolean")

    if has_bool_arg and not has_num_arg:
        raise check50.Failure(
            "Custom block parameter is a Boolean input, expected Number/Text.",
            help="When creating your custom block parameter, choose 'Add an input (number or text)', not a boolean input."
        )

    if not has_num_arg:
        raise check50.Failure(
            "Custom block does not accept a number/text input parameter.",
            help="Add a number/text input parameter 'n' when creating your custom block."
        )

    # Check number of arguments in prototype
    for b_id, b in blocks.items():
        if b.get("opcode") == "procedures_prototype":
            mut = b.get("mutation", {})
            proccode = mut.get("proccode", "")
            # proccode contains placeholders like %s for string/number, %b for boolean
            args = mut.get("argumentnames", "[]")
            if proccode.count("%s") + proccode.count("%b") > 1:
                raise check50.Failure(
                    "Custom block has too many parameters.",
                    help="Custom block should take exactly one input parameter (n)."
                )

@check50.check(custom_block_has_single_number_input)
def custom_block_uses_param_and_waits():
    """custom block uses parameter n in move steps and waits 1 second"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    uses_param_in_move = False
    has_wait_1 = False

    for b_id, b in blocks.items():
        if b.get("opcode") == "procedures_definition":
            # Traverse blocks under define
            curr = b.get("next")
            visited = set()
            while curr and curr in blocks and curr not in visited:
                visited.add(curr)
                cb = blocks[curr]
                op = cb.get("opcode", "")
                if op == "motion_movesteps":
                    # Check STEPS input
                    steps_input = cb.get("inputs", {}).get("STEPS")
                    if isinstance(steps_input, list) and len(steps_input) >= 2:
                        input_block_id = steps_input[1]
                        if isinstance(input_block_id, str) and input_block_id in blocks:
                            arg_block = blocks[input_block_id]
                            if arg_block.get("opcode") == "argument_reporter_string_number":
                                uses_param_in_move = True
                if op == "control_wait":
                    dur = scratch_helper.get_block_input_value(cb, "DURATION", blocks)
                    if dur and str(dur).strip() == "1":
                        has_wait_1 = True
                curr = cb.get("next")

    if not uses_param_in_move:
        raise check50.Failure(
            "Custom block does not use parameter (n) in 'move steps'.",
            help="Drag your parameter block 'n' from the 'define' header into the 'move [n] steps' block."
        )

    if not has_wait_1:
        raise check50.Failure(
            "Custom block is missing 'wait 1 seconds'.",
            help="Attach a 'wait 1 seconds' block inside your custom block definition."
        )

@check50.check(has_custom_block)
def calls_custom_block_with_argument():
    """custom block is called with an argument from an event script"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    called_with_arg = False

    for b_id, b in blocks.items():
        if b.get("opcode") == "procedures_call":
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                inputs = b.get("inputs", {})
                # Check if any input in call has a non-empty value
                for key, val in inputs.items():
                    val_str = scratch_helper.get_block_input_value(b, key, blocks)
                    if val_str and str(val_str).strip() != "":
                        called_with_arg = True
                        break

    if not called_with_arg:
        raise check50.Failure(
            "Custom block call is missing an argument value.",
            help="When calling your custom block (e.g. under 'when green flag clicked'), pass a number (like 10) in the input slot."
        )
