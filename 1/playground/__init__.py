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
def has_sprites():
    """project contains at least one sprite"""
    project = scratch_helper.get_project()
    if scratch_helper.count_sprites(project) < 1:
        raise check50.Failure("Did not find any sprites in the project.")

@check50.check(valid_sb3)
def has_blocks():
    """project contains code blocks"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if len(blocks) < 1:
        raise check50.Failure("Project seems empty (no blocks found).")

@check50.check(valid_sb3)
def has_loop():
    """project contains at least 1 loop"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.check_loop(blocks):
        raise check50.Failure("Did not find any loops (e.g., repeat, forever).")

@check50.check(valid_sb3)
def has_conditional():
    """project contains at least 1 conditional"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.check_conditional(blocks):
        raise check50.Failure("Did not find any conditionals (e.g., if, if-else).")
