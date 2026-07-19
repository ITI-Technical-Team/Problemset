import check50
import re
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
def asks_question():
    """sprite asks 'where are you from?'"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    # Check sensing_askandwait block exists
    ask_blocks = [b for b in blocks.values() if b.get("opcode") == "sensing_askandwait"]
    if not ask_blocks:
        raise check50.Failure("Did not find 'ask and wait' block.", help="Use the 'ask [where are you from?] and wait' block from the Sensing category.")
        
    found_question = False
    for b in ask_blocks:
        question_input = b.get("inputs", {}).get("QUESTION")
        if question_input and len(question_input) > 1:
            val = question_input[1]
            if isinstance(val, list) and len(val) > 1:
                text = str(val[1]).strip().lower()
                # Match "where are you from" case-insensitively and ignore punctuation/spaces
                clean_text = re.sub(r"[^\w\s]", "", text)
                clean_target = re.sub(r"[^\w\s]", "", "where are you from")
                if clean_target in clean_text:
                    found_question = True
                    break
            elif isinstance(val, str):
                ref_block = blocks.get(val)
                if ref_block:
                    # Traversal helper for nested text blocks
                    def get_text_recursive(block_id):
                        bl = blocks.get(block_id)
                        if not bl:
                            return ""
                        combined_text = ""
                        for inp in bl.get("inputs", {}).values():
                            if isinstance(inp, list) and len(inp) > 1:
                                nested_val = inp[1]
                                if isinstance(nested_val, list) and len(nested_val) > 1:
                                    combined_text += " " + str(nested_val[1]).strip().lower()
                                elif isinstance(nested_val, str):
                                    combined_text += " " + get_text_recursive(nested_val)
                        return combined_text
                    
                    text = get_text_recursive(val)
                    clean_text = re.sub(r"[^\w\s]", "", text)
                    clean_target = re.sub(r"[^\w\s]", "", "where are you from")
                    if clean_target in clean_text:
                        found_question = True
                        break
                        
    if not found_question:
        raise check50.Failure("Sprite did not ask 'where are you from?'", help="Make sure your 'ask' block contains the exact text: 'where are you from?'")

@check50.check(asks_question)
def prints_answer():
    """sprite says the answer"""
    project = scratch_helper.get_project()
    blocks = scratch_helper.get_blocks(project)
    
    # Check sensing_answer block exists
    if not scratch_helper.has_opcode(blocks, "sensing_answer"):
        raise check50.Failure("Did not find the 'answer' block.", help="Use the 'answer' reporter block from the Sensing category to refer to the user's input.")
        
    # Check looks_say or looks_sayforsecs exists
    say_opcodes = ["looks_say", "looks_sayforsecs"]
    say_blocks = [b for b in blocks.values() if b.get("opcode") in say_opcodes]
    if not say_blocks:
        raise check50.Failure("Did not find 'say' block.", help="Use the 'say' or 'say for [2] seconds' block from the Looks category to print the answer.")
        
    # Helper to recursively check if target block ID is used in an expression
    answer_ids = [bid for bid, b in blocks.items() if b.get("opcode") == "sensing_answer"]
    
    def uses_id(block_id, target_ids):
        if block_id in target_ids:
            return True
        block = blocks.get(block_id)
        if not block:
            return False
        for inp in block.get("inputs", {}).values():
            if isinstance(inp, list) and len(inp) > 1:
                val = inp[1]
                if isinstance(val, str) and uses_id(val, target_ids):
                    return True
        return False

    found_print = False
    for b in say_blocks:
        message_input = b.get("inputs", {}).get("MESSAGE")
        if message_input and len(message_input) > 1:
            val = message_input[1]
            if isinstance(val, str) and uses_id(val, answer_ids):
                found_print = True
                break
                
    if not found_print:
        raise check50.Failure("Sprite did not say the answer.", help="Make sure you pass the 'answer' block into your 'say' block.")
