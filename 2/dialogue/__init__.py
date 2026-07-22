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
def has_two_active_event_scripts():
    """both sprites have scripts started by event blocks"""
    project = scratch_helper.get_project()
    active_event_sprites = 0
    for target in project.get("targets", []):
        if not target.get("isStage"):
            target_blocks = scratch_helper.get_target_blocks(target)
            has_event_script = False
            for b in target_blocks.values():
                opcode = b.get("opcode", "")
                if opcode.startswith("event_") or opcode == "control_start_as_clone":
                    next_id = b.get("next")
                    if next_id and isinstance(next_id, str) and next_id in target_blocks:
                        has_event_script = True
                        break
            if has_event_script:
                active_event_sprites += 1
                
    if active_event_sprites < 2:
        raise check50.Failure(
            "Not both sprites have event scripts.",
            help="Make sure both sprites start their actions with an event block like 'when green flag clicked' or 'when I receive message'."
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

def get_block_text(b, blocks):
    opcode = b.get("opcode")
    inputs = b.get("inputs", {})
    if opcode == "sensing_askandwait":
        input_name = "QUESTION"
    elif opcode in ("looks_say", "looks_sayforsecs", "looks_think", "looks_thinkforsecs"):
        input_name = "MESSAGE"
    else:
        return None

    inp = inputs.get(input_name)
    if not inp or len(inp) < 2:
        return None
    val = inp[1]
    if isinstance(val, list) and len(val) > 1:
        return str(val[1]).strip()
    elif isinstance(val, str):
        return scratch_helper.get_block_input_value(b, input_name, blocks)
    return None

@check50.check(both_sprites_have_scripts)
def uses_say_or_ask_or_think():
    """project uses say, ask, or think blocks for dialogue"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    dialogue_opcodes = ("looks_say", "looks_sayforsecs", "looks_think", "looks_thinkforsecs", "sensing_askandwait")
    has_dialogue_block = any(b.get("opcode") in dialogue_opcodes for b in blocks.values())
    if not has_dialogue_block:
        raise check50.Failure(
            "Project does not use say, ask, or think blocks.",
            help="Use blocks like 'say [Hello!] for [2] seconds' or 'ask [What is your name?] and wait' to make your sprites speak."
        )

@check50.check(both_sprites_have_scripts)
def first_sprite_asks():
    """first sprite asks 'How old are you?'"""
    project = scratch_helper.get_project()
    asked_question = False

    for target in project.get("targets", []):
        if not target.get("isStage"):
            target_blocks = scratch_helper.get_target_blocks(target)
            for b_id, b in target_blocks.items():
                opcode = b.get("opcode", "")
                if opcode in ("looks_say", "looks_sayforsecs", "looks_think", "looks_thinkforsecs", "sensing_askandwait"):
                    if scratch_helper.is_connected_to_hat(b_id, target_blocks):
                        msg = get_block_text(b, target_blocks)
                        if msg:
                            msg_lower = str(msg).lower()
                            if "how old" in msg_lower:
                                asked_question = True
                                break
            if asked_question:
                break

    if not asked_question:
        raise check50.Failure(
            "First sprite did not ask 'How old are you?'",
            help="In the say or ask block for the first sprite, type 'How old are you?'."
        )

@check50.check(both_sprites_have_scripts)
def second_sprite_answers():
    """second sprite answers with age '20'"""
    project = scratch_helper.get_project()
    answered_age = False

    for target in project.get("targets", []):
        if not target.get("isStage"):
            target_blocks = scratch_helper.get_target_blocks(target)
            for b_id, b in target_blocks.items():
                opcode = b.get("opcode", "")
                if opcode in ("looks_say", "looks_sayforsecs", "looks_think", "looks_thinkforsecs", "sensing_askandwait"):
                    if scratch_helper.is_connected_to_hat(b_id, target_blocks):
                        msg = get_block_text(b, target_blocks)
                        if msg:
                            msg_lower = str(msg).lower()
                            if "20" in msg_lower:
                                answered_age = True
                                break
            if answered_age:
                break

    if not answered_age:
        raise check50.Failure(
            "Second sprite did not answer with age '20'",
            help="In the say or think block for the second sprite, include '20' (e.g., 'I'm 20 years old.')."
        )
