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
def has_space_key_condition():
    """project checks if space key is pressed"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    found_space = False

    for b_id, b in blocks.items():
        op = b.get("opcode", "")
        if op == "sensing_keypressed":
            # Check key option input or fields
            key_val = scratch_helper.get_block_input_value(b, "KEY_OPTION", blocks) or scratch_helper.get_block_field_value(b, "KEY_OPTION")
            # If input points to a sensing_keyoptions block
            if key_val and key_val in blocks:
                key_val = scratch_helper.get_block_field_value(blocks[key_val], "KEY_OPTION")
            if key_val and key_val.lower() == "space":
                found_space = True
                break
        elif op == "event_whenkeypressed":
            key_val = scratch_helper.get_block_field_value(b, "KEY_OPTION")
            if key_val and key_val.lower() == "space":
                found_space = True
                break

    if not found_space:
        raise check50.Failure(
            "Did not find sensing block for space key pressed.",
            help="Use the 'key [space] pressed?' sensing block inside your if-else condition."
        )

@check50.check(has_space_key_condition)
def has_if_else_connected():
    """if-else block is connected to an event script"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    found_if_else = False
    for b_id, b in blocks.items():
        if b.get("opcode") == "control_if_else":
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                found_if_else = True
                break

    if not found_if_else:
        raise check50.Failure(
            "If-else block is disconnected or missing.",
            help="Attach your if-else block to an event block like 'when green flag clicked' or 'when space key pressed'."
        )

@check50.check(has_if_else_connected)
def then_branch_move_and_wait():
    """then branch moves 1 step and waits 1 second"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    valid_then = False
    move_first = True

    for b_id, b in blocks.items():
        if b.get("opcode") == "control_if_else":
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                has_move_1 = False
                has_wait_1 = False
                move_idx = -1
                wait_idx = -1

                inputs = b.get("inputs", {})
                if "SUBSTACK" in inputs:
                    sub_first = scratch_helper.get_block_input_value(b, "SUBSTACK", blocks)
                    if sub_first and sub_first in blocks:
                        curr = sub_first
                        visited = set()
                        idx = 0
                        while curr and curr in blocks and curr not in visited:
                            visited.add(curr)
                            cb = blocks[curr]
                            op = cb.get("opcode", "")
                            if op == "motion_movesteps":
                                steps = scratch_helper.get_block_input_value(cb, "STEPS", blocks)
                                if steps and str(steps).strip() == "1":
                                    has_move_1 = True
                                    move_idx = idx
                            if op == "control_wait":
                                dur = scratch_helper.get_block_input_value(cb, "DURATION", blocks)
                                if dur and str(dur).strip() == "1":
                                    has_wait_1 = True
                                    wait_idx = idx
                            idx += 1
                            curr = cb.get("next")

                if has_move_1 and has_wait_1:
                    if move_idx < wait_idx:
                        valid_then = True
                        break
                    else:
                        move_first = False

    if not valid_then:
        if not move_first:
            raise check50.Failure(
                "Then branch has incorrect block order.",
                help="Move 1 steps must come before wait 1 seconds, not the opposite."
            )
        raise check50.Failure(
            "Then branch is missing 'move 1 steps' or 'wait 1 seconds'.",
            help="Inside the top ('then') section of your if-else block, add: (1) 'move 1 steps', and (2) 'wait 1 seconds'."
        )

@check50.check(has_if_else_connected)
def else_branch_sound_and_wait():
    """else branch plays a sound and waits 2 seconds"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    valid_else = False
    sound_first = True

    for b_id, b in blocks.items():
        if b.get("opcode") == "control_if_else":
            if scratch_helper.is_connected_to_hat(b_id, blocks):
                has_sound = False
                has_wait_2 = False
                sound_idx = -1
                wait_idx = -1

                inputs = b.get("inputs", {})
                if "SUBSTACK2" in inputs:
                    sub_first = scratch_helper.get_block_input_value(b, "SUBSTACK2", blocks)
                    if sub_first and sub_first in blocks:
                        curr = sub_first
                        visited = set()
                        idx = 0
                        while curr and curr in blocks and curr not in visited:
                            visited.add(curr)
                            cb = blocks[curr]
                            op = cb.get("opcode", "")
                            if op in ("sound_play", "sound_playuntildone"):
                                has_sound = True
                                sound_idx = idx
                            if op == "control_wait":
                                dur = scratch_helper.get_block_input_value(cb, "DURATION", blocks)
                                if dur and str(dur).strip() == "2":
                                    has_wait_2 = True
                                    wait_idx = idx
                            idx += 1
                            curr = cb.get("next")

                if has_sound and has_wait_2:
                    if sound_idx < wait_idx:
                        valid_else = True
                        break
                    else:
                        sound_first = False

    if not valid_else:
        if not sound_first:
            raise check50.Failure(
                "Else branch has incorrect block order.",
                help="Play sound must come before wait 2 seconds, not the opposite."
            )
        raise check50.Failure(
            "Else branch is missing sound or 'wait 2 seconds'.",
            help="Inside the bottom ('else') section of your if-else block, add: (1) a sound block, and (2) 'wait 2 seconds'."
        )
