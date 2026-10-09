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
def has_custom_block():
    """project defines a custom block (function)"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.check_custom_block(blocks):
        raise check50.Failure("Did not find any custom blocks (functions).", help="Create a custom block using 'Make a Block' under My Blocks.")

@check50.check(has_custom_block)
def custom_block_has_body():
    """custom block has code blocks attached under 'define'"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.check_custom_block_has_body(blocks):
        raise check50.Failure(
            "Custom block 'define' block has no code attached.",
            help="Attach code blocks directly under the 'define' block for your custom function."
        )

def get_custom_block_body_blocks(definition_block_id, blocks):
    visited = set()
    chain = []
    current_id = blocks[definition_block_id].get("next")
    while current_id and current_id not in visited:
        visited.add(current_id)
        block = blocks.get(current_id)
        if not block:
            break
        chain.append(block)
        inputs = block.get("inputs", {})
        for key in ("SUBSTACK", "SUBSTACK2"):
            if key in inputs:
                inner = inputs[key]
                if isinstance(inner, list) and len(inner) > 1:
                    inner_id = inner[1]
                    if inner_id and isinstance(inner_id, str) and inner_id in blocks:
                        sub_chain_visited = set()
                        sub_current_id = inner_id
                        while sub_current_id and sub_current_id not in sub_chain_visited:
                            sub_chain_visited.add(sub_current_id)
                            sub_block = blocks.get(sub_current_id)
                            if not sub_block:
                                break
                            chain.append(sub_block)
                            sub_current_id = sub_block.get("next")
        current_id = block.get("next")
    return chain

def is_action_block(block):
    opcode = block.get("opcode", "")
    if opcode == "procedures_call":
        return True
    if opcode.startswith("procedures_"):
        return False
    if opcode in ("control_if", "control_if_else", "control_repeat", "control_forever", "control_repeat_until"):
        return False
    return True

@check50.check(has_custom_block)
def custom_block_has_action():
    """custom block executes at least one action"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    has_action = False
    for block_id, block in blocks.items():
        if block.get("opcode") == "procedures_definition":
            body = get_custom_block_body_blocks(block_id, blocks)
            if any(is_action_block(b) for b in body):
                has_action = True
                break
    if not has_action:
        raise check50.Failure(
            "Custom block does not execute any actions.",
            help="Attach action blocks (like motion, looks, sound, etc.) inside your custom block definition."
        )

@check50.check(has_custom_block)
def calls_custom_block():
    """custom block is called from an event script"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.check_custom_block_called(blocks):
        raise check50.Failure(
            "Did not call the custom block.",
            help="Use your custom block call (from My Blocks) attached to an event block like 'when green flag clicked' to execute the function."
        )

@check50.check(valid_sb3)
def has_conditional():
    """project contains a working conditional"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.check_active_conditional(blocks) and not scratch_helper.check_active_conditional_in_custom_block(blocks):
        raise check50.Failure(
            "Did not find a working conditional.",
            help="Make sure your conditional (if or if-else) is: (1) attached to an event or inside a custom block, and (2) has blocks inside it."
        )

@check50.check(valid_sb3)
def conditional_has_action():
    """conditional block has actions inside it"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    conditional_opcodes = ["control_if", "control_if_else"]
    has_act = False
    found_cond = False
    for block_id, block in blocks.items():
        if block.get("opcode") in conditional_opcodes:
            found_cond = True
            inputs = block.get("inputs", {})
            for key in ("SUBSTACK", "SUBSTACK2"):
                if key in inputs:
                    inner = inputs[key]
                    if isinstance(inner, list) and len(inner) > 1:
                        inner_id = inner[1]
                        if inner_id and isinstance(inner_id, str) and inner_id in blocks:
                            visited = set()
                            current_id = inner_id
                            while current_id and current_id not in visited:
                                visited.add(current_id)
                                b = blocks.get(current_id)
                                if not b:
                                    break
                                if is_action_block(b):
                                    has_act = True
                                    break
                                current_id = b.get("next")
            if has_act:
                break
    if not found_cond:
        raise check50.Failure("Did not find a conditional block.")
    if not has_act:
        raise check50.Failure(
            "Conditional block is empty.",
            help="Make sure you place blocks (like motion, looks, or sound blocks) inside the 'then' or 'else' part of your conditional."
        )

@check50.check(valid_sb3)
def conditional_has_condition():
    """conditional block has a condition input"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    conditional_opcodes = ["control_if", "control_if_else"]
    has_cond = False
    found_cond = False
    for block_id, block in blocks.items():
        if block.get("opcode") in conditional_opcodes:
            found_cond = True
            inputs = block.get("inputs", {})
            if "CONDITION" in inputs:
                cond_val = inputs["CONDITION"]
                if isinstance(cond_val, list) and len(cond_val) > 1:
                    cond_id = cond_val[1]
                    if cond_id and isinstance(cond_id, str) and cond_id in blocks:
                        has_cond = True
                        break
    if not found_cond:
        raise check50.Failure("Did not find a conditional block.")
    if not has_cond:
        raise check50.Failure(
            "Conditional block's condition is empty.",
            help="Place a sensing or operator block (like 'touching mouse-pointer?' or comparison) inside the condition slot of the 'if' block."
        )

@check50.check(valid_sb3)
def uses_action_blocks():
    """project uses motion, looks, sound, pen, or data blocks to perform actions"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    has_action = False
    for b in blocks.values():
        opcode = b.get("opcode", "")
        if any(opcode.startswith(prefix) for prefix in ("motion_", "looks_", "sound_", "data_", "pen_")):
            has_action = True
            break
            
    if not has_action:
        raise check50.Failure(
            "Project does not use any action blocks.",
            help="Use blocks like 'move', 'say', or 'play sound' to perform actions."
        )

@check50.check(valid_sb3)
def event_starts_script():
    """project has an event block connected to an action script"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    has_event_chain = False
    for b in blocks.values():
        opcode = b.get("opcode", "")
        # Omit procedures definition from starting events as it's not a user event
        if opcode.startswith("event_") or opcode == "control_start_as_clone":
            next_id = b.get("next")
            if next_id and isinstance(next_id, str) and next_id in blocks:
                has_event_chain = True
                break
                
    if not has_event_chain:
        raise check50.Failure(
            "No event script starts actions.",
            help="Make sure you attach blocks below event blocks (like 'when green flag clicked')."
        )
