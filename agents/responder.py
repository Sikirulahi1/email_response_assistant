from langchain_core.prompts import ChatPromptTemplate
from ..core import EmailState, model, EmailMessage, ResponseMessage


llm = model



responder_prompt = ChatPromptTemplate.from_template("""
    You are an email response assistant. Your task is to draft an appropriate response to the email below.
    
    Original Email Subject: {subject}
    Original Email: {content}
    Email Category: {category}
    
    Previous Conversation:
    {conversation_history}
    
    Draft a response that is:
    1. Appropriate for the email category
    2. Professional yet personable
    3. Clear and concise
    4. Addresses all questions or requests in the original email
    5. Maintains continuity with any previous conversation
    
    Response:
    """)

    

def generate_response(state: EmailState):
    # Get previous message context
    previous_messages = state.get("messages", [])
    
    # Format the previous messages as conversation history
    conversation_history = ""
    for msg in previous_messages:
        if isinstance(msg, EmailMessage):
            conversation_history += f"Incoming ({msg.timestamp}): {msg.content}\n\n"
        elif isinstance(msg, ResponseMessage):
            conversation_history += f"Response ({msg.timestamp}, {msg.category}): {msg.content}\n\n"
    

    chain = responder_prompt | llm

    response = chain.invoke({
        "content": state["email"].content,
        "subject": state["email"].subject,
        "category": state["email_category"],
        "conversation_history": conversation_history
    }).content

    return {'response_draft': response}