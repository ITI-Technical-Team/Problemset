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
def has_custom_block():
    """defines a custom block (function)"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.check_custom_block(blocks):
        raise check50.Failure("Did not find any custom blocks (functions).", help="Create a custom block in the 'My Blocks' category.")

@check50.check(valid_sb3)
def has_custom_input():
    """custom block has an input parameter"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.check_custom_block_with_input(blocks):
        raise check50.Failure("Custom block does not seem to accept inputs.", help="Add a number or text input when creating your custom block.")

@check50.check(valid_sb3)
def has_multiplication():
    """performs multiplication (age * 365)"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.has_opcode(blocks, "operator_multiply"):
        raise check50.Failure("Did not find multiplication block.", help="Use the '*' operator block from the Operators category.")

@check50.check(valid_sb3)
def has_say():
    """says the result"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.has_opcode(blocks, "looks_say") and not scratch_helper.has_opcode(blocks, "looks_sayforsecs"):
        raise check50.Failure("Sprite doesn't seem to use any 'say' blocks.", help="Use the 'say' block from the Looks category to output the calculated days.")
