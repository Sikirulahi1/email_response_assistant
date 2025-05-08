from langchain_core.prompts import ChatPromptTemplate
from ..core import EmailState, model, EmailMessage, ResponseMessage



llm = model

classifier_prompt = ChatPromptTemplate.from_template("""
    You are an email classifier. Analyze the following email and determine its category:
    - personal: Emails from friends, family, or about personal matters
    - business: Professional emails regarding work, partnerships, or business opportunities
    - support: Customer support or technical assistance requests
    - marketing: Promotional emails or marketing content
    - urgent: Emails requiring immediate attention
    - other: Any other category
    
    {conversation_context}
    
    Current Email Subject: {subject}
    Current Email: {content}
    
    Provide ONLY the category name as your response, nothing else.
    """)



def classify_email(state: EmailState):
    """Classifies the incoming email"""

    # Get previous message content

    previous_messages = state.get("messages", [])
    conversation_context = ""

    if previous_messages:

        conversation_context = "Previous Conversation context \n"
        for msg in previous_messages:
            if isinstance(msg, EmailMessage):
                conversation_context += f"Email: {msg.subject} - {msg.content}\n"
            elif isinstance(msg, ResponseMessage):
                conversation_context += f"Response ({msg.category}): {msg.content}\n"


    chain = classifier_prompt | llm
    email_category = chain.invoke({
        "content": state["email"].content,
        "subject": state["email"].subject,
        "conversation_context": conversation_context
    }).content.strip().lower()

    return {"email_category" : email_category}