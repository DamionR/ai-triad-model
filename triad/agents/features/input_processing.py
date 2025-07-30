"""
Input Processing for Westminster Parliamentary AI System

Implements processing methods for multimodal parliamentary content
including content transformation, multimodal input creation, and
parliamentary content analysis.
"""

import mimetypes
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from pathlib import Path
from pydantic_ai import Agent
from pydantic_ai.messages import (
    ImageUrl, 
    BinaryContent, 
    AudioUrl, 
    VideoUrl, 
    DocumentUrl
)

from triad.models.model_config import get_model_config
from triad.tools.governance.governance_toolsets import AuthorityLevel
from triad.agents.enhanced_agents import EnhancedParliamentaryDeps
from triad.core.logging import get_logfire_config
from .input_types import (
    InputType, 
    ParliamentaryContentType, 
    SecurityClassification,
    ParliamentaryInput
)


class InputProcessor:
    """
    Handles all processing operations for parliamentary input content.
    
    Provides multimodal input creation, content analysis, and
    media type detection functionality.
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
        constitutional_authority: AuthorityLevel,
        agent_deps: Optional[EnhancedParliamentaryDeps] = None,
        validation_result = None
    ) -> Dict[str, Any]:
        """
        Analyze parliamentary content using appropriate AI model.
        
        Args:
            input_data: Parliamentary input to analyze
            analysis_instructions: Instructions for analysis
            constitutional_authority: Authority requesting analysis
            agent_deps: Optional agent dependencies
            validation_result: Pre-computed validation result
            
        Returns:
            Analysis results with constitutional metadata
        """
        
        try:
            if not validation_result or not validation_result.valid:
                return {
                    "analysis_successful": False,
                    "validation_result": validation_result,
                    "error": f"Input validation failed: {validation_result.issues if validation_result else 'No validation performed'}"
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
                    "constitutional_compliance": validation_result.constitutional_compliance if validation_result else True
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
    constitutional_authority: AuthorityLevel = AuthorityLevel.COORDINATOR
) -> Dict[str, Any]:
    """Analyze parliamentary bill text."""
    
    from .input_handler import ParliamentaryInputHandler
    
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
    constitutional_authority: AuthorityLevel
) -> Dict[str, Any]:
    """Analyze parliamentary document file."""
    
    from .input_handler import ParliamentaryInputHandler
    
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
    constitutional_authority: AuthorityLevel = AuthorityLevel.SPECIALIST
) -> Dict[str, Any]:
    """Analyze parliamentary debate audio."""
    
    from .input_handler import ParliamentaryInputHandler
    
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