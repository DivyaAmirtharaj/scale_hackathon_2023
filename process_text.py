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
    """Roman Description: George Clooney as a 45 year old businessman, salt and pepper hair, wearing a suit
Sarah Description: Jennifer Aniston as a 40 year old artist, wavy brown hair, wearing a summer dress
Scene Background: Roman and Sarah, standing in a modern art gallery, surrounded by contemporary paintings and sculptures
Scene Descriptors: modern art gallery, contemporary paintings and sculptures, bright lighting, large windows
Line 1: Roman, serious, looking straight ahead, hands clasped
Line 2: Sarah, surprised, raising an eyebrow
Line 3: Roman, looking down, sorrowful
Line 4: Roman, looking away, regretful
Line 5: Roman, closing eyes, pained expression
Line 6: Sarah, shocked, mouth open
Line 7: Roman, looking at Sarah, nodding
Line 8: Roman, apologetic, looking down."""
)

for x in result:
    print(x)
