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
    """project contains two different sprites with dialogue"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    if scratch_helper.count_sprites(project) < 2:
        raise check50.Failure("Did not find at least two sprites.")
    if not scratch_helper.has_opcode(blocks, "looks_say") and not scratch_helper.has_opcode(blocks, "looks_sayforsecs"):
        raise check50.Failure("Did not find any say blocks for dialogue.")

