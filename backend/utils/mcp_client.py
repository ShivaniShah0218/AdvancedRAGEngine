"""
This module defines the MCP client for calling tools with the MCP protocol with the backend defined in the .env file and exposes a function to call an MCP tool with a given payload
"""

import os
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from backend.logging_config import get_logger

load_dotenv()

logger = get_logger(__name__)

MCP_URL = os.getenv("MCP_URL")


async def call_mcp_tool(tool_name: str, payload: dict):
    """
    Calls an MCP tool with the given payload
    """
    async with streamablehttp_client(MCP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            logger.info(f"MCP client connected to {MCP_URL}")
            logger.info("Initializing MCP handshake")
            await session.initialize()
            logger.info(f"Calling mcp tool {tool_name} at {MCP_URL}")
            result = await session.call_tool(tool_name, payload)
            return result