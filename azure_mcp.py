from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import json, os, logging, asyncio
from dotenv import load_dotenv

# Setup logging and load environment variables
logger = logging.getLogger(__name__)
load_dotenv()

# Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL", "gpt-4o")

# Initialize Azure credentials
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)

async def run():
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT, 
            api_version="2024-04-01-preview", 
            azure_ad_token_provider=token_provider
        )

    # MCP client configurations
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@azure/mcp@latest", "server", "start"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            for tool in tools.tools: print(tool.name)

            # Format tools for Azure OpenAI
            available_tools = [{
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            } for tool in tools.tools]

            # Start conversational loop
            messages = []
            while True:
                try:
                    user_input = input("\nPrompt: ")
                    messages.append({"role": "user", "content": user_input})

                    # First API call with tool configuration
                    response = client.chat.completions.create(
                        model = AZURE_OPENAI_MODEL,
                        messages = messages,
                        tools = available_tools)

                    # Process the model's response
                    response_message = response.choices[0].message
                    messages.append(response_message)

                    # Handle function calls
                    if response_message.tool_calls:
                        for tool_call in response_message.tool_calls:
                                function_args = json.loads(tool_call.function.arguments)
                                result = await session.call_tool(tool_call.function.name, function_args)

                                # Add the tool response to the messages
                                messages.append({
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",
                                    "name": tool_call.function.name,
                                    "content": result.content,
                                })
                    else:
                        logger.info("No tool calls were made by the model")

                    # Get the final response from the model
                    final_response = client.chat.completions.create(
                        model = AZURE_OPENAI_MODEL,
                        messages = messages,
                        tools = available_tools)

                    for item in final_response.choices:
                        print(item.message.content)
                except Exception as e:
                    logger.error(f"Error in conversation loop: {e}")
                    print(f"An error occurred: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())