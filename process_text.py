import pprint


def gpt_output_to_diffusion_prompt(o):
    # Process prompt output to pull character descriptions
    # Transform into Stable Diffusion inputs
    components = o.split("\n")
    (char1Name, char1Desc) = components[0].split(" Description: ")
    (char2Name, char2Desc) = components[1].split(" Description: ")
    sceneDesc = components[3].split(": ")[1]
    frameDescsRaw = [components[2]] + list(
        map(lambda x: x.split(": ")[1], components[4:])
    )
    frameDescs = list(
        map(
            lambda x: x.replace(char1Name, char1Desc).replace(char2Name, char2Desc)
            + ", "
            + sceneDesc,
            frameDescsRaw,
        )
    )
    return frameDescs


result = gpt_output_to_diffusion_prompt(
    """Bill Description: George Clooney as a 45 year old businessman, salt and pepper hair, sharp suit
Joe Description: Ryan Gosling as a 35 year old engineer, blonde hair, glasses
Scene Background: Bill and Joe in a high-rise office, cityscape through the window, late evening
Scene Descriptors: high-rise office, cityscape view, late evening, sleek office decor
Line 1: Bill, serious, looking straight at Joe, hands clasped on the table
Line 2: Bill, acknowledging, nodding in appreciation, still maintaining eye contact
Line 3: Bill, furrowing his brow, hands gesturing for emphasis
Line 4: Joe, apologetic, looking down, hands clasped
Line 5: Joe, explaining, gesturing with one hand, looking hopeful
Line 6: Bill, angry, pointing at Joe, voice raised
Line 7: Bill, dismissive, turning away, arm extended towards the door."""
)

pp = pprint.PrettyPrinter()
pp.pprint(result)
