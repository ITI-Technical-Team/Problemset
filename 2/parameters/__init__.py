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
        raise check50.Failure("Did not find any custom blocks (functions).")

@check50.check(valid_sb3)
def has_custom_block_input():
    """custom block accepts input parameter(s)"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.check_custom_block_with_input(blocks):
        raise check50.Failure("Custom block does not seem to accept inputs.")

@check50.check(valid_sb3)
def has_motion_move():
    """project uses move steps block"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.has_opcode(blocks, "motion_movesteps"):
        raise check50.Failure("Did not find move steps block.")

@check50.check(valid_sb3)
def has_wait():
    """project uses wait block"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.has_opcode(blocks, "control_wait"):
        raise check50.Failure("Did not find a wait block.")
