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
    """project is expected to count even numbers from 1 to 100"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    if not scratch_helper.check_loop(blocks):
        raise check50.Failure("Did not find any loops to count to 100.")
    # Heuristic check for say blocks or variables
    if not scratch_helper.has_opcode(blocks, "looks_say") and not scratch_helper.has_opcode(blocks, "looks_sayforsecs"):
        raise check50.Failure("Sprite doesn't seem to say the numbers.")

