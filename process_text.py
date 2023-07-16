import pprint
import requests


def gpt_output_to_diffusion_prompt(o):
    # Process prompt output to pull character descriptions
    # Transform into Stable Diffusion inputs

    print("Converting GPT output to diffusion prompts.")
    components = o.split("\n")
    (char1Name, char1Desc) = components[0].split(" Description: ")
    (char2Name, char2Desc) = components[1].split(" Description: ")
    sceneDesc = components[3].split(": ")[1]
    frameDescsRaw = [components[2]] + list(
        map(lambda x: x.split(": ")[1], components[4:])
    )
    frameDescs2 = []
    for x in frameDescsRaw:
        if char1Name in x and char2Name in x:
            if x.index(char1Name) < x.index(char2Name):
                frameDescs2.append(x.replace(char2Name, ""))
            else:
                frameDescs2.append(x.replace(char1Name, ""))
        else:
            frameDescs2.append(x)
    frameDescs = list(
        map(
            lambda x: x.replace(char1Name, char1Desc).replace(char2Name, char2Desc)
            + ", "
            + sceneDesc,
            frameDescs2,
        )
    )
    print("Diffusion prompts: ", frameDescs)
    return frameDescs


def dialogue_to_gpt_input(dialogue):
    print("Converting dialogue to GPT Input.")
    gpt_url = "https://dashboard.scale.com/spellbook/api/v2/deploy/w533d85"
    headers = {"Authorization": "Bearer clk4hgwlb00rb1axr3kypcr3p"}
    data = {"input": {"input": dialogue}}

    response = requests.post(gpt_url, headers=headers, json=data)
    parsed_image_prompt = response.json()["output"]
    print("GPT input: ", parsed_image_prompt)
    return parsed_image_prompt


def dialogue_cleaned(dialogue):
    comps = dialogue.split("\n")
    return list(map(lambda x: x.split(": ")[1], comps))
