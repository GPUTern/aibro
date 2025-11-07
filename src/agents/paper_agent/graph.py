"""Define a React agent.
"""
from langchain.agents import create_agent
from langchain_dev_utils.chat_models import load_chat_model

from src.agents.paper_agent.prompts import SYSTEM_PROMPT
from src.agents.paper_agent.tools import PAPER_TOOLS, FILE_TOOLS
from src.agents.paper_agent.context import Context


model = load_chat_model("minimax:MiniMax-M2")

agent = create_agent(
    model=model,
    tools=PAPER_TOOLS+FILE_TOOLS,
    context_schema=Context,
    system_prompt=SYSTEM_PROMPT
)


if __name__ == "__main__":
    pass


