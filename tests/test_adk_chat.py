#!/usr/bin/env python3
"""
Test ADK Chat Functionality
===========================

A simple test to verify the ADK chat functionality works correctly.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'  # Go up one more level since we're in tests/
    if env_path.exists():
        load_dotenv(env_path)
        print("✅ Environment variables loaded from .env file")
except ImportError:
    pass

import asyncio
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner


async def test_simple_chat():
    """Test basic ADK chat functionality."""
    
    # Check API key
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return
    
    print(f"✅ Using API key: {api_key[:10]}...{api_key[-4:]}")
    
    # Create a simple agent
    agent = Agent(
        name="test_agent",
        model="gemini-2.0-flash",
        description="A simple test agent",
        instruction="You are a helpful assistant. Keep responses brief and friendly."
    )
    
    # Set up session
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test_app",
        session_id="test_session",
        user_id="test_user"
    )
    
    # Create runner
    runner = Runner(
        agent=agent,
        session_service=session_service,
        app_name="test_app"
    )
    
    # Test message
    message = "Hello! What is 2+2?"
    print(f"\n🗣️  User: {message}")
    
    try:
        # Try different API calls to find the correct one
        from google.genai import types
        
        # Create content
        content = types.Content(parts=[types.Part(text=message)])
        
        print("🤖 Agent: ", end="")
        events = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session",
            new_message=content
        ):
            events.append(event)
            print(f"Event type: {type(event)}, attributes: {dir(event)}")
            
            if hasattr(event, 'content') and event.content:
                print(f"Content: {event.content}")
            if hasattr(event, 'message') and event.message:
                print(f"Message: {event.message}")
            if hasattr(event, 'response') and event.response:
                print(f"Response: {event.response}")
                
            if event.is_final_response():
                print(f"Final response event: {event}")
                # Try different ways to extract text
                if hasattr(event, 'content'):
                    print(f"Final content: {event.content}")
                break
                
    except Exception as e:
        print(f"❌ Chat failed: {e}")
        print(f"Error type: {type(e)}")


if __name__ == "__main__":
    asyncio.run(test_simple_chat())
