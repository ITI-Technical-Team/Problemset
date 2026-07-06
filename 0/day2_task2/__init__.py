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
    """project uses space key, conditionals, sound and wait blocks"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    if not scratch_helper.has_opcode(blocks, "sensing_keypressed"):
        raise check50.Failure("Did not find sensing block for key press.")
    if not scratch_helper.has_opcode(blocks, "control_if_else"):
        raise check50.Failure("Did not find an if-else block.")
    if not scratch_helper.has_opcode(blocks, "sound_play") and not scratch_helper.has_opcode(blocks, "sound_playuntildone"):
        raise check50.Failure("Did not find a sound block.")
    if not scratch_helper.has_opcode(blocks, "control_wait"):
        raise check50.Failure("Did not find a wait block.")

