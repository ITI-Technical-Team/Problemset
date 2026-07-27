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

def is_input_variable(block, input_name, blocks):
    inputs = block.get("inputs", {})
    if input_name not in inputs:
        return False
    val = inputs[input_name]
    if not isinstance(val, list) or len(val) < 2:
        return False
        
    # Case 1: Direct variable representation [12, "var_name", "var_id"]
    if val[0] == 12:
        return True
        
    # Case 2: Nested variable inside type 3: [3, [12, "var_name", "var_id"], [10, "default"]]
    if val[0] == 3 and isinstance(val[1], list) and len(val[1]) > 0 and val[1][0] == 12:
        return True
        
    # Case 3: Block reference [2, "block_id"] or [3, "block_id", ...]
    if val[0] in (2, 3):
        ref_id = val[1]
        if isinstance(ref_id, str):
            if ref_id in blocks:
                return blocks[ref_id].get("opcode") == "data_variable"
            # Fallback for dummy/corrupted files containing "var" in the ID
            if "var" in ref_id.lower():
                return True
                
    return False

@check50.check(valid_sb3)
def set_is_outside_loop():
    """variable is initialized BEFORE (outside) the repeat loop, not inside it"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    loop_opcodes = {"control_repeat", "control_repeat_until", "control_forever"}

    def get_all_inside_block_ids(container_block_id):
        """Walk all blocks nested inside a container block (loop/conditional)."""
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
                # Recurse into nested loops/conditionals
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
                            help="Move the 'set [variable] to [2]' block to BEFORE the repeat loop. If it's inside, the variable resets to 2 on every iteration and the sprite will say 2 fifty times instead of counting up."
                        )

@check50.check(valid_sb3)
def has_variable_initialization():
    """project initializes a variable"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    found_init = False
    for b_id, b in blocks.items():
        if b.get("opcode") == "data_setvariableto":
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                found_init = True
                break
    if not found_init:
        raise check50.Failure(
            "Did not find variable initialization.",
            help="Use 'set [variable] to [0]' (or [2]) attached under the green flag event block."
        )

@check50.check(valid_sb3)
def has_even_initialization():
    """variable is initialized to an even starting number (e.g. 0 or 2)"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    found_even_set = False
    found_odd_set = False
    found_set = False

    for b_id, b in blocks.items():
        if b.get("opcode") == "data_setvariableto":
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                found_set = True
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

    if not found_set:
        raise check50.Failure("Did not find variable initialization (set block).")
    if found_odd_set and not found_even_set:
        raise check50.Failure(
            "Variable initialized to an odd number.",
            help="To count even numbers (2, 4, 6...), initialize your variable to an even number like 0 or 2, not an odd number."
        )
    if not found_even_set:
        raise check50.Failure(
            "Variable is not initialized to an even number.",
            help="Use 'set [variable] to [0]' or [2] to start counting even numbers."
        )

@check50.check(valid_sb3)
def has_repeat_loop():
    """project contains a loop connected to an event block"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    loop_opcodes = ["control_repeat", "control_repeat_until", "control_forever"]
    found_loop = False
    for b_id, b in blocks.items():
        if b.get("opcode") in loop_opcodes:
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                found_loop = True
                break
    if not found_loop:
        raise check50.Failure(
            "Counting loop is missing.",
            help="Add a 'repeat [50]' loop connected under the green flag to run the counting process."
        )

@check50.check(valid_sb3)
def say_inside_loop():
    """say block is inside the loop"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    loop_opcodes = ["control_repeat", "control_repeat_until", "control_forever"]
    has_say = False
    for b_id, b in blocks.items():
        if b.get("opcode") in loop_opcodes:
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                inputs = b.get("inputs", {})
                if "SUBSTACK" in inputs:
                    sub_first = scratch_helper.get_block_input_value(b, "SUBSTACK", blocks)
                    curr = sub_first
                    visited = set()
                    while curr and curr in blocks and curr not in visited:
                        visited.add(curr)
                        cb = blocks[curr]
                        if cb.get("opcode", "") in ("looks_say", "looks_sayforsecs"):
                            has_say = True
                            break
                        curr = cb.get("next")
            if has_say:
                break
    if not has_say:
        raise check50.Failure(
            "Missing say block inside the loop.",
            help="Put a 'say' block inside the repeat loop so the sprite speaks the counted numbers."
        )

@check50.check(valid_sb3)
def change_inside_loop():
    """variable change/increment block is inside the loop"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    loop_opcodes = ["control_repeat", "control_repeat_until", "control_forever"]
    has_change = False
    for b_id, b in blocks.items():
        if b.get("opcode") in loop_opcodes:
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                inputs = b.get("inputs", {})
                if "SUBSTACK" in inputs:
                    sub_first = scratch_helper.get_block_input_value(b, "SUBSTACK", blocks)
                    curr = sub_first
                    visited = set()
                    while curr and curr in blocks and curr not in visited:
                        visited.add(curr)
                        cb = blocks[curr]
                        if cb.get("opcode", "") in ("data_changevariableby", "data_setvariableto"):
                            has_change = True
                            break
                        curr = cb.get("next")
            if has_change:
                break
    if not has_change:
        raise check50.Failure(
            "Missing variable increment block inside the loop.",
            help="Put a 'change [variable] by [2]' block inside the repeat loop to increment the number."
        )

@check50.check(valid_sb3)
def wait_inside_loop():
    """wait block is inside the loop to slow down counting"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    loop_opcodes = ["control_repeat", "control_repeat_until", "control_forever"]
    has_wait = False
    for b_id, b in blocks.items():
        if b.get("opcode") in loop_opcodes:
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                inputs = b.get("inputs", {})
                if "SUBSTACK" in inputs:
                    sub_first = scratch_helper.get_block_input_value(b, "SUBSTACK", blocks)
                    curr = sub_first
                    visited = set()
                    while curr and curr in blocks and curr not in visited:
                        visited.add(curr)
                        cb = blocks[curr]
                        op = cb.get("opcode", "")
                        if op == "control_wait" or op == "looks_sayforsecs":
                            has_wait = True
                            break
                        curr = cb.get("next")
            if has_wait:
                break
    if not has_wait:
        raise check50.Failure(
            "Missing wait block (or say for seconds block) inside the loop.",
            help="Add a 'wait [1] seconds' block or use 'say [Counter] for [1] seconds' inside the loop to slow down the counting."
        )

@check50.check(valid_sb3)
def says_variable_value():
    """say block inside loop speaks the variable, not a hardcoded string"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    loop_opcodes = ["control_repeat", "control_repeat_until", "control_forever"]
    says_var = False
    found_say = False
    for b_id, b in blocks.items():
        if b.get("opcode") in loop_opcodes:
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                inputs = b.get("inputs", {})
                if "SUBSTACK" in inputs:
                    sub_first = scratch_helper.get_block_input_value(b, "SUBSTACK", blocks)
                    curr = sub_first
                    visited = set()
                    while curr and curr in blocks and curr not in visited:
                        visited.add(curr)
                        cb = blocks[curr]
                        if cb.get("opcode", "") in ("looks_say", "looks_sayforsecs"):
                            found_say = True
                            if is_input_variable(cb, "MESSAGE", blocks):
                                says_var = True
                                break
                        curr = cb.get("next")
            if says_var:
                break
    if not found_say:
        raise check50.Failure("Missing say block inside the loop.")
    if not says_var:
        raise check50.Failure(
            "Say block is speaking a hardcoded value instead of the variable.",
            help="Drag your variable reporter block (from the Variables tab) into the say block's text slot."
        )

@check50.check(valid_sb3)
def increments_by_two():
    """variable increments by 2 in each loop iteration"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    loop_opcodes = ["control_repeat", "control_repeat_until", "control_forever"]
    inc_by_two = False
    found_change = False
    for b_id, b in blocks.items():
        if b.get("opcode") in loop_opcodes:
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                inputs = b.get("inputs", {})
                if "SUBSTACK" in inputs:
                    sub_first = scratch_helper.get_block_input_value(b, "SUBSTACK", blocks)
                    curr = sub_first
                    visited = set()
                    while curr and curr in blocks and curr not in visited:
                        visited.add(curr)
                        cb = blocks[curr]
                        if cb.get("opcode", "") == "data_changevariableby":
                            found_change = True
                            val_str = scratch_helper.get_block_input_value(cb, "VALUE", blocks)
                            if val_str is not None:
                                try:
                                    val = int(float(val_str))
                                    if val == 2:
                                        inc_by_two = True
                                        break
                                except ValueError:
                                    pass
                        curr = cb.get("next")
            if inc_by_two:
                break
    if not found_change:
        raise check50.Failure("Missing variable change block inside the loop.")
    if not inc_by_two:
        raise check50.Failure(
            "Variable does not increment by 2.",
            help="Set the increment value in 'change [variable] by [2]' to exactly 2."
        )

@check50.check(valid_sb3)
def count_limit():
    """repeat loop counts up to 100 (e.g. repeat 50 times)"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    found_repeat = False
    valid_limit = False
    times = 0
    for b_id, b in blocks.items():
        if b.get("opcode") == "control_repeat":
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                found_repeat = True
                times_str = scratch_helper.get_block_input_value(b, "TIMES", blocks)
                if times_str is not None:
                    try:
                        times = int(float(times_str))
                        if 40 <= times <= 60:
                            valid_limit = True
                            break
                    except ValueError:
                        pass
                        
    if not found_repeat:
        return

    if not valid_limit:
        if times > 60:
            raise check50.Failure(
                f"Repeat count is too high ({times} times).",
                help="If incrementing by 2, repeating 50 times reaches 100. Repeating 100 times would count up to 200!"
            )
        else:
            raise check50.Failure(
                f"Repeat count is too low ({times} times).",
                help="To count even numbers up to 100 (incrementing by 2), repeat 50 times."
            )
