import check50
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import scratch_helper

@check50.check()
def exists():
    """project.sb3 exists"""
    check50.exists("*.sb3")

@check50.check(exists)
def test_requirements():
    """project contains a function with 1 loop and 1 conditional"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    if not scratch_helper.check_custom_block(blocks):
        raise check50.Failure("Did not find any custom blocks (functions).")
    if not scratch_helper.check_loop(blocks):
        raise check50.Failure("Did not find any loops inside the project.")
    if not scratch_helper.check_conditional(blocks):
        raise check50.Failure("Did not find any conditionals inside the project.")

