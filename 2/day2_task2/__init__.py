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
def has_space_key():
    """project uses sensing block for space key pressed"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.has_opcode(blocks, "sensing_keypressed"):
        raise check50.Failure("Did not find sensing block for key press.")

@check50.check(valid_sb3)
def has_if_else():
    """project uses an if-else conditional block"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.has_opcode(blocks, "control_if_else"):
        raise check50.Failure("Did not find an if-else block.")

@check50.check(valid_sb3)
def has_sound():
    """project plays sound blocks"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.has_opcode(blocks, "sound_play") and not scratch_helper.has_opcode(blocks, "sound_playuntildone"):
        raise check50.Failure("Did not find a sound block.")

@check50.check(valid_sb3)
def has_wait():
    """project uses wait block"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.has_opcode(blocks, "control_wait"):
        raise check50.Failure("Did not find a wait block.")
