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
def has_two_sprites():
    """project contains at least two sprites"""
    project = scratch_helper.get_project()
    if scratch_helper.count_sprites(project) < 2:
        raise check50.Failure("Did not find at least two sprites.")

@check50.check(valid_sb3)
def has_say_blocks():
    """sprites contain say blocks"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.has_opcode(blocks, "looks_say") and not scratch_helper.has_opcode(blocks, "looks_sayforsecs"):
        raise check50.Failure("Did not find any say blocks for dialogue.")

@check50.check(valid_sb3)
def dialogue_structured():
    """dialogue contains multiple say blocks"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    say_count = scratch_helper.count_opcode(blocks, "looks_say") + scratch_helper.count_opcode(blocks, "looks_sayforsecs")
    if say_count < 2:
        raise check50.Failure("Dialogue seems too short (need at least 2 say blocks).")
