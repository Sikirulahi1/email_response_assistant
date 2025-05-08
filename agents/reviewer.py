from langchain_core.prompts import ChatPromptTemplate
from ..core import EmailState, model, EmailMessage, ResponseMessage

import datetime

llm = model

def review_response(state: EmailState):
    """Reviews and potentially refines the draft response."""
    
    
    # Current timestamp
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    reviewer_prompt = ChatPromptTemplate.from_template("""
    You are an email response reviewer. Review the following draft response to ensure it's:
    1. Appropriate for the email category ({category})
    2. Professional and courteous
    3. Clear and addresses all points in the original email
    4. Maintains appropriate context from previous conversation
    5. Free of errors (grammar, spelling, tone)
    
    Original Email: {content}
    Draft Response: {response_draft}
    
    If the response is good, respond with "APPROVED" followed by the response.
    If it needs changes, respond with "REVISED" followed by your improved version.
    """)
    
    chain = reviewer_prompt | llm
    
    review_result = chain.invoke({
        "content": state["email"].content,
        "category": state["email_category"],
        "response_draft": state["response_draft"]
    }).content
    
    if review_result.startswith("APPROVED"):
        final_content = state["response_draft"]
    else:
        # Extract the revised response (everything after "REVISED")
        final_content = review_result.split("REVISED", 1)[1].strip()
    
    # Create a ResponseMessage object
    final_response = ResponseMessage(
        content=final_content,
        category=state["email_category"],
        timestamp=current_time
    )
    
    # Add both the incoming email and the response to messages
    new_messages = [state["email"], final_response]
    
    return {
        "final_response": final_response,
        "messages": new_messages
    }