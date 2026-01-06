from google.adk.agents.llm_agent import Agent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.sessions import InMemorySessionService
from google.adk.tools.tool_context import ToolContext


# Create a NEW session service instance for this state demonstration
session_service_stateful = InMemorySessionService()
SESSION_ID_STATEFUL = "session_state_demo_001"
USER_ID_STATEFUL = "user_state_demo"
APP_NAME = "pricing_agent_app"


initial_state = {
    "user_preference_temperature_unit": "Celsius"
}

# Create the session, providing the initial state
session_stateful = session_service_stateful.create_session(
    app_name=APP_NAME, # Use the consistent app name
    user_id=USER_ID_STATEFUL,
    session_id=SESSION_ID_STATEFUL,
    state=initial_state # <<< Initialize state during creation
)


search_agent = Agent(
    model='gemini-3-flash-preview',
    name='SearchAgent',
    description="Agent that performs Google Searches",
    instruction="You're a spealist in Google Search",
    tools=[google_search]
)

amazon_agent = Agent(
    model='gemini-3-flash-preview',
    name='amazon_agent',
    description="You are a subagent that checks the current price of a certain product by checking on Amazon",
    instruction="You visit the url https://www.amazon.in/s?k=<product_name> where product_name is input by consumer. For each product you go to all the website, find the price that matches the user provided input. While matching you need to make sure that you match the user requested unit of measurement, quantity and product name and actual product link for which the price is being shared. if same quantity is not available you find an alternative quantity but you never change the product, the final outcome that you share to your parent agent is in following format - item_name, item_price, item_quantity, item price/quantity, purchase_link",
    tools=[AgentTool(agent=search_agent)],
    output_key="amazon_response"
)

blinkit_agent = Agent(
    model='gemini-3-flash-preview',
    name='blinkit_agent',
    description="You are a subagent that checks the current price of a certain product by checking on Blinkit",
    instruction=
    " You visit the url https://blinkit.com/s/?q=<product_name> where product_name is input by consumer" \
    " For each product you go to all the website, find the price that matches the user provided input " \
    "- while matching you need to make sure that you match the user requested unit of measurement, quantity and product name and actual product link for which the price is being shared" \
    "if same quantity is not available you find an alternative quantity but you never change the product, the final outcome that you share to your parent agent is in following format " \
    "item_name, item_price, item_quantity, item price/qutantity, purchase_link",
    tools=[AgentTool(agent=search_agent)],
    output_key="blinkit_response"
)


zepto_agent = Agent(
    model='gemini-3-flash-preview',
    name='zepto_agent',
    description="You are a subagent that checks the current price of a certain product by checking on Zepto",
    instruction=
    " You visit the url https://www.zepto.com/search?query=<product_name> where product_name is input by consumer" \
    " For each product you go to all the website, find the price that matches the user provided input " \
    "- while matching you need to make sure that you match the user requested unit of measurement, quantity and product name and actual product link for which the price is being shared" \
    "if same quantity is not available you find an alternative quantity but you never change the product, the final outcome that you share to your parent agent is in following format " \
    "item_name, item_price, item_quantity, item price/qutantity, purchase_link",
    tools=[AgentTool(agent=search_agent)],
    output_key="zepto_response"
)


merger_agent = Agent(
    model='gemini-3-flash-preview',
    name='merger_agent',
    description="Summarise best price of a certain product by merging output from multiple subagents",
    instruction="You are a summarizer agent that tells the user the best price for the product by comparing the output from multiple subagents." \
    "Output fomat is a table with following rows, columns are names of companies whose information is displayed" \
    "Item name" \
    "Item price" \
    "Item quantity" \
    "Item price/qty " \
    "Purchase link" ,
)


parallel_research_agent = ParallelAgent(
     name="ParallelPricingAgent",
     sub_agents=[amazon_agent, blinkit_agent, zepto_agent],
     description="Runs multiple pricing agents in parallel to gather information."
)


input_agent = Agent(
    model='gemini-3-flash-preview',
    name='input_agent',
    description="Agent that collects user input for product pricing",
    instruction="You collect the product name, quantity, unit of measurement from the user to proceed with pricing research.",
)


sequential_pipeline_agent = SequentialAgent(
     name="sequqential_pricing_agent",
     sub_agents=[input_agent, parallel_research_agent, merger_agent],
     description="Coordinates parallel pricing and synthesizes the results."
)

root_agent = sequential_pipeline_agent


