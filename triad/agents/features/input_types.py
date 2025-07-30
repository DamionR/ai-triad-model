"""
Input Types for Westminster Parliamentary AI System

Defines all data models, enums, and types used across the input handling system
including input types, content types, security classifications, and validation results.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field, validator

from triad.tools.governance.governance_toolsets import AuthorityLevel


class InputType(Enum):
    """Types of input content for parliamentary analysis."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    STRUCTURED_DATA = "structured_data"


class ParliamentaryContentType(Enum):
    """Specific types of parliamentary content."""
    BILL_TEXT = "bill_text"
    HANSARD_TRANSCRIPT = "hansard_transcript"
    COMMITTEE_REPORT = "committee_report"
    CONSTITUTIONAL_DOCUMENT = "constitutional_document"
    LEGISLATIVE_AMENDMENT = "legislative_amendment"
    PARLIAMENTARY_DEBATE = "parliamentary_debate"
    QUESTION_PERIOD = "question_period"
    VOTING_RECORD = "voting_record"
    CITIZEN_PETITION = "citizen_petition"
    GOVERNMENT_DOCUMENT = "government_document"
    COURT_DECISION = "court_decision"
    POLICY_PROPOSAL = "policy_proposal"


class SecurityClassification(Enum):
    """Security classifications for parliamentary content."""
    UNCLASSIFIED = "unclassified"
    PROTECTED_A = "protected_a"
    PROTECTED_B = "protected_b"
    PROTECTED_C = "protected_c"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"


class ParliamentaryInput(BaseModel):
    """Structured input for parliamentary AI analysis."""
    content: Union[str, bytes]
    input_type: InputType
    content_type: ParliamentaryContentType
    title: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    date_created: Optional[datetime] = None
    constitutional_authority: Optional[AuthorityLevel] = None
    security_classification: SecurityClassification = SecurityClassification.UNCLASSIFIED
    metadata: Dict[str, Any] = Field(default_factory=dict)
    validation_required: bool = True
    
    @validator('content')
    def validate_content(cls, v, values):
        """Validate content based on input type."""
        input_type = values.get('input_type')
        
        if input_type == InputType.TEXT and not isinstance(v, str):
            raise ValueError("Text input must be a string")
        elif input_type in [InputType.IMAGE, InputType.AUDIO, InputType.VIDEO, InputType.DOCUMENT]:
            if not isinstance(v, (bytes, str)):
                raise ValueError("Media input must be bytes or URL string")
        
        return v


class InputValidationResult(BaseModel):
    """Result of input validation."""
    valid: bool
    validation_type: str
    issues: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    constitutional_compliance: bool = True
    security_cleared: bool = True
    recommended_actions: List[str] = Field(default_factory=list)
    validated_by: Optional[str] = None
    validation_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))