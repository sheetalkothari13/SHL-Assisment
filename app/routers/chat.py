from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.session import ConversationalSession, SessionMessage
from app.schemas.chat import ChatRequest, ChatResponse, SessionSummary, Message
from app.agent.recommender import AssessmentRecommenderAgent
from app.logging_config import logger
from typing import List

router = APIRouter(tags=["Conversational Advisor"])

# Initialize singleton recommender agent
agent = AssessmentRecommenderAgent()

@router.post("/chat", response_model=ChatResponse)
async def chat_stateless(request: ChatRequest):
    """Stateless chat turn runner (compatible with original CLI and testing schemas)"""
    history = [{"role": m.role, "content": m.content} for m in request.messages]
    result = agent.process_conversation(history)
    return ChatResponse(
        reply=result["reply"],
        recommendations=result["recommendations"],
        end_of_conversation=result["end_of_conversation"]
    )

@router.post("/sessions", response_model=SessionSummary)
async def create_session(db: AsyncSession = Depends(get_db)):
    """Create a new persistent, stateful conversational session"""
    session = ConversationalSession()
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    # Save the initial agent welcome greeting message
    greeting = SessionMessage(
        session_id=session.id,
        role="assistant",
        content=(
            "Hello! I am your SHL Assessment Advisor. I can help you select "
            "the most suitable pre-employment assessments for your hiring needs.\n\n"
            "To begin, could you tell me: What job role or business function are you hiring for, "
            "and what seniority level (Entry, Mid, Senior)?"
        )
    )
    db.add(greeting)
    await db.commit()
    
    return SessionSummary(
        id=session.id,
        title=session.title,
        status=session.status,
        turn_count=session.turn_count,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat()
    )

@router.get("/sessions", response_model=List[SessionSummary])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    """List all saved chat sessions"""
    result = await db.execute(
        select(ConversationalSession).order_by(ConversationalSession.updated_at.desc())
    )
    sessions = result.scalars().all()
    return [
        SessionSummary(
            id=s.id,
            title=s.title,
            status=s.status,
            turn_count=s.turn_count,
            created_at=s.created_at.isoformat(),
            updated_at=s.updated_at.isoformat()
        ) for s in sessions
    ]

@router.get("/sessions/{session_id}")
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve full chat history and metadata of a specific session"""
    result = await db.execute(
        select(ConversationalSession).filter(ConversationalSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Conversational session not found.")
    return session.to_dict()

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a conversational session"""
    result = await db.execute(
        select(ConversationalSession).filter(ConversationalSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Conversational session not found.")
    
    await db.delete(session)
    await db.commit()
    return {"status": "success", "message": f"Session {session_id} successfully deleted."}

@router.post("/sessions/{session_id}/message", response_model=ChatResponse)
async def post_session_message(session_id: str, message: Message, db: AsyncSession = Depends(get_db)):
    """Post a new message to an existing session, run the advisor, and persist the stateful response"""
    # 1. Fetch Session
    result = await db.execute(
        select(ConversationalSession).filter(ConversationalSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Conversational session not found.")
        
    # 2. Validate Turn Limit
    if session.turn_count >= 8:
        raise HTTPException(status_code=400, detail="The turn limit of 8 exchanges has been exceeded.")
        
    # 3. Save User Message
    user_msg = SessionMessage(
        session_id=session.id,
        role="user",
        content=message.content
    )
    db.add(user_msg)
    await db.flush() # Flush to get user_msg ID
    
    # 4. Fetch full conversation history context
    history_result = await db.execute(
        select(SessionMessage)
        .filter(SessionMessage.session_id == session_id)
        .order_by(SessionMessage.id.asc())
    )
    history_messages = history_result.scalars().all()
    history = [{"role": m.role, "content": m.content} for m in history_messages]
    
    # 5. Run LLM Agent with full session context
    reply_text, recommendations, end_of_conv = agent.chat(history)
    
    # 6. Save Agent Response
    assistant_msg = SessionMessage(
        session_id=session.id,
        role="assistant",
        content=reply_text
    )
    assistant_msg.recommendations = recommendations
    db.add(assistant_msg)
    
    # 7. Update Session state
    session.turn_count += 1
    session.status = "Requirement Gathering"
    if end_of_conv:
        session.status = "Shortlisted"
        
    # Set dynamic title from user's first query
    if session.title == "New Assessment Campaign" and len(message.content) > 5:
        clean_title = message.content.strip()
        session.title = clean_title[:40] + ("..." if len(clean_title) > 40 else "")
        
    await db.commit()
    await db.refresh(session)
    
    return ChatResponse(
        reply=reply_text,
        recommendations=recommendations,
        end_of_conversation=end_of_conv
    )
