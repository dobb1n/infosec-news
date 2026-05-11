import vertexai
from vertexai.preview import reasoning_engines

# TODO(developer): Update and un-comment below line
PROJECT_ID = "the-tinkering-shed"
vertexai.init(project=PROJECT_ID, location="europe-west2")

reasoning_engine_list = reasoning_engines.ReasoningEngine.list()
print(reasoning_engine_list)

for agent in reasoning_engine_list:
    print(agent)

""" reasoning_engine = reasoning_engines.ReasoningEngine(reasoning_engine_id)
reasoning_engine.delete() """