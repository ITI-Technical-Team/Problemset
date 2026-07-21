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
