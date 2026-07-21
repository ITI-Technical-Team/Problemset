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

@check50.check(has_blocks)
def has_sprites():
    """project contains at least one sprite"""
    project = scratch_helper.get_project()
    if scratch_helper.count_sprites(project) < 1:
        raise check50.Failure("Did not find any sprites in the project.")

@check50.check(valid_sb3)
def has_even_initialization():
    """variable is initialized to an even starting number (e.g. 0 or 2)"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    found_even_set = False
    found_odd_set = False

    for b_id, b in blocks.items():
        if b.get("opcode") == "data_setvariableto":
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                val_str = scratch_helper.get_block_input_value(b, "VALUE", blocks)
                if val_str is not None:
                    try:
                        val = int(float(val_str))
                        if val % 2 == 0:
                            found_even_set = True
                        else:
                            found_odd_set = True
                    except ValueError:
                        pass

    if found_odd_set and not found_even_set:
        raise check50.Failure(
            "Variable initialized to an odd number.",
            help="To count even numbers (2, 4, 6...), initialize your variable to an even number like 0 or 2, not an odd number."
        )
    if not found_even_set:
        raise check50.Failure(
            "Did not find variable initialization (set number to 0 or 2).",
            help="Use 'set [number] to [2]' attached under 'when green flag clicked' before starting the counting loop."
        )

@check50.check(has_even_initialization)
def has_counting_loop():
    """loop is attached to green flag and contains say and increment blocks"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    loop_opcodes = ["control_repeat", "control_repeat_until", "control_forever"]
    valid_loop_found = False

    for b_id, b in blocks.items():
        if b.get("opcode") in loop_opcodes:
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                has_say = False
                has_change = False

                inputs = b.get("inputs", {})
                if "SUBSTACK" in inputs:
                    sub_first = scratch_helper.get_block_input_value(b, "SUBSTACK", blocks)
                    if sub_first and sub_first in blocks:
                        curr = sub_first
                        visited = set()
                        while curr and curr in blocks and curr not in visited:
                            visited.add(curr)
                            cb = blocks[curr]
                            op = cb.get("opcode", "")
                            if op in ("looks_say", "looks_sayforsecs"):
                                has_say = True
                            if op in ("data_changevariableby", "data_setvariableto"):
                                has_change = True
                            curr = cb.get("next")

                if has_say and has_change:
                    valid_loop_found = True
                    break

    if not valid_loop_found:
        raise check50.Failure(
            "Counting loop is missing say or variable increment blocks.",
            help="Inside your repeat loop, make sure to include: (1) a say block to speak the number, and (2) a 'change [number] by [2]' block to increment."
        )

@check50.check(has_counting_loop)
def count_limit():
    """repeat loop counts up to 100 (e.g. repeat 50 times)"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    for b_id, b in blocks.items():
        if b.get("opcode") == "control_repeat":
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                times_str = scratch_helper.get_block_input_value(b, "TIMES", blocks)
                if times_str is not None:
                    try:
                        times = int(float(times_str))
                        if times > 60:
                            raise check50.Failure(
                                f"Repeat count is too high ({times} times).",
                                help="If incrementing by 2, repeating 50 times reaches 100. Repeating 100 times would count up to 200!"
                            )
                        elif times < 40 and times != 0:
                            raise check50.Failure(
                                f"Repeat count is too low ({times} times).",
                                help="To count even numbers up to 100 (incrementing by 2), repeat 50 times."
                            )
                    except ValueError:
                        pass
