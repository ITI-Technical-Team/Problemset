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
def has_space_trigger():
    """project detects the 'space' key press"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    found_space = False
    for b in blocks.values():
        if b.get("opcode") in ["event_whenkeypressed", "sensing_keyoptions"]:
            for f_val in b.get("fields", {}).values():
                if isinstance(f_val, list) and len(f_val) > 0 and str(f_val[0]).strip().lower() == "space":
                    found_space = True
                    break
        if found_space:
            break
            
    if not found_space:
        raise check50.Failure("Did not find space key press detection block.", help="Use the 'when [space] key pressed' event or the 'key [space] pressed?' sensing block.")

@check50.check(valid_sb3)
def plays_sound():
    """project plays a sound"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    if not scratch_helper.has_opcode(blocks, "sound_play") and not scratch_helper.has_opcode(blocks, "sound_playuntildone"):
        raise check50.Failure("Did not find any sound blocks.", help="Use a 'start sound' or 'play sound until done' block to produce a sound.")
