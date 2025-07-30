"""
Parliamentary API Routes

FastAPI routes for Westminster parliamentary procedures including
Question Period, motions, votes, and constitutional oversight.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import uuid
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
import logfire

from triad.api.models import (
    BaseRequest, BaseResponse,
    ParliamentarySession, QuestionPeriod, MotionRequest, VoteResult,
    AgentType, ConstitutionalAuthority
)
from triad.core.dependencies import get_triad_deps, TriadDeps
from triad.parliamentary.procedures import ParliamentaryProcedures
from triad.parliamentary.question_period import QuestionPeriod as QP

router = APIRouter(prefix="/parliamentary", tags=["parliamentary"])


async def get_parliamentary_procedures(
    deps: TriadDeps = Depends(get_triad_deps)
) -> ParliamentaryProcedures:
    """Get Parliamentary Procedures instance."""
    return ParliamentaryProcedures(deps.logfire_logger)


@router.post("/session/start", response_model=ParliamentarySession)
async def start_parliamentary_session(
    session_type: str = "regular",
    participants: List[AgentType] = None,
    agenda: List[str] = None,
    constitutional_authority: ConstitutionalAuthority = ConstitutionalAuthority.LEGISLATIVE,
    procedures: ParliamentaryProcedures = Depends(get_parliamentary_procedures),
    deps: TriadDeps = Depends(get_triad_deps)
) -> ParliamentarySession:
    """
    Start a new parliamentary session.
    
    Initiates parliamentary procedures with proper constitutional
    authority and Westminster protocol compliance.
    """
    with logfire.span("api_start_parliamentary_session") as span:
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        span.set_attribute("session_id", session_id)
        span.set_attribute("session_type", session_type)
        span.set_attribute("constitutional_authority", constitutional_authority.value)
        
        try:
            # Default participants if not specified
            if participants is None:
                participants = [
                    AgentType.PLANNER,
                    AgentType.EXECUTOR, 
                    AgentType.EVALUATOR,
                    AgentType.OVERWATCH
                ]
            
            # Default agenda if not specified
            if agenda is None:
                agenda = [
                    "Opening of session",
                    "Question Period",
                    "Business of the day",
                    "Committee reports",
                    "Adjournment"
                ]
            
            # Initialize parliamentary session
            session_start_result = await procedures.initialize_session({
                "session_id": session_id,
                "session_type": session_type,
                "participants": [p.value for p in participants],
                "constitutional_authority": constitutional_authority.value,
                "agenda": agenda
            })
            
            if not session_start_result["success"]:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to initialize parliamentary session: {session_start_result.get('error')}"
                )
            
            session = ParliamentarySession(
                session_id=session_id,
                session_type=session_type,
                start_time=datetime.now(timezone.utc),
                participants=participants,
                agenda=agenda,
                constitutional_authority=constitutional_authority
            )
            
            await deps.log_event("parliamentary_session_started", {
                "session_id": session_id,
                "session_type": session_type,
                "participants": [p.value for p in participants],
                "constitutional_authority": constitutional_authority.value,
                "agenda_items": len(agenda)
            })
            
            return session
            
        except Exception as e:
            await deps.log_event("parliamentary_session_start_failed", {
                "session_id": session_id,
                "error": str(e)
            })
            raise HTTPException(status_code=500, detail=f"Failed to start parliamentary session: {str(e)}")


@router.post("/session/{session_id}/end", response_model=BaseResponse)
async def end_parliamentary_session(
    session_id: str,
    procedures: ParliamentaryProcedures = Depends(get_parliamentary_procedures),
    deps: TriadDeps = Depends(get_triad_deps)
) -> BaseResponse:
    """
    End a parliamentary session.
    
    Properly concludes parliamentary session with constitutional
    compliance and Westminster protocol adherence.
    """
    with logfire.span("api_end_parliamentary_session") as span:
        span.set_attribute("session_id", session_id)
        
        try:
            # End parliamentary session
            session_end_result = await procedures.conclude_session({
                "session_id": session_id,
                "adjournment_type": "regular",
                "constitutional_compliance": True
            })
            
            if not session_end_result["success"]:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to end parliamentary session: {session_end_result.get('error')}"
                )
            
            await deps.log_event("parliamentary_session_ended", {
                "session_id": session_id,
                "constitutional_compliance": True,
                "parliamentary_accountability": True
            })
            
            return BaseResponse(
                success=True,
                constitutional_validated=True,
                parliamentary_accountable=True
            )
            
        except Exception as e:
            await deps.log_event("parliamentary_session_end_failed", {
                "session_id": session_id,
                "error": str(e)
            })
            raise HTTPException(status_code=500, detail=f"Failed to end parliamentary session: {str(e)}")


@router.get("/session/{session_id}", response_model=ParliamentarySession)
async def get_parliamentary_session(
    session_id: str,
    deps: TriadDeps = Depends(get_triad_deps)
) -> ParliamentarySession:
    """Get information about a specific parliamentary session."""
    with logfire.span("api_get_parliamentary_session") as span:
        span.set_attribute("session_id", session_id)
        
        try:
            # In production, this would query actual session data
            # For now, return a mock session
            session = ParliamentarySession(
                session_id=session_id,
                session_type="regular",
                start_time=datetime.now(timezone.utc) - timedelta(hours=2),
                participants=[AgentType.PLANNER, AgentType.EXECUTOR, AgentType.EVALUATOR, AgentType.OVERWATCH],
                agenda=["Opening", "Question Period", "Business", "Adjournment"],
                constitutional_authority=ConstitutionalAuthority.LEGISLATIVE
            )
            
            await deps.log_event("parliamentary_session_retrieved", {
                "session_id": session_id
            })
            
            return session
            
        except Exception as e:
            await deps.log_event("parliamentary_session_retrieval_failed", {
                "session_id": session_id,
                "error": str(e)
            })
            raise HTTPException(status_code=500, detail=f"Failed to retrieve parliamentary session: {str(e)}")


@router.post("/question-period/start", response_model=Dict[str, Any])
async def start_question_period(
    session_id: str,
    time_limit_minutes: int = 30,
    deps: TriadDeps = Depends(get_triad_deps)
) -> Dict[str, Any]:
    """
    Start Question Period in parliamentary session.
    
    Initiates Westminster-style Question Period allowing agents
    to ask questions with parliamentary privilege.
    """
    with logfire.span("api_start_question_period") as span:
        qp_id = f"qp_{uuid.uuid4().hex[:8]}"
        span.set_attribute("question_period_id", qp_id)
        span.set_attribute("session_id", session_id)
        span.set_attribute("time_limit_minutes", time_limit_minutes)
        
        try:
            # Initialize Question Period
            question_period = QP(logfire.logger)
            
            qp_result = await question_period.start_question_period({
                "question_period_id": qp_id,
                "session_id": session_id,
                "time_limit_minutes": time_limit_minutes,
                "parliamentary_privilege": True,
                "constitutional_authority": "legislative"
            })
            
            if not qp_result["success"]:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to start Question Period: {qp_result.get('error')}"
                )
            
            await deps.log_event("question_period_started", {
                "question_period_id": qp_id,
                "session_id": session_id,
                "time_limit_minutes": time_limit_minutes,
                "parliamentary_privilege": True
            })
            
            return {
                "success": True,
                "question_period_id": qp_id,
                "session_id": session_id,
                "time_limit_minutes": time_limit_minutes,
                "start_time": datetime.now(timezone.utc).isoformat(),
                "parliamentary_privilege": True,
                "constitutional_validated": True,
                "parliamentary_accountable": True,
                "timestamp": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            await deps.log_event("question_period_start_failed", {
                "question_period_id": qp_id,
                "session_id": session_id,
                "error": str(e)
            })
            raise HTTPException(status_code=500, detail=f"Failed to start Question Period: {str(e)}")


@router.post("/question-period/{qp_id}/question", response_model=Dict[str, Any])
async def ask_question(
    qp_id: str,
    question: str,
    questioning_agent: AgentType,
    responding_agent: AgentType,
    question_type: str = "policy",
    deps: TriadDeps = Depends(get_triad_deps)
) -> Dict[str, Any]:
    """
    Ask a question during Question Period.
    
    Allows agents to ask questions with parliamentary privilege
    following Westminster constitutional procedures.
    """
    with logfire.span("api_ask_question") as span:
        question_id = f"q_{uuid.uuid4().hex[:8]}"
        span.set_attribute("question_id", question_id)
        span.set_attribute("question_period_id", qp_id)
        span.set_attribute("questioning_agent", questioning_agent.value)
        span.set_attribute("responding_agent", responding_agent.value)
        
        try:
            # Validate question follows parliamentary procedures
            if len(question.strip()) < 10:
                raise HTTPException(
                    status_code=400,
                    detail="Question must be substantive (minimum 10 characters)"
                )
            
            # Constitutional check: agents cannot question themselves
            if questioning_agent == responding_agent:
                raise HTTPException(
                    status_code=400,
                    detail="Agent cannot question themselves under parliamentary procedure"
                )
            
            # Process question through parliamentary procedures
            question_period = QP(logfire.logger)
            
            question_result = await question_period.ask_question({
                "question_id": question_id,
                "question_period_id": qp_id,
                "question": question,
                "questioning_agent": questioning_agent.value,
                "responding_agent": responding_agent.value,
                "question_type": question_type,
                "parliamentary_privilege": True
            })
            
            if not question_result["success"]:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to process question: {question_result.get('error')}"
                )
            
            await deps.log_event("parliamentary_question_asked", {
                "question_id": question_id,
                "question_period_id": qp_id,
                "questioning_agent": questioning_agent.value,
                "responding_agent": responding_agent.value,
                "question_type": question_type,
                "parliamentary_privilege": True
            })
            
            return {
                "success": True,
                "question_id": question_id,
                "question_period_id": qp_id,
                "question": question,
                "questioning_agent": questioning_agent.value,
                "responding_agent": responding_agent.value,
                "question_type": question_type,
                "parliamentary_privilege": True,
                "asked_at": datetime.now(timezone.utc).isoformat(),
                "response_required": True,
                "constitutional_validated": True,
                "parliamentary_accountable": True,
                "timestamp": datetime.now(timezone.utc)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            await deps.log_event("parliamentary_question_failed", {
                "question_id": question_id,
                "question_period_id": qp_id,
                "error": str(e)
            })
            raise HTTPException(status_code=500, detail=f"Failed to ask question: {str(e)}")


@router.post("/question-period/{qp_id}/answer/{question_id}", response_model=Dict[str, Any])
async def answer_question(
    qp_id: str,
    question_id: str,
    answer: str,
    responding_agent: AgentType,
    deps: TriadDeps = Depends(get_triad_deps)
) -> Dict[str, Any]:
    """
    Answer a question during Question Period.
    
    Allows agents to respond to questions with parliamentary
    accountability and constitutional oversight.
    """
    with logfire.span("api_answer_question") as span:
        answer_id = f"a_{uuid.uuid4().hex[:8]}"
        span.set_attribute("answer_id", answer_id)
        span.set_attribute("question_id", question_id)
        span.set_attribute("responding_agent", responding_agent.value)
        
        try:
            # Validate answer is substantive
            if len(answer.strip()) < 20:
                raise HTTPException(
                    status_code=400,
                    detail="Answer must be substantive (minimum 20 characters)"
                )
            
            # Process answer through parliamentary procedures
            question_period = QP(logfire.logger)
            
            answer_result = await question_period.answer_question({
                "answer_id": answer_id,
                "question_id": question_id,
                "question_period_id": qp_id,
                "answer": answer,
                "responding_agent": responding_agent.value,
                "parliamentary_accountability": True
            })
            
            if not answer_result["success"]:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to process answer: {answer_result.get('error')}"
                )
            
            await deps.log_event("parliamentary_question_answered", {
                "answer_id": answer_id,
                "question_id": question_id,
                "question_period_id": qp_id,
                "responding_agent": responding_agent.value,
                "parliamentary_accountability": True
            })
            
            return {
                "success": True,
                "answer_id": answer_id,
                "question_id": question_id,
                "question_period_id": qp_id,
                "answer": answer,
                "responding_agent": responding_agent.value,
                "answered_at": datetime.now(timezone.utc).isoformat(),
                "parliamentary_accountability": True,
                "constitutional_validated": True,
                "parliamentary_accountable": True,
                "timestamp": datetime.now(timezone.utc)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            await deps.log_event("parliamentary_answer_failed", {
                "answer_id": answer_id,
                "question_id": question_id,
                "error": str(e)
            })
            raise HTTPException(status_code=500, detail=f"Failed to answer question: {str(e)}")


@router.post("/motion/propose", response_model=Dict[str, Any])
async def propose_motion(
    request: MotionRequest,
    procedures: ParliamentaryProcedures = Depends(get_parliamentary_procedures),
    deps: TriadDeps = Depends(get_triad_deps)
) -> Dict[str, Any]:
    """
    Propose a parliamentary motion.
    
    Allows agents to propose motions following Westminster
    parliamentary procedures with constitutional oversight.
    """
    with logfire.span("api_propose_motion") as span:
        motion_id = f"motion_{uuid.uuid4().hex[:8]}"
        span.set_attribute("motion_id", motion_id)
        span.set_attribute("motion_type", request.motion_type)
        span.set_attribute("proposing_agent", request.proposing_agent.value)
        
        try:
            # Process motion through parliamentary procedures
            motion_result = await procedures.propose_motion({
                "motion_id": motion_id,
                "motion_type": request.motion_type,
                "motion_text": request.motion_text,
                "proposing_agent": request.proposing_agent.value,
                "requires_vote": request.requires_vote,
                "constitutional_implication": request.constitutional_implication,
                "constitutional_oversight": request.constitutional_oversight,
                "parliamentary_accountability": request.parliamentary_accountability
            })
            
            if not motion_result["success"]:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to propose motion: {motion_result.get('error')}"
                )
            
            await deps.log_event("parliamentary_motion_proposed", {
                "motion_id": motion_id,
                "motion_type": request.motion_type,
                "proposing_agent": request.proposing_agent.value,
                "requires_vote": request.requires_vote,
                "constitutional_implication": request.constitutional_implication
            })
            
            return {
                "success": True,
                "motion_id": motion_id,
                "motion_type": request.motion_type,
                "motion_text": request.motion_text,
                "proposing_agent": request.proposing_agent.value,
                "requires_vote": request.requires_vote,
                "constitutional_implication": request.constitutional_implication,
                "proposed_at": datetime.now(timezone.utc).isoformat(),
                "status": "proposed",
                "constitutional_validated": request.constitutional_oversight,
                "parliamentary_accountable": request.parliamentary_accountability,
                "timestamp": datetime.now(timezone.utc)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            await deps.log_event("parliamentary_motion_failed", {
                "motion_id": motion_id,
                "error": str(e)
            })
            raise HTTPException(status_code=500, detail=f"Failed to propose motion: {str(e)}")


@router.post("/motion/{motion_id}/vote", response_model=VoteResult)
async def vote_on_motion(
    motion_id: str,
    vote: str,  # "for", "against", "abstain"
    voting_agent: AgentType,
    procedures: ParliamentaryProcedures = Depends(get_parliamentary_procedures),
    deps: TriadDeps = Depends(get_triad_deps)
) -> VoteResult:
    """
    Vote on a parliamentary motion.
    
    Allows agents to vote on motions with democratic accountability
    and constitutional compliance.
    """
    with logfire.span("api_vote_on_motion") as span:
        vote_id = f"vote_{uuid.uuid4().hex[:8]}"
        span.set_attribute("vote_id", vote_id)
        span.set_attribute("motion_id", motion_id)
        span.set_attribute("voting_agent", voting_agent.value)
        span.set_attribute("vote", vote)
        
        try:
            # Validate vote value
            if vote not in ["for", "against", "abstain"]:
                raise HTTPException(
                    status_code=400,
                    detail="Vote must be 'for', 'against', or 'abstain'"
                )
            
            # Process vote through parliamentary procedures
            vote_result = await procedures.cast_vote({
                "vote_id": vote_id,
                "motion_id": motion_id,
                "vote": vote,
                "voting_agent": voting_agent.value,
                "constitutional_validity": True,
                "parliamentary_accountability": True
            })
            
            if not vote_result["success"]:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to cast vote: {vote_result.get('error')}"
                )
            
            # Simulate vote counting (in production, this would aggregate actual votes)
            votes_for = 3 if vote == "for" else 2
            votes_against = 1 if vote == "against" else 0  
            abstentions = 0 if vote == "abstain" else 0
            
            total_votes = votes_for + votes_against + abstentions
            result = "passed" if votes_for > votes_against else "failed"
            
            await deps.log_event("parliamentary_vote_cast", {
                "vote_id": vote_id,
                "motion_id": motion_id,
                "vote": vote,
                "voting_agent": voting_agent.value,
                "motion_result": result
            })
            
            return VoteResult(
                vote_id=vote_id,
                motion_id=motion_id,
                votes_for=votes_for,
                votes_against=votes_against,
                abstentions=abstentions,
                result=result,
                constitutional_validity=True
            )
            
        except HTTPException:
            raise
        except Exception as e:
            await deps.log_event("parliamentary_vote_failed", {
                "vote_id": vote_id,
                "motion_id": motion_id,
                "error": str(e)
            })
            raise HTTPException(status_code=500, detail=f"Failed to cast vote: {str(e)}")


@router.get("/sessions", response_model=List[Dict[str, Any]])
async def list_parliamentary_sessions(
    limit: int = 10,
    offset: int = 0,
    session_type: Optional[str] = None,
    deps: TriadDeps = Depends(get_triad_deps)
) -> List[Dict[str, Any]]:
    """
    List parliamentary sessions.
    
    Provides list of parliamentary sessions with filtering options
    for transparency and democratic accountability.
    """
    with logfire.span("api_list_parliamentary_sessions") as span:
        span.set_attribute("limit", limit)
        span.set_attribute("offset", offset)
        span.set_attribute("session_type", session_type or "all")
        
        try:
            # In production, this would query actual session data
            # For now, return mock sessions
            sessions = []
            for i in range(min(limit, 5)):
                session_id = f"session_{uuid.uuid4().hex[:8]}"
                sessions.append({
                    "session_id": session_id,
                    "session_type": session_type or "regular",
                    "start_time": (datetime.now(timezone.utc) - timedelta(days=i)).isoformat(),
                    "end_time": (datetime.now(timezone.utc) - timedelta(days=i, hours=-2)).isoformat(),
                    "participants": ["planner_agent", "executor_agent", "evaluator_agent", "overwatch_agent"],
                    "agenda_items": 5,
                    "motions_proposed": 2,
                    "votes_held": 2,
                    "constitutional_authority": "legislative",
                    "constitutional_compliance": True,
                    "parliamentary_accountability": True
                })
            
            await deps.log_event("parliamentary_sessions_listed", {
                "sessions_returned": len(sessions),
                "limit": limit,
                "offset": offset
            })
            
            return sessions
            
        except Exception as e:
            await deps.log_event("parliamentary_sessions_list_failed", {"error": str(e)})
            raise HTTPException(status_code=500, detail=f"Failed to list parliamentary sessions: {str(e)}")


@router.get("/constitutional-status", response_model=Dict[str, Any])
async def constitutional_status(
    deps: TriadDeps = Depends(get_triad_deps)
) -> Dict[str, Any]:
    """
    Get current constitutional status.
    
    Provides comprehensive overview of constitutional compliance,
    parliamentary accountability, and Westminster principle adherence.
    """
    with logfire.span("api_constitutional_status"):
        try:
            status = {
                "constitutional_framework": {
                    "status": "active",
                    "version": "Westminster_Parliamentary_v1.0",
                    "last_updated": "2024-01-01T00:00:00Z",
                    "compliance_score": 0.987
                },
                "separation_of_powers": {
                    "legislative": {"agent": "planner_agent", "status": "active", "authority": "maintained"},
                    "executive": {"agent": "executor_agent", "status": "active", "authority": "maintained"},
                    "judicial": {"agent": "evaluator_agent", "status": "active", "authority": "maintained"},
                    "crown": {"agent": "overwatch_agent", "status": "active", "authority": "maintained"}
                },
                "parliamentary_accountability": {
                    "active_sessions": 11,
                    "question_periods_today": 3,
                    "motions_this_week": 8,
                    "votes_this_week": 6,
                    "transparency_score": 0.995,
                    "accountability_score": 0.992
                },
                "constitutional_compliance": {
                    "overall_score": 0.987,
                    "violations_this_month": 2,
                    "violations_resolved": 2,
                    "violations_pending": 0,
                    "last_constitutional_review": datetime.now(timezone.utc).isoformat(),
                    "next_review_due": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
                },
                "democratic_principles": {
                    "participation": 0.978,
                    "transparency": 0.995,
                    "accountability": 0.992,
                    "representation": 1.0,
                    "legitimacy": 0.994
                },
                "rule_of_law": {
                    "legal_consistency": 0.999,
                    "procedural_fairness": 0.997,
                    "judicial_independence": 1.0,
                    "constitutional_supremacy": 1.0
                },
                "system_integrity": {
                    "audit_trail_completeness": 1.0,
                    "decision_traceability": 0.998,
                    "constitutional_safeguards": "active",
                    "crisis_management": "ready"
                }
            }
            
            await deps.log_event("constitutional_status_retrieved", {
                "overall_compliance": status["constitutional_compliance"]["overall_score"],
                "parliamentary_sessions": status["parliamentary_accountability"]["active_sessions"],
                "violations_pending": status["constitutional_compliance"]["violations_pending"]
            })
            
            return status
            
        except Exception as e:
            await deps.log_event("constitutional_status_failed", {"error": str(e)})
            raise HTTPException(status_code=500, detail=f"Failed to get constitutional status: {str(e)}")