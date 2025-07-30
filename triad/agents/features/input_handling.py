"""
Input Handling for Westminster Parliamentary AI System

Implements comprehensive input handling for multimodal parliamentary content
including documents, images, audio, video, and structured parliamentary data.
"""

import asyncio
import base64
import mimetypes
from typing import Dict, List, Optional, Any, Union, BinaryIO
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
import logfire
from pydantic import BaseModel, Field, validator
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import (
    ImageUrl, 
    BinaryContent, 
    AudioUrl, 
    VideoUrl, 
    DocumentUrl
)

from triad.models.model_config import get_model_config
from triad.tools.parliamentary_toolsets import ParliamentaryAuthority
from triad.agents.enhanced_agents import EnhancedParliamentaryDeps
from triad.core.logging import get_logfire_config


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
    constitutional_authority: Optional[ParliamentaryAuthority] = None
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


class ParliamentaryInputHandler:
    """
    Comprehensive input handler for Westminster Parliamentary AI System.
    
    Handles multimodal content including text, images, documents, audio, and video
    with appropriate parliamentary validation and constitutional oversight.
    """
    
    def __init__(self):
        self.logger = get_logfire_config()
        self.model_config = get_model_config()
        self.supported_formats = self._get_supported_formats()
    
    def _get_supported_formats(self) -> Dict[InputType, List[str]]:
        """Get supported file formats by input type."""
        return {
            InputType.TEXT: ['.txt', '.md', '.rtf'],
            InputType.IMAGE: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
            InputType.AUDIO: ['.mp3', '.wav', '.m4a', '.ogg', '.flac'],
            InputType.VIDEO: ['.mp4', '.avi', '.mov', '.wmv', '.mkv', '.webm'],
            InputType.DOCUMENT: ['.pdf', '.doc', '.docx', '.odt', '.html']
        }
    
    async def validate_parliamentary_input(
        self,
        input_data: ParliamentaryInput,
        constitutional_authority: Optional[ParliamentaryAuthority] = None
    ) -> InputValidationResult:
        """
        Validate parliamentary input for constitutional compliance and security.
        
        Args:
            input_data: Parliamentary input to validate
            constitutional_authority: Authority requesting validation
            
        Returns:
            Validation result with compliance assessment
        """
        
        try:
            with self.logger.parliamentary_session_span(
                f"input-validation-{input_data.input_type.value}",
                [constitutional_authority.value if constitutional_authority else "system"]
            ) as span:
                
                validation_result = InputValidationResult(
                    valid=True,
                    validation_type="parliamentary_input",
                    validated_by=constitutional_authority.value if constitutional_authority else "system"
                )
                
                # Security classification validation
                if not self._validate_security_clearance(
                    input_data.security_classification, 
                    constitutional_authority
                ):
                    validation_result.valid = False
                    validation_result.security_cleared = False
                    validation_result.issues.append(
                        f"Insufficient clearance for {input_data.security_classification.value} content"
                    )
                
                # Content type validation
                content_validation = self._validate_content_type(input_data)
                if not content_validation["valid"]:
                    validation_result.valid = False
                    validation_result.issues.extend(content_validation["issues"])
                
                # Constitutional compliance check
                constitutional_check = await self._check_constitutional_compliance(input_data)
                validation_result.constitutional_compliance = constitutional_check["compliant"]
                if not constitutional_check["compliant"]:
                    validation_result.issues.extend(constitutional_check["violations"])
                
                # Format validation for media content
                if input_data.input_type != InputType.TEXT:
                    format_validation = self._validate_media_format(input_data)
                    if not format_validation["valid"]:
                        validation_result.valid = False
                        validation_result.issues.extend(format_validation["issues"])
                
                # Generate recommendations
                if not validation_result.valid:
                    validation_result.recommended_actions = self._generate_remediation_actions(
                        validation_result.issues
                    )
                
                # Log validation
                self.logger.log_parliamentary_event(
                    event_type="input_validation_completed",
                    data={
                        "input_type": input_data.input_type.value,
                        "content_type": input_data.content_type.value,
                        "valid": validation_result.valid,
                        "constitutional_compliant": validation_result.constitutional_compliance,
                        "security_cleared": validation_result.security_cleared,
                        "issues_count": len(validation_result.issues)
                    },
                    authority=constitutional_authority.value if constitutional_authority else "system"
                )
                
                span.set_attribute("validation.valid", validation_result.valid)
                span.set_attribute("validation.input_type", input_data.input_type.value)
                span.set_attribute("validation.content_type", input_data.content_type.value)
                span.set_attribute("validation.issues_count", len(validation_result.issues))
                
                return validation_result
                
        except Exception as e:
            self.logger.log_parliamentary_event(
                event_type="input_validation_error",
                data={
                    "error": str(e),
                    "input_type": input_data.input_type.value
                },
                authority=constitutional_authority.value if constitutional_authority else "system"
            )
            
            return InputValidationResult(
                valid=False,
                validation_type="parliamentary_input",
                issues=[f"Validation error: {e}"],
                constitutional_compliance=False,
                security_cleared=False
            )
    
    def _validate_security_clearance(
        self,
        classification: SecurityClassification,
        authority: Optional[ParliamentaryAuthority]
    ) -> bool:
        """Validate security clearance for content access."""
        
        if not authority:
            # Only allow unclassified content without authority
            return classification == SecurityClassification.UNCLASSIFIED
        
        # Authority-based clearance levels
        clearance_levels = {
            ParliamentaryAuthority.CROWN: [
                SecurityClassification.UNCLASSIFIED,
                SecurityClassification.PROTECTED_A,
                SecurityClassification.PROTECTED_B,
                SecurityClassification.PROTECTED_C,
                SecurityClassification.CONFIDENTIAL,
                SecurityClassification.SECRET,
                SecurityClassification.TOP_SECRET
            ],
            ParliamentaryAuthority.JUDICIAL: [
                SecurityClassification.UNCLASSIFIED,
                SecurityClassification.PROTECTED_A,
                SecurityClassification.PROTECTED_B,
                SecurityClassification.PROTECTED_C,
                SecurityClassification.CONFIDENTIAL
            ],
            ParliamentaryAuthority.EXECUTIVE: [
                SecurityClassification.UNCLASSIFIED,
                SecurityClassification.PROTECTED_A,
                SecurityClassification.PROTECTED_B,
                SecurityClassification.PROTECTED_C,
                SecurityClassification.CONFIDENTIAL
            ],
            ParliamentaryAuthority.LEGISLATIVE: [
                SecurityClassification.UNCLASSIFIED,
                SecurityClassification.PROTECTED_A,
                SecurityClassification.PROTECTED_B
            ],
            ParliamentaryAuthority.SPEAKER: [
                SecurityClassification.UNCLASSIFIED,
                SecurityClassification.PROTECTED_A
            ],
            ParliamentaryAuthority.CLERK: [
                SecurityClassification.UNCLASSIFIED,
                SecurityClassification.PROTECTED_A
            ]
        }
        
        authorized_levels = clearance_levels.get(authority, [SecurityClassification.UNCLASSIFIED])
        return classification in authorized_levels
    
    def _validate_content_type(self, input_data: ParliamentaryInput) -> Dict[str, Any]:
        """Validate content type against input type."""
        
        validation = {"valid": True, "issues": []}
        
        # Check if content type matches input type expectations
        text_content_types = [
            ParliamentaryContentType.BILL_TEXT,
            ParliamentaryContentType.HANSARD_TRANSCRIPT,
            ParliamentaryContentType.LEGISLATIVE_AMENDMENT,
            ParliamentaryContentType.POLICY_PROPOSAL
        ]
        
        document_content_types = [
            ParliamentaryContentType.COMMITTEE_REPORT,
            ParliamentaryContentType.CONSTITUTIONAL_DOCUMENT,
            ParliamentaryContentType.GOVERNMENT_DOCUMENT,
            ParliamentaryContentType.COURT_DECISION,
            ParliamentaryContentType.CITIZEN_PETITION
        ]
        
        audio_content_types = [
            ParliamentaryContentType.PARLIAMENTARY_DEBATE,
            ParliamentaryContentType.QUESTION_PERIOD
        ]
        
        if input_data.input_type == InputType.TEXT:
            if input_data.content_type not in text_content_types:
                validation["issues"].append(
                    f"Content type {input_data.content_type.value} not suitable for text input"
                )
        
        elif input_data.input_type == InputType.DOCUMENT:
            if input_data.content_type not in document_content_types:
                validation["issues"].append(
                    f"Content type {input_data.content_type.value} not suitable for document input"
                )
        
        elif input_data.input_type == InputType.AUDIO:
            if input_data.content_type not in audio_content_types:
                validation["issues"].append(
                    f"Content type {input_data.content_type.value} not suitable for audio input"
                )
        
        validation["valid"] = len(validation["issues"]) == 0
        return validation
    
    async def _check_constitutional_compliance(
        self, 
        input_data: ParliamentaryInput
    ) -> Dict[str, Any]:
        """Check constitutional compliance of input content."""
        
        compliance_check = {"compliant": True, "violations": []}
        
        # Basic compliance checks based on content
        content_str = str(input_data.content).lower() if isinstance(input_data.content, str) else ""
        
        # Check for potential constitutional violations
        violation_indicators = [
            "unconstitutional", "charter violation", "illegal surveillance",
            "arbitrary detention", "discrimination", "ultra vires"
        ]
        
        found_violations = [indicator for indicator in violation_indicators 
                          if indicator in content_str]
        
        if found_violations:
            compliance_check["violations"].extend([
                f"Potential constitutional issue: {violation}" 
                for violation in found_violations
            ])
            compliance_check["compliant"] = False
        
        # Additional content-type specific checks
        if input_data.content_type == ParliamentaryContentType.BILL_TEXT:
            if "emergency powers" in content_str and "parliamentary oversight" not in content_str:
                compliance_check["violations"].append(
                    "Emergency powers without parliamentary oversight may violate separation of powers"
                )
                compliance_check["compliant"] = False
        
        return compliance_check
    
    def _validate_media_format(self, input_data: ParliamentaryInput) -> Dict[str, Any]:
        """Validate media format and technical specifications."""
        
        validation = {"valid": True, "issues": []}
        
        # If content is a URL, validate URL format
        if isinstance(input_data.content, str) and input_data.content.startswith(('http://', 'https://')):
            # URL validation
            if not self._is_valid_url(input_data.content):
                validation["issues"].append("Invalid URL format")
        
        # If content is bytes, validate format
        elif isinstance(input_data.content, bytes):
            format_valid = self._validate_binary_format(input_data.content, input_data.input_type)
            if not format_valid:
                validation["issues"].append(f"Invalid {input_data.input_type.value} format")
        
        validation["valid"] = len(validation["issues"]) == 0
        return validation
    
    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation."""
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _validate_binary_format(self, content: bytes, input_type: InputType) -> bool:
        """Validate binary content format."""
        
        # Simple magic number validation
        if input_type == InputType.IMAGE:
            # Check for common image magic numbers
            image_signatures = [
                b'\xFF\xD8\xFF',  # JPEG
                b'\x89PNG\r\n\x1a\n',  # PNG
                b'GIF87a', b'GIF89a',  # GIF
                b'BM',  # BMP
                b'RIFF'  # WebP (partial)
            ]
            return any(content.startswith(sig) for sig in image_signatures)
        
        elif input_type == InputType.AUDIO:
            audio_signatures = [
                b'ID3',  # MP3
                b'RIFF',  # WAV
                b'\x00\x00\x00\x20ftypM4A',  # M4A (partial)
                b'OggS'  # OGG
            ]
            return any(content.startswith(sig) for sig in audio_signatures)
        
        elif input_type == InputType.VIDEO:
            video_signatures = [
                b'\x00\x00\x00\x20ftyp',  # MP4
                b'RIFF',  # AVI
                b'\x00\x00\x00\x1CftypM',  # MOV (partial)
                b'1a45dfa3'  # MKV (partial)
            ]
            return any(content.startswith(sig) for sig in video_signatures)
        
        elif input_type == InputType.DOCUMENT:
            document_signatures = [
                b'%PDF',  # PDF
                b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1',  # DOC/DOCX
                b'PK\x03\x04'  # ODT/DOCX (ZIP-based)
            ]
            return any(content.startswith(sig) for sig in document_signatures)
        
        return True  # Default to valid for unknown types
    
    def _generate_remediation_actions(self, issues: List[str]) -> List[str]:
        """Generate recommended actions to address validation issues."""
        
        actions = []
        
        for issue in issues:
            if "clearance" in issue.lower():
                actions.append("Obtain appropriate security clearance or declassify content")
            elif "format" in issue.lower():
                actions.append("Convert content to supported format")
            elif "constitutional" in issue.lower():
                actions.append("Review content for constitutional compliance")
            elif "url" in issue.lower():
                actions.append("Verify URL accessibility and format")
            else:
                actions.append("Review and correct identified issues")
        
        return list(set(actions))  # Remove duplicates
    
    async def create_multimodal_input(
        self,
        content: Union[str, bytes, Path],
        input_type: InputType,
        content_type: ParliamentaryContentType,
        **kwargs
    ) -> Union[str, ImageUrl, BinaryContent, AudioUrl, VideoUrl, DocumentUrl]:
        """
        Create appropriate Pydantic AI input object for multimodal content.
        
        Args:
            content: Content data (string, bytes, or file path)
            input_type: Type of input content
            content_type: Parliamentary content type
            **kwargs: Additional metadata
            
        Returns:
            Pydantic AI compatible input object
        """
        
        try:
            # Handle different content sources
            if isinstance(content, Path):
                if content.exists():
                    if input_type == InputType.TEXT:
                        return content.read_text(encoding='utf-8')
                    else:
                        content_bytes = content.read_bytes()
                        media_type = mimetypes.guess_type(str(content))[0] or "application/octet-stream"
                        
                        return BinaryContent(
                            data=content_bytes,
                            media_type=media_type
                        )
                else:
                    raise FileNotFoundError(f"File not found: {content}")
            
            elif isinstance(content, str):
                if input_type == InputType.TEXT:
                    return content
                elif content.startswith(('http://', 'https://')):
                    # URL content
                    if input_type == InputType.IMAGE:
                        return ImageUrl(url=content)
                    elif input_type == InputType.AUDIO:
                        return AudioUrl(url=content)
                    elif input_type == InputType.VIDEO:
                        return VideoUrl(url=content)
                    elif input_type == InputType.DOCUMENT:
                        return DocumentUrl(url=content)
                else:
                    # String content for non-text types
                    content_bytes = content.encode('utf-8')
                    return BinaryContent(
                        data=content_bytes,
                        media_type="text/plain"
                    )
            
            elif isinstance(content, bytes):
                # Binary content
                media_type = self._guess_media_type(content, input_type)
                return BinaryContent(
                    data=content,
                    media_type=media_type
                )
            
            else:
                raise ValueError(f"Unsupported content type: {type(content)}")
                
        except Exception as e:
            self.logger.log_parliamentary_event(
                event_type="multimodal_input_creation_error",
                data={
                    "error": str(e),
                    "input_type": input_type.value,
                    "content_type": content_type.value
                },
                authority="system"
            )
            raise
    
    def _guess_media_type(self, content: bytes, input_type: InputType) -> str:
        """Guess media type from binary content."""
        
        # Media type mapping based on magic numbers
        if input_type == InputType.IMAGE:
            if content.startswith(b'\xFF\xD8\xFF'):
                return "image/jpeg"
            elif content.startswith(b'\x89PNG\r\n\x1a\n'):
                return "image/png"
            elif content.startswith(b'GIF87a') or content.startswith(b'GIF89a'):
                return "image/gif"
            elif content.startswith(b'BM'):
                return "image/bmp"
            elif content.startswith(b'RIFF') and b'WEBP' in content[:20]:
                return "image/webp"
            else:
                return "image/jpeg"  # Default
        
        elif input_type == InputType.AUDIO:
            if content.startswith(b'ID3') or content.startswith(b'\xFF\xFB'):
                return "audio/mpeg"
            elif content.startswith(b'RIFF') and b'WAVE' in content[:20]:
                return "audio/wav"
            elif content.startswith(b'\x00\x00\x00\x20ftypM4A'):
                return "audio/m4a"
            elif content.startswith(b'OggS'):
                return "audio/ogg"
            else:
                return "audio/mpeg"  # Default
        
        elif input_type == InputType.VIDEO:
            if content.startswith(b'\x00\x00\x00\x20ftyp'):
                return "video/mp4"
            elif content.startswith(b'RIFF') and b'AVI ' in content[:20]:
                return "video/avi"
            elif content.startswith(b'\x00\x00\x00\x1CftypM'):
                return "video/quicktime"
            else:
                return "video/mp4"  # Default
        
        elif input_type == InputType.DOCUMENT:
            if content.startswith(b'%PDF'):
                return "application/pdf"
            elif content.startswith(b'PK\x03\x04'):
                return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif content.startswith(b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'):
                return "application/msword"
            else:
                return "application/pdf"  # Default
        
        return "application/octet-stream"  # Fallback
    
    async def analyze_parliamentary_content(
        self,
        input_data: ParliamentaryInput,
        analysis_instructions: str,
        constitutional_authority: ParliamentaryAuthority,
        agent_deps: Optional[EnhancedParliamentaryDeps] = None
    ) -> Dict[str, Any]:
        """
        Analyze parliamentary content using appropriate AI model.
        
        Args:
            input_data: Parliamentary input to analyze
            analysis_instructions: Instructions for analysis
            constitutional_authority: Authority requesting analysis
            agent_deps: Optional agent dependencies
            
        Returns:
            Analysis results with constitutional metadata
        """
        
        try:
            # Validate input first
            validation_result = await self.validate_parliamentary_input(
                input_data, constitutional_authority
            )
            
            if not validation_result.valid:
                return {
                    "analysis_successful": False,
                    "validation_result": validation_result,
                    "error": f"Input validation failed: {validation_result.issues}"
                }
            
            # Create multimodal input
            ai_input = await self.create_multimodal_input(
                content=input_data.content,
                input_type=input_data.input_type,
                content_type=input_data.content_type
            )
            
            # Get appropriate model configuration
            model_config = get_model_config()
            
            # Create agent for analysis
            if input_data.input_type in [InputType.IMAGE, InputType.VIDEO, InputType.AUDIO]:
                # Use multimodal-capable model
                enabled_providers = model_config.get_enabled_providers()
                
                multimodal_providers = ["openai", "gemini", "anthropic"]
                selected_provider = None
                
                for provider in multimodal_providers:
                    if provider in enabled_providers:
                        selected_provider = provider
                        break
                
                if not selected_provider:
                    return {
                        "analysis_successful": False,
                        "error": "No multimodal-capable AI provider available"
                    }
                
                fallback_model = model_config.create_fallback_model([selected_provider])
            else:
                # Use standard model
                fallback_model = model_config.create_fallback_model()
            
            # Create analysis agent
            analysis_agent = Agent(
                model=fallback_model,
                system_prompt=f"""You are analyzing parliamentary content as the {constitutional_authority.value} constitutional authority.

Content Type: {input_data.content_type.value}
Security Classification: {input_data.security_classification.value}

Provide thorough analysis while maintaining:
- Constitutional accountability
- Westminster parliamentary principles
- Appropriate security handling
- Democratic transparency where applicable

Analysis Instructions: {analysis_instructions}"""
            )
            
            # Execute analysis
            start_time = datetime.now(timezone.utc)
            
            with self.logger.parliamentary_session_span(
                f"content-analysis-{input_data.input_type.value}",
                [constitutional_authority.value]
            ) as span:
                
                # Create analysis prompt
                analysis_prompt = [
                    f"Analyze this {input_data.content_type.value} content:",
                    ai_input
                ]
                
                if input_data.title:
                    analysis_prompt.insert(1, f"Title: {input_data.title}")
                
                if input_data.description:
                    analysis_prompt.insert(-1, f"Description: {input_data.description}")
                
                # Run analysis
                analysis_result = await analysis_agent.run(
                    analysis_prompt,
                    deps=agent_deps
                )
                
                execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                
                # Create comprehensive result
                result = {
                    "analysis_successful": True,
                    "analysis_result": str(analysis_result.data),
                    "input_metadata": {
                        "input_type": input_data.input_type.value,
                        "content_type": input_data.content_type.value,
                        "security_classification": input_data.security_classification.value,
                        "title": input_data.title,
                        "source": input_data.source
                    },
                    "validation_result": validation_result,
                    "execution_time_seconds": execution_time,
                    "constitutional_authority": constitutional_authority.value,
                    "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
                    "constitutional_compliance": validation_result.constitutional_compliance
                }
                
                # Log analysis completion
                self.logger.log_parliamentary_event(
                    event_type="parliamentary_content_analyzed",
                    data={
                        "input_type": input_data.input_type.value,
                        "content_type": input_data.content_type.value,
                        "execution_time": execution_time,
                        "constitutional_compliant": result["constitutional_compliance"],
                        "analysis_successful": True
                    },
                    authority=constitutional_authority.value
                )
                
                span.set_attribute("analysis.successful", True)
                span.set_attribute("analysis.input_type", input_data.input_type.value)
                span.set_attribute("analysis.execution_time", execution_time)
                
                return result
                
        except Exception as e:
            self.logger.log_parliamentary_event(
                event_type="parliamentary_content_analysis_error",
                data={
                    "error": str(e),
                    "input_type": input_data.input_type.value,
                    "content_type": input_data.content_type.value
                },
                authority=constitutional_authority.value
            )
            
            return {
                "analysis_successful": False,
                "error": str(e),
                "input_metadata": {
                    "input_type": input_data.input_type.value,
                    "content_type": input_data.content_type.value
                }
            }


# Convenience functions for common parliamentary input scenarios

async def analyze_bill_text(
    bill_text: str,
    bill_title: str,
    constitutional_authority: ParliamentaryAuthority = ParliamentaryAuthority.LEGISLATIVE
) -> Dict[str, Any]:
    """Analyze parliamentary bill text."""
    
    handler = ParliamentaryInputHandler()
    
    input_data = ParliamentaryInput(
        content=bill_text,
        input_type=InputType.TEXT,
        content_type=ParliamentaryContentType.BILL_TEXT,
        title=bill_title,
        constitutional_authority=constitutional_authority,
        security_classification=SecurityClassification.PROTECTED_A
    )
    
    return await handler.analyze_parliamentary_content(
        input_data=input_data,
        analysis_instructions="Analyze this bill for constitutional compliance, policy implications, and parliamentary procedure requirements.",
        constitutional_authority=constitutional_authority
    )


async def analyze_parliamentary_document(
    document_path: Path,
    content_type: ParliamentaryContentType,
    constitutional_authority: ParliamentaryAuthority
) -> Dict[str, Any]:
    """Analyze parliamentary document file."""
    
    handler = ParliamentaryInputHandler()
    
    input_data = ParliamentaryInput(
        content=document_path.read_bytes(),
        input_type=InputType.DOCUMENT,
        content_type=content_type,
        title=document_path.stem,
        source=str(document_path),
        constitutional_authority=constitutional_authority
    )
    
    return await handler.analyze_parliamentary_content(
        input_data=input_data,
        analysis_instructions="Analyze this parliamentary document for key findings, constitutional implications, and recommended actions.",
        constitutional_authority=constitutional_authority
    )


async def analyze_debate_audio(
    audio_url: str,
    debate_title: str,
    constitutional_authority: ParliamentaryAuthority = ParliamentaryAuthority.SPEAKER
) -> Dict[str, Any]:
    """Analyze parliamentary debate audio."""
    
    handler = ParliamentaryInputHandler()
    
    input_data = ParliamentaryInput(
        content=audio_url,
        input_type=InputType.AUDIO,
        content_type=ParliamentaryContentType.PARLIAMENTARY_DEBATE,
        title=debate_title,
        constitutional_authority=constitutional_authority
    )
    
    return await handler.analyze_parliamentary_content(
        input_data=input_data,
        analysis_instructions="Transcribe and analyze this parliamentary debate for key arguments, procedural compliance, and significant exchanges.",
        constitutional_authority=constitutional_authority
    )


# Global input handler
parliamentary_input_handler = ParliamentaryInputHandler()


def get_parliamentary_input_handler() -> ParliamentaryInputHandler:
    """Get the global parliamentary input handler."""
    return parliamentary_input_handler


# Example usage
async def example_input_handling():
    """Example of comprehensive input handling for parliamentary content."""
    
    handler = get_parliamentary_input_handler()
    
    # Example 1: Analyze bill text
    bill_analysis = await analyze_bill_text(
        bill_text="An Act to establish digital privacy protections for Canadian citizens...",
        bill_title="Digital Privacy Protection Act",
        constitutional_authority=ParliamentaryAuthority.LEGISLATIVE
    )
    
    print(f"Bill Analysis:")
    print(f"Success: {bill_analysis['analysis_successful']}")
    print(f"Constitutional Compliant: {bill_analysis.get('constitutional_compliance', 'Unknown')}")
    print(f"Analysis: {bill_analysis.get('analysis_result', 'No analysis')[:200]}...")
    
    # Example 2: Validate input
    sample_input = ParliamentaryInput(
        content="Sample parliamentary content for validation",
        input_type=InputType.TEXT,
        content_type=ParliamentaryContentType.POLICY_PROPOSAL,
        security_classification=SecurityClassification.PROTECTED_B
    )
    
    validation_result = await handler.validate_parliamentary_input(
        sample_input,
        ParliamentaryAuthority.EXECUTIVE
    )
    
    print(f"\nInput Validation:")
    print(f"Valid: {validation_result.valid}")
    print(f"Constitutional Compliant: {validation_result.constitutional_compliance}")
    print(f"Security Cleared: {validation_result.security_cleared}")
    print(f"Issues: {validation_result.issues}")
    
    return {
        "bill_analysis": bill_analysis,
        "validation_result": validation_result
    }


if __name__ == "__main__":
    asyncio.run(example_input_handling())