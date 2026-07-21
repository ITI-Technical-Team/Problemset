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
def has_two_sprites():
    """project contains at least two sprites"""
    project = scratch_helper.get_project()
    if scratch_helper.count_sprites(project) < 2:
        raise check50.Failure("Did not find at least two sprites in the project.")

@check50.check(has_two_sprites)
def both_sprites_have_scripts():
    """both sprites have active scripts connected to events"""
    project = scratch_helper.get_project()

    active_sprites = 0
    for target in project.get("targets", []):
        if not target.get("isStage"):
            target_blocks = scratch_helper.get_target_blocks(target)
            has_script = False
            for b_id in target_blocks.keys():
                if scratch_helper.is_connected_to_hat(b_id, target_blocks):
                    has_script = True
                    break
            if has_script:
                active_sprites += 1

    if active_sprites < 2:
        raise check50.Failure(
            "Dialogue blocks are all on one sprite.",
            help="Make sure BOTH sprites have code blocks attached to event blocks (e.g. 'when green flag clicked' on Sprite 1 and 'when I receive message1' on Sprite 2)."
        )

@check50.check(both_sprites_have_scripts)
def uses_broadcast_sync():
    """sprites communicate using broadcast and receive blocks"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)

    has_broadcast = (
        scratch_helper.has_opcode(blocks, "event_broadcast") or
        scratch_helper.has_opcode(blocks, "event_broadcastandwait")
    )
    has_receive = scratch_helper.has_opcode(blocks, "event_whenbroadcastreceived")

    if not (has_broadcast and has_receive):
        raise check50.Failure(
            "Missing broadcast / receive blocks for sprite communication.",
            help="Use 'broadcast [message1]' on the first sprite and 'when I receive [message1]' on the second sprite so they take turns speaking."
        )

@check50.check(both_sprites_have_scripts)
def dialogue_text_correct():
    """sprites say the required dialogue text"""
    project = scratch_helper.get_project()

    asked_question = False
    answered_age = False

    for target in project.get("targets", []):
        if not target.get("isStage"):
            target_blocks = scratch_helper.get_target_blocks(target)
            for b_id, b in target_blocks.items():
                if b.get("opcode") in ("looks_say", "looks_sayforsecs"):
                    if scratch_helper.is_connected_to_hat(b_id, target_blocks):
                        msg = scratch_helper.get_block_input_value(b, "MESSAGE", target_blocks)
                        if msg:
                            msg_lower = str(msg).lower()
                            if "how old" in msg_lower:
                                asked_question = True
                            if "20" in msg_lower:
                                answered_age = True

    if not asked_question:
        raise check50.Failure(
            "First sprite did not ask 'How old are you?'",
            help="In the say block for the first sprite, type 'How old are you?'."
        )

    if not answered_age:
        raise check50.Failure(
            "Second sprite did not answer with age '20'",
            help="In the say block for the second sprite, include '20' (e.g., 'I'm 20 years old.')."
        )
