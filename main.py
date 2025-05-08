from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing import Dict, TypedDict, List, Annotated
from .core import EmailState, EmailMessage
import os
from dotenv import load_dotenv
import uuid
from dotenv import load_dotenv
from .agents import classify_email, generate_response, review_response
import datetime
from .core import model

load_dotenv()

llm = model


# Create a memory saver
memory = MemorySaver()

workflow = StateGraph(EmailState)


# Add nodes to the graph
workflow.add_node("classifier", classify_email)
workflow.add_node("responder", generate_response)
workflow.add_node("reviewer", review_response)

# Connect the nodes
workflow.add_edge(START, 'classifier')
workflow.add_edge("classifier", "responder")
workflow.add_edge("responder", "reviewer")
workflow.add_edge("reviewer", END)

# Compile the graph
app = workflow.compile(checkpointer=memory)



def process_email(email_content, subject="No Subject", sender="user@example.com", thread_id=None):
    """Process an incoming email and generate a response using memory."""
    
    # Create a unique thread ID for this conversation if needed
    # thread_id = None  # You can retrieve an existing thread ID here if you have one
    
    if not thread_id:
        thread_id = str(uuid.uuid4())
    
    # Create an EmailMessage object
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    email = EmailMessage(
        content=email_content,
        subject=subject,
        sender=sender,
        timestamp=current_time
    )

    try:
        # Try to retrieve existing state from memory
        existing_state = memory.load(thread_id)
        message_history = existing_state.get("message_history", [])
    except:
        # If no existing state, start with empty history
        message_history = []
    
    # Initialize the state
    initial_state = {
        "email": email,
        "email_category": "",
        "response_draft": "",
        "final_response": None,
        "messages": message_history # This will be populated from memory if the thread exists
    }
    
    # Run the graph with memory
    # result = app.invoke(initial_state, config={"configurable": {"thread_id": thread_id}})

    import time
    from httpx import HTTPStatusError

    for attempt in range(5):
        try:
            result = app.invoke(initial_state, config={"configurable": {"thread_id": thread_id}})
            break
        except HTTPStatusError as e:
            if e.response.status_code == 429:
                wait = 2 ** attempt  # 1s, 2s, 4s, 8s…
                print(f"Rate limited—waiting {wait}s before retrying")
                time.sleep(wait)
            else:
                raise
    else:
        raise RuntimeError("Failed after retries due to rate limits")
    
    return result["final_response"], result["email_category"], thread_id


if __name__ == "__main__":
    # Example usage
    sample_email = """
    Hello,
    I'm interested in your product but I have a few questions before making a purchase.
    1. Do you offer discounts for bulk orders?
    2. What's your return policy?
    3. How long does shipping typically take?
    Thanks,
    John
    """
    
    response, category, thread_id = process_email(
        email_content=sample_email,
        subject="Product Questions",
        sender="john@example.com"
    )
    
    print(f"Email Category: {category}")
    print(f"\nGenerated Response:\n{response.content}")
    
    # # Example of a follow-up email (using the same thread_id)
    # follow_up = """
    # Thanks for the quick reply!
    # One more question - do you ship internationally?
    # Regards,
    # John
    # """
    
    # # Process the follow-up using the same thread_id
    # response2, category2, thread_id = process_email(
    #     email_content=follow_up,
    #     subject="Re: Product Questions",
    #     sender="john@example.com"
    # )
    
    # print(f"\nFollow-up Email Category: {category2}")
    # print(f"\nFollow-up Response:\n{response2.content}")