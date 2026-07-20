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
def has_loop():
    """project contains a loop connected to an event and doing something"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.check_active_loop(blocks):
        raise check50.Failure(
            "Did not find a working loop.",
            help="Make sure your loop (repeat, forever, or repeat until) is: "
                 "(1) attached to a hat block like 'when green flag clicked', and "
                 "(2) has at least one block inside it."
        )

@check50.check(valid_sb3)
def has_conditional():
    """project contains a conditional connected to an event and doing something"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.check_active_conditional(blocks):
        raise check50.Failure(
            "Did not find a working conditional.",
            help="Make sure your if/if-else block is: "
                 "(1) attached to a hat block like 'when green flag clicked', and "
                 "(2) has at least one block inside it."
        )
