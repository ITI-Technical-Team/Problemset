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
        raise check50.Failure("Could not read the .sb3 file. Make sure it is a valid Scratch project.")

@check50.check(valid_sb3)
def has_custom_block():
    """project defines a custom block (function)"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.check_custom_block(blocks):
        raise check50.Failure("Did not find any custom blocks.", help="Create a custom block using 'Make a Block' in the 'My Blocks' category.")

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

@check50.check(has_custom_block)
def has_sprites():
    """project contains at least one sprite"""
    project = scratch_helper.get_project()
    if scratch_helper.count_sprites(project) < 1:
        raise check50.Failure("Did not find any sprites in the project.")
