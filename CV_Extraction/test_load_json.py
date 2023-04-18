import json

with open("/home/aia/Nhat/ChatGPT-Conversation/CV_Extraction/output/output_0.json", "r") as fi:
    text = fi.read()
    fi.close()
output = json.loads(text)
print(output)