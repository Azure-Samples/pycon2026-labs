from dotenv import load_dotenv
from os import environ
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from service import TravelAgentTools as agent_tools

load_dotenv(override=False)


chat: AzureChatOpenAI | None = None
agent_with_chat_history = None


def get_chat_client() -> AzureChatOpenAI:
    azure_endpoint = environ.get("AZURE_OPENAI_ENDPOINT")
    azure_api_key = environ.get("AZURE_OPENAI_API_KEY")
    azure_api_version = environ.get("AZURE_OPENAI_API_VERSION")
    azure_deployment = (
        environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT")
        or environ.get("AZURE_OPENAI_DEPLOYMENT")
    )

    missing = []
    if not azure_endpoint:
        missing.append("AZURE_OPENAI_ENDPOINT")
    if not azure_api_key:
        missing.append("AZURE_OPENAI_API_KEY")
    if not azure_api_version:
        missing.append("AZURE_OPENAI_API_VERSION")
    if not azure_deployment:
        missing.append("AZURE_OPENAI_CHAT_DEPLOYMENT")

    if missing:
        missing_vars = ", ".join(missing)
        raise ValueError(
            f"Missing required Azure OpenAI settings: {missing_vars}. "
            "Set them in your environment or .env file before starting the API."
        )

    return AzureChatOpenAI(
        azure_endpoint=azure_endpoint,
        api_key=azure_api_key,
        api_version=azure_api_version,
        azure_deployment=azure_deployment,
        temperature=0,
    )

class _AgentWrapper:
    """Adapts a LangGraph agent to the invoke({"input": ...}, config) interface."""

    def __init__(self, agent):
        self._agent = agent

    def invoke(self, inputs: dict, config: dict | None = None) -> dict:
        session_id = (config or {}).get("configurable", {}).get("session_id", "default")
        result = self._agent.invoke(
            {"messages": [HumanMessage(content=inputs["input"])]},
            config={"configurable": {"thread_id": session_id}},
        )
        return {"output": result["messages"][-1].content}


def LLM_init():
    global chat, agent_with_chat_history
    chat = get_chat_client()
    tools = [agent_tools.vacation_lookup, agent_tools.itinerary_lookup, agent_tools.book_cruise]

    system_prompt = (
        "You are a helpful and friendly travel assistant for a cruise company. "
        "For any question about destinations, cruises, ships, itineraries, packages, amenities, schedules, or booking, you must use the available tools before answering. "
        "Do not answer those questions from general knowledge or make up information when tool results are available. "
        "Use vacation_lookup for destination and cruise discovery questions. "
        "Use itinerary_lookup for ship itinerary, package, room, and schedule questions. "
        "Use book_cruise only when the user is asking to make a booking. "
        "If the user wants to book a cruise, collect the passenger's real name and the selected room before calling the booking tool. "
        "If a tool does not return enough information, say that clearly instead of inventing details. "
        "Answer should be embedded in html tags."
    )

    checkpointer = MemorySaver()
    agent = create_react_agent(chat, tools, prompt=system_prompt, checkpointer=checkpointer)
    agent_with_chat_history = _AgentWrapper(agent)


LLM_init()