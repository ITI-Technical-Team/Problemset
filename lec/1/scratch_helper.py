import zipfile
import json
import check50

import glob

# Hat block opcodes — blocks that start a script
HAT_OPCODES = {
    "event_whenflagclicked",
    "event_whenkeypressed",
    "event_whenthisspriteclicked",
    "event_whenbackdropswitchesto",
    "event_whengreaterthan",
    "event_whenbroadcastreceived",
    "control_start_as_clone",
    "procedures_definition",
}

def get_project(filename=None):
    """Extracts and parses project.json from the given Scratch .sb3 file."""
    if filename is None:
        sb3_files = glob.glob("*.sb3")
        if not sb3_files:
            raise check50.Failure("No .sb3 file found.")
        filename = sb3_files[0]

    try:
        with zipfile.ZipFile(filename, 'r') as z:
            with z.open("project.json") as f:
                return json.load(f)
    except Exception as e:
        raise check50.Failure(f"Could not read {filename}. Make sure it is a valid Scratch .sb3 file.")

def get_blocks(project):
    """Returns a dictionary of all blocks across all targets in the project."""
    blocks = {}
    for target in project.get("targets", []):
        for block_id, block in target.get("blocks", {}).items():
            if isinstance(block, dict):
                blocks[block_id] = block
    return blocks

def get_target_blocks(target):
    """Returns a dict of blocks for a specific target sprite/stage."""
    blocks = {}
    for block_id, block in target.get("blocks", {}).items():
        if isinstance(block, dict):
            blocks[block_id] = block
    return blocks

def get_block_input_value(block, input_name, blocks=None):
    """Extracts raw value or connected block ID from a block's input field."""
    inputs = block.get("inputs", {})
    if input_name not in inputs:
        return None
    val = inputs[input_name]
    if isinstance(val, list):
        if len(val) >= 2:
            second = val[1]
            if isinstance(second, list) and len(second) >= 2:
                return str(second[1])
            elif isinstance(second, str):
                return second
    return None

def get_block_field_value(block, field_name):
    """Extracts field value from a block's fields."""
    fields = block.get("fields", {})
    if field_name not in fields:
        return None
    val = fields[field_name]
    if isinstance(val, list) and len(val) >= 1:
        return str(val[0])
    return str(val)

def has_opcode(blocks, opcode):
    """Checks if there is at least one block with the given opcode."""
    return any(b.get("opcode") == opcode for b in blocks.values())

def count_opcode(blocks, opcode):
    """Counts the number of blocks with the given opcode."""
    return sum(1 for b in blocks.values() if b.get("opcode") == opcode)

def is_connected_to_hat(block_id, blocks):
    """Checks if the given block is part of a script connected to a hat block.
    Traces the parent chain upward until it finds a hat block or dead-ends."""
    current_id = block_id
    visited = set()
    while current_id:
        if current_id in visited:
            return False  # circular reference guard
        visited.add(current_id)
        block = blocks.get(current_id)
        if not block:
            return False
        if block.get("opcode") in HAT_OPCODES:
            return True
        parent_id = block.get("parent")
        if not parent_id:
            return False
        current_id = parent_id
    return False

def is_inside_custom_block(block_id, blocks):
    """Traces parent chain upward to check if block_id is attached under a procedures_definition block."""
    current_id = block_id
    visited = set()
    while current_id:
        if current_id in visited:
            return False
        visited.add(current_id)
        block = blocks.get(current_id)
        if not block:
            return False
        if block.get("opcode") == "procedures_definition":
            return True
        parent_id = block.get("parent")
        if not parent_id:
            return False
        current_id = parent_id
    return False

def block_has_substack(block, blocks):
    """Checks if a loop or conditional block has at least one block inside it (non-empty)."""
    inputs = block.get("inputs", {})
    for key in ("SUBSTACK", "SUBSTACK2"):
        if key in inputs:
            inner = inputs[key]
            if isinstance(inner, list) and len(inner) > 1:
                inner_id = inner[1]
                if inner_id and isinstance(inner_id, str) and inner_id in blocks:
                    return True
    return False

def check_loop(blocks):
    """Checks if a loop exists that is connected to a hat block."""
    loop_opcodes = ["control_repeat", "control_forever", "control_repeat_until"]
    for block_id, block in blocks.items():
        if block.get("opcode") in loop_opcodes:
            if is_connected_to_hat(block_id, blocks):
                return True
    return False

def check_conditional(blocks):
    """Checks if a conditional exists that is connected to a hat block."""
    conditional_opcodes = ["control_if", "control_if_else"]
    for block_id, block in blocks.items():
        if block.get("opcode") in conditional_opcodes:
            if is_connected_to_hat(block_id, blocks):
                return True
    return False

def check_active_loop(blocks):
    """Checks if a loop exists that is connected to a hat block AND has blocks inside it."""
    loop_opcodes = ["control_repeat", "control_forever", "control_repeat_until"]
    for block_id, block in blocks.items():
        if block.get("opcode") in loop_opcodes:
            if is_connected_to_hat(block_id, blocks) and block_has_substack(block, blocks):
                return True
    return False

def check_active_conditional(blocks):
    """Checks if a conditional exists that is connected to a hat block AND has blocks inside it."""
    conditional_opcodes = ["control_if", "control_if_else"]
    for block_id, block in blocks.items():
        if block.get("opcode") in conditional_opcodes:
            if is_connected_to_hat(block_id, blocks) and block_has_substack(block, blocks):
                return True
    return False

def check_active_loop_in_custom_block(blocks):
    """Checks if a non-empty loop exists INSIDE a custom block definition."""
    loop_opcodes = ["control_repeat", "control_forever", "control_repeat_until"]
    for block_id, block in blocks.items():
        if block.get("opcode") in loop_opcodes:
            if is_inside_custom_block(block_id, blocks) and block_has_substack(block, blocks):
                return True
    return False

def check_active_conditional_in_custom_block(blocks):
    """Checks if a non-empty conditional exists INSIDE a custom block definition."""
    conditional_opcodes = ["control_if", "control_if_else"]
    for block_id, block in blocks.items():
        if block.get("opcode") in conditional_opcodes:
            if is_inside_custom_block(block_id, blocks) and block_has_substack(block, blocks):
                return True
    return False

def check_custom_block_has_body(blocks):
    """Checks if at least one procedures_definition block has code attached (next pointer points to a valid block)."""
    for block_id, block in blocks.items():
        if block.get("opcode") == "procedures_definition":
            next_id = block.get("next")
            if next_id and isinstance(next_id, str) and next_id in blocks:
                return True
    return False

def check_custom_block_called(blocks):
    """Checks if a custom block is called (procedures_call) and connected to an event/hat block."""
    for block_id, block in blocks.items():
        if block.get("opcode") == "procedures_call":
            if is_connected_to_hat(block_id, blocks):
                return True
    return False

def check_custom_block(blocks):
    """Checks if a custom block (function) exists."""
    return has_opcode(blocks, "procedures_definition")

def check_custom_block_with_input(blocks):
    """Checks if a custom block has inputs."""
    return has_opcode(blocks, "argument_reporter_string_number") or has_opcode(blocks, "argument_reporter_boolean")

def count_sprites(project):
    """Counts the number of sprites (excluding the stage)."""
    return sum(1 for t in project.get("targets", []) if not t.get("isStage"))
