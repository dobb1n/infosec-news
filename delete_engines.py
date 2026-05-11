import vertexai
from vertexai.preview import reasoning_engines

# TODO(developer): Update and un-comment below line
PROJECT_ID = "the-tinkering-shed"
vertexai.init(project=PROJECT_ID, location="europe-west2")

reasoning_engine_ids = [
    "1399968573228580864",
    "1651888677384617984",
    "1790092890949550080",
    "2941888495649554432",
    "3145676378788069376",
    "3983345909478981632",
    "7930750982869221376",
    "9022873892506566656",
]

for reasoning_engine_id in reasoning_engine_ids:
    reasoning_engine = reasoning_engines.ReasoningEngine(reasoning_engine_id)
    reasoning_engine.delete()