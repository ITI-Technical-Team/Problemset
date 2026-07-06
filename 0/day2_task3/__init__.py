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
def test_requirements():
    """project contains a custom block with an input parameter"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    if not scratch_helper.check_custom_block(blocks):
        raise check50.Failure("Did not find any custom blocks (functions).")
    if not scratch_helper.check_custom_block_with_input(blocks):
        raise check50.Failure("Custom block does not seem to accept inputs.")
    if not scratch_helper.has_opcode(blocks, "motion_movesteps"):
        raise check50.Failure("Did not find move steps block.")

