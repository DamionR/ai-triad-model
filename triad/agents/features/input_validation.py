"""
Input Validation for Westminster Parliamentary AI System

Implements comprehensive validation for multimodal parliamentary content
including security clearance, content type, constitutional compliance,
and media format validation.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from enum import Enum
import logfire

from triad.tools.governance.governance_toolsets import AuthorityLevel
from triad.core.logging import get_logfire_config
from .input_types import (
    InputType, 
    ParliamentaryContentType, 
    SecurityClassification,
    ParliamentaryInput,
    InputValidationResult
)


class InputValidator:
    """
    Handles all validation operations for parliamentary input content.
    
    Provides security clearance validation, content type validation,
    constitutional compliance checks, and media format validation.
    """
    
    def __init__(self):
        self.logger = get_logfire_config()
    
    async def validate_parliamentary_input(
        self,
        input_data: ParliamentaryInput,
        constitutional_authority: Optional[AuthorityLevel] = None
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
        authority: Optional[AuthorityLevel]
    ) -> bool:
        """Validate security clearance for content access."""
        
        if not authority:
            # Only allow unclassified content without authority
            return classification == SecurityClassification.UNCLASSIFIED
        
        # Authority-based clearance levels
        clearance_levels = {
            AuthorityLevel.OVERSEER: [
                SecurityClassification.UNCLASSIFIED,
                SecurityClassification.PROTECTED_A,
                SecurityClassification.PROTECTED_B,
                SecurityClassification.PROTECTED_C,
                SecurityClassification.CONFIDENTIAL,
                SecurityClassification.SECRET,
                SecurityClassification.TOP_SECRET
            ],
            AuthorityLevel.EXECUTIVE: [
                SecurityClassification.UNCLASSIFIED,
                SecurityClassification.PROTECTED_A,
                SecurityClassification.PROTECTED_B,
                SecurityClassification.PROTECTED_C,
                SecurityClassification.CONFIDENTIAL
            ],
            AuthorityLevel.COORDINATOR: [
                SecurityClassification.UNCLASSIFIED,
                SecurityClassification.PROTECTED_A,
                SecurityClassification.PROTECTED_B,
                SecurityClassification.PROTECTED_C,
                SecurityClassification.CONFIDENTIAL
            ],
            AuthorityLevel.SPECIALIST: [
                SecurityClassification.UNCLASSIFIED,
                SecurityClassification.PROTECTED_A,
                SecurityClassification.PROTECTED_B
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