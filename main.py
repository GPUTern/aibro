from langchain.messages import HumanMessage
from langchain_dev_utils.chat_models import register_model_provider
from dotenv import load_dotenv

load_dotenv()

register_model_provider(
    provider_name="mm",
    chat_model="openai-compatible",
    base_url="https://api.minimaxi.com/v1",
)
register_model_provider(
    provider_name="glm",
    chat_model="openai-compatible",
    base_url="https://api.minimaxi.com/v1",
)



if __name__ == "__main__":
    from src.agents.paper_agent import agent
    for mode, chunk in agent.stream({"messages":[HumanMessage("阅读一下./temp下的.md论文，给出总结")]}, stream_mode=['messages', 'updates', 'custom']):
        if mode == 'messages':
            message, metadata = chunk
            print(message.content)
        else:
            print(chunk)
    
    # from src.agents.code_agent.graph import agent
    # for mode, chunk in agent.stream({"messages":[HumanMessage("在./temp/my-app下的贪吃蛇游戏，有点问题，界面宽度太宽了，修复并优化一下")]},
    #                                 config={"recursion_limit":300},
    #                                 stream_mode=['messages', 'updates', 'custom']):
    #     if mode == 'messages':
    #         message, metadata = chunk
    #         print(message.content)
    #     else:
    #         print(chunk)