import zipfile
import json
import check50

import glob

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

def has_opcode(blocks, opcode):
    """Checks if there is at least one block with the given opcode."""
    return any(b.get("opcode") == opcode for b in blocks.values())

def count_opcode(blocks, opcode):
    """Counts the number of blocks with the given opcode."""
    return sum(1 for b in blocks.values() if b.get("opcode") == opcode)

def check_loop(blocks):
    """Checks if a loop exists."""
    loop_opcodes = ["control_repeat", "control_forever", "control_repeat_until"]
    return any(has_opcode(blocks, op) for op in loop_opcodes)

def check_conditional(blocks):
    """Checks if a conditional exists."""
    conditional_opcodes = ["control_if", "control_if_else"]
    return any(has_opcode(blocks, op) for op in conditional_opcodes)

def check_custom_block(blocks):
    """Checks if a custom block (function) exists."""
    return has_opcode(blocks, "procedures_definition")

def check_custom_block_with_input(blocks):
    """Checks if a custom block has inputs."""
    return has_opcode(blocks, "argument_reporter_string_number") or has_opcode(blocks, "argument_reporter_boolean")

def count_sprites(project):
    """Counts the number of sprites (excluding the stage)."""
    return sum(1 for t in project.get("targets", []) if not t.get("isStage"))
