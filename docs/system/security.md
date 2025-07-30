# AI Triad Security Architecture

## Overview

The AI Triad Model implements comprehensive security measures based on **constitutional AI principles** and **zero-trust architecture**. Security is designed around the Canadian Westminster Parliamentary System's checks and balances, ensuring no single component can compromise system integrity.

## 🏛️ Constitutional Security Model

### Security Branches (Westminster Inspired)

| **Branch** | **AI Triad Agent** | **Security Responsibilities** |
|------------|-------------------|-------------------------------|
| **Legislative** | **Planner Agent** | Policy creation, access rule definition, security requirement planning |
| **Executive** | **Executor Agent** | Policy enforcement, access control execution, security measure implementation |
| **Judicial** | **Evaluator Agent** | Security validation, compliance assessment, threat evaluation |
| **Crown** | **Overwatch Agent** | Constitutional security oversight, escalation authority, system-wide monitoring |

### **Fundamental Security Principles**

1. **No Unilateral Security Decisions**: All security actions require multi-agent validation
2. **Constitutional Oversight**: Overwatch maintains security authority over all agents
3. **Mandatory Security Validation**: All operations pass through security evaluation
4. **Continuous Security Monitoring**: Constitutional compliance in all security measures
5. **Democratic Security Governance**: Transparent, accountable security processes

## 🔐 Authentication & Authorization

### Multi-Factor Agent Authentication

```python
from pydantic import BaseModel
from typing import List, Optional
import logfire
from datetime import datetime, timedelta
import jwt
from cryptography.fernet import Fernet

class SecurityContext(BaseModel):
    """Constitutional security context for all operations."""
    user_id: str
    session_id: str
    security_clearance: SecurityClearance
    constitutional_branch: str  # legislative, executive, judicial, crown
    permissions: List[Permission]
    mfa_verified: bool
    token_expires_at: datetime
    
class AgentSecurityManager:
    """Constitutional security manager for agent operations."""
    
    def __init__(self, deps: TriadDeps):
        self.deps = deps
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
    async def authenticate_constitutional_access(
        self, 
        credentials: AgentCredentials,
        requested_branch: str
    ) -> SecurityContext:
        """Authenticate access with constitutional validation."""
        
        with logfire.span("constitutional_authentication") as span:
            span.set_attribute("requested_branch", requested_branch)
            span.set_attribute("user_id", credentials.user_id)
            
            # Step 1: Verify credentials
            if not await self._verify_credentials(credentials):
                await self.deps.logfire_logger.warning(
                    "Authentication failed - invalid credentials",
                    user_id=credentials.user_id,
                    security_event="auth_failure"
                )
                raise AuthenticationError("Invalid credentials")
            
            # Step 2: Verify MFA
            if not await self._verify_mfa(credentials):
                await self.deps.logfire_logger.warning(
                    "Authentication failed - MFA verification failed",
                    user_id=credentials.user_id,
                    security_event="mfa_failure"
                )
                raise AuthenticationError("MFA verification failed")
            
            # Step 3: Constitutional branch validation
            security_clearance = await self._get_security_clearance(credentials.user_id)
            if not await self._validate_branch_access(security_clearance, requested_branch):
                await self.deps.logfire_logger.error(
                    "Access denied - insufficient constitutional authority",
                    user_id=credentials.user_id,
                    requested_branch=requested_branch,
                    clearance_level=security_clearance.level,
                    security_event="authorization_failure"
                )
                raise AuthorizationError("Insufficient constitutional authority")
            
            # Step 4: Create security context
            security_context = SecurityContext(
                user_id=credentials.user_id,
                session_id=self._generate_session_id(),
                security_clearance=security_clearance,
                constitutional_branch=requested_branch,
                permissions=await self._get_user_permissions(credentials.user_id),
                mfa_verified=True,
                token_expires_at=datetime.now(timezone.utc) + timedelta(hours=8)
            )
            
            # Step 5: Log successful authentication with constitutional oversight
            await self.deps.logfire_logger.info(
                "Constitutional authentication successful",
                user_id=credentials.user_id,
                constitutional_branch=requested_branch,
                security_clearance=security_clearance.level,
                security_event="auth_success",
                constitutional_oversight=True
            )
            
            # Step 6: Notify other agents via A2A protocol
            await self.deps.a2a_broker.broadcast_security_event({
                "event_type": "authentication_success",
                "user_id": credentials.user_id,
                "constitutional_branch": requested_branch,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": security_context.session_id
            })
            
            return security_context
```

### API Security Implementation

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_constitutional_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    deps: TriadDeps = Depends(get_deps)
) -> SecurityContext:
    """Verify JWT token with constitutional validation."""
    
    try:
        # Decode and verify JWT
        payload = jwt.decode(
            credentials.credentials,
            deps.config.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        
        # Validate constitutional authority
        constitutional_branch = payload.get("constitutional_branch")
        if not constitutional_branch:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Missing constitutional authority"
            )
        
        # Verify session is still active
        session_id = payload.get("session_id")
        if not await deps.security_manager.is_session_active(session_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired or invalid"
            )
        
        # Log access attempt
        await deps.logfire_logger.info(
            "API access authorized",
            user_id=payload.get("user_id"),
            constitutional_branch=constitutional_branch,
            endpoint=request.url.path,
            security_event="api_access",
            constitutional_oversight=True
        )
        
        return SecurityContext.model_validate(payload)
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

## 🛡️ Data Protection & Encryption

### Constitutional Data Classification

```python
from enum import Enum
from cryptography.fernet import Fernet
import hashlib

class DataClassification(Enum):
    """Constitutional data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"  # Requires Crown (Overwatch) authority
    TOP_SECRET = "top_secret"  # Constitutional oversight required

class ConstitutionalDataProtection:
    """Data protection with constitutional oversight."""
    
    def __init__(self, deps: TriadDeps):
        self.deps = deps
        self.encryption_keys = self._initialize_encryption_keys()
        
    async def encrypt_constitutional_data(
        self,
        data: dict,
        classification: DataClassification,
        constitutional_authority: str
    ) -> str:
        """Encrypt data with constitutional validation."""
        
        with logfire.span("constitutional_data_encryption") as span:
            span.set_attribute("classification", classification.value)
            span.set_attribute("constitutional_authority", constitutional_authority)
            
            # Validate authority level for classification
            if not await self._validate_encryption_authority(
                classification, constitutional_authority
            ):
                raise SecurityError(
                    f"Insufficient authority to encrypt {classification.value} data"
                )
            
            # Select appropriate encryption key based on classification
            encryption_key = self.encryption_keys[classification]
            cipher_suite = Fernet(encryption_key)
            
            # Add constitutional metadata
            constitutional_data = {
                "data": data,
                "classification": classification.value,
                "encrypted_by": constitutional_authority,
                "encrypted_at": datetime.now(timezone.utc).isoformat(),
                "constitutional_oversight": True
            }
            
            # Encrypt data
            encrypted_data = cipher_suite.encrypt(
                json.dumps(constitutional_data).encode()
            )
            
            # Log encryption event
            await self.deps.logfire_logger.info(
                "Constitutional data encrypted",
                classification=classification.value,
                constitutional_authority=constitutional_authority,
                data_hash=hashlib.sha256(str(data).encode()).hexdigest()[:16],
                security_event="data_encryption"
            )
            
            return encrypted_data.decode()
    
    async def decrypt_constitutional_data(
        self,
        encrypted_data: str,
        security_context: SecurityContext
    ) -> dict:
        """Decrypt data with constitutional authorization."""
        
        with logfire.span("constitutional_data_decryption") as span:
            span.set_attribute("user_id", security_context.user_id)
            span.set_attribute("constitutional_branch", security_context.constitutional_branch)
            
            try:
                # Attempt decryption with user's clearance level
                classification = await self._determine_data_classification(encrypted_data)
                
                # Validate decryption authority
                if not await self._validate_decryption_authority(
                    classification, security_context
                ):
                    await self.deps.logfire_logger.warning(
                        "Unauthorized decryption attempt",
                        user_id=security_context.user_id,
                        classification=classification.value,
                        security_event="unauthorized_decryption"
                    )
                    raise SecurityError("Insufficient authority to decrypt data")
                
                encryption_key = self.encryption_keys[classification]
                cipher_suite = Fernet(encryption_key)
                
                decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
                constitutional_data = json.loads(decrypted_data.decode())
                
                # Log successful decryption
                await self.deps.logfire_logger.info(
                    "Constitutional data decrypted",
                    user_id=security_context.user_id,
                    classification=classification.value,
                    constitutional_oversight=True,
                    security_event="data_decryption"
                )
                
                return constitutional_data["data"]
                
            except Exception as e:
                await self.deps.logfire_logger.error(
                    "Data decryption failed",
                    user_id=security_context.user_id,
                    error=str(e),
                    security_event="decryption_failure"
                )
                raise SecurityError("Data decryption failed")
```

## 🚨 Threat Detection & Response

### Constitutional Threat Monitoring

```python
class ConstitutionalThreatDetector:
    """AI-powered threat detection with constitutional oversight."""
    
    def __init__(self, deps: TriadDeps):
        self.deps = deps
        self.threat_patterns = self._load_threat_patterns()
        self.baseline_behavior = self._establish_baseline()
        
    async def monitor_constitutional_threats(self):
        """Continuous threat monitoring with democratic oversight."""
        
        while True:
            with logfire.span("constitutional_threat_monitoring") as span:
                # Collect security metrics from all constitutional branches
                security_metrics = await self._collect_security_metrics()
                
                # Analyze for anomalies
                threats = await self._analyze_for_threats(security_metrics)
                
                for threat in threats:
                    await self._handle_constitutional_threat(threat)
                
                # Wait for next monitoring cycle
                await asyncio.sleep(30)  # 30-second monitoring cycle
    
    async def _handle_constitutional_threat(self, threat: DetectedThreat):
        """Handle detected threats with constitutional process."""
        
        with logfire.span("constitutional_threat_response") as span:
            span.set_attribute("threat_level", threat.severity.value)
            span.set_attribute("threat_type", threat.threat_type)
            span.set_attribute("constitutional_oversight", True)
            
            # Log threat detection
            await self.deps.logfire_logger.warning(
                f"Constitutional threat detected: {threat.threat_type}",
                threat_id=threat.id,
                severity=threat.severity.value,
                affected_component=threat.affected_component,
                threat_indicators=threat.indicators,
                security_event="threat_detected"
            )
            
            # Immediate response based on severity
            if threat.severity == ThreatSeverity.CRITICAL:
                # Crown (Overwatch) authority - immediate action
                await self._execute_emergency_response(threat)
                
                # Notify all constitutional branches
                await self.deps.a2a_broker.broadcast_emergency({
                    "event_type": "critical_security_threat",
                    "threat_id": threat.id,
                    "threat_type": threat.threat_type,
                    "immediate_action_required": True,
                    "constitutional_authority": "crown"
                })
                
            elif threat.severity == ThreatSeverity.HIGH:
                # Judicial review required - Evaluator Agent validation
                await self._request_judicial_review(threat)
                
            else:
                # Standard constitutional process
                await self._initiate_standard_response(threat)
    
    async def _execute_emergency_response(self, threat: DetectedThreat):
        """Execute emergency response with Crown authority."""
        
        # Immediate protective measures
        if threat.threat_type == "unauthorized_access":
            await self._revoke_suspicious_sessions(threat.indicators)
            await self._enable_enhanced_monitoring()
            
        elif threat.threat_type == "data_breach":
            await self._isolate_affected_systems(threat.affected_component)
            await self._encrypt_sensitive_data()
            
        elif threat.threat_type == "agent_compromise":
            await self._quarantine_agent(threat.affected_component)
            await self._activate_backup_agents()
        
        # Constitutional notification
        await self.deps.logfire_logger.critical(
            "Emergency security response executed",
            threat_id=threat.id,
            response_actions=threat.response_actions,
            constitutional_authority="crown",
            security_event="emergency_response"
        )
```

## 🔒 Secure External Integration

### MCP Security Framework

```python
class SecureMCPIntegration:
    """Secure external system integration with constitutional oversight."""
    
    def __init__(self, deps: TriadDeps):
        self.deps = deps
        self.integration_policies = self._load_integration_policies()
        
    async def secure_external_integration(
        self,
        system_type: str,
        operation: str,
        parameters: dict,
        security_context: SecurityContext
    ) -> dict:
        """Securely integrate with external systems via MCP."""
        
        with logfire.span("secure_external_integration") as span:
            span.set_attribute("system_type", system_type)
            span.set_attribute("operation", operation)
            span.set_attribute("user_id", security_context.user_id)
            span.set_attribute("constitutional_oversight", True)
            
            # Step 1: Validate integration authority
            if not await self._validate_integration_authority(
                system_type, operation, security_context
            ):
                raise SecurityError(
                    f"Insufficient authority for {system_type} integration"
                )
            
            # Step 2: Sanitize parameters
            sanitized_params = await self._sanitize_parameters(parameters)
            
            # Step 3: Add security headers
            secure_params = {
                **sanitized_params,
                "security_context": {
                    "user_id": security_context.user_id,
                    "session_id": security_context.session_id,
                    "constitutional_branch": security_context.constitutional_branch,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                "constitutional_validation": True
            }
            
            # Step 4: Execute integration with monitoring
            try:
                result = await self.deps.mcp_client.call_tool(
                    f"{system_type}_adapter",
                    operation,
                    secure_params
                )
                
                # Step 5: Validate response
                validated_result = await self._validate_integration_response(
                    result, system_type, operation
                )
                
                # Step 6: Log successful integration
                await self.deps.logfire_logger.info(
                    "Secure external integration completed",
                    system_type=system_type,
                    operation=operation,
                    user_id=security_context.user_id,
                    constitutional_oversight=True,
                    security_event="external_integration_success"
                )
                
                return validated_result
                
            except Exception as e:
                await self.deps.logfire_logger.error(
                    "Secure external integration failed",
                    system_type=system_type,
                    operation=operation,
                    user_id=security_context.user_id,
                    error=str(e),
                    security_event="external_integration_failure"
                )
                raise SecurityError(f"External integration failed: {str(e)}")
```

## 📊 Security Monitoring & Compliance

### Constitutional Security Dashboard

```python
class ConstitutionalSecurityDashboard:
    """Real-time security monitoring with constitutional oversight."""
    
    async def get_security_status(self, security_context: SecurityContext) -> SecurityStatus:
        """Get comprehensive security status with constitutional authority."""
        
        # Validate viewing authority
        if not await self._validate_security_viewing_authority(security_context):
            raise SecurityError("Insufficient authority to view security status")
        
        with logfire.span("constitutional_security_status") as span:
            span.set_attribute("user_id", security_context.user_id)
            span.set_attribute("constitutional_branch", security_context.constitutional_branch)
            
            # Collect security metrics from all branches
            auth_metrics = await self._collect_authentication_metrics()
            threat_metrics = await self._collect_threat_metrics()
            integration_metrics = await self._collect_integration_security_metrics()
            compliance_metrics = await self._collect_compliance_metrics()
            
            # Generate security summary
            security_status = SecurityStatus(
                overall_security_level=self._calculate_overall_security_level(
                    auth_metrics, threat_metrics, integration_metrics, compliance_metrics
                ),
                constitutional_branches={
                    "legislative": await self._get_branch_security_status("legislative"),
                    "executive": await self._get_branch_security_status("executive"),
                    "judicial": await self._get_branch_security_status("judicial"),
                    "crown": await self._get_branch_security_status("crown")
                },
                active_threats=await self._get_active_threats(),
                security_alerts=await self._get_security_alerts(),
                compliance_status=await self._get_compliance_status(),
                external_integrations=await self._get_integration_security_status(),
                recommendations=await self._generate_security_recommendations()
            )
            
            # Log security status access
            await self.deps.logfire_logger.info(
                "Security status accessed",
                user_id=security_context.user_id,
                constitutional_branch=security_context.constitutional_branch,
                overall_security_level=security_status.overall_security_level,
                active_threat_count=len(security_status.active_threats),
                security_event="security_status_access"
            )
            
            return security_status
```

## 🛠️ Security Best Practices

### Implementation Guidelines

1. **Constitutional Security Governance**
   - All security decisions follow democratic AI principles
   - Multi-agent validation for critical security actions
   - Crown (Overwatch) authority for emergency responses
   - Transparent audit trails for all security events

2. **Zero-Trust Architecture**
   - Verify every request regardless of source
   - Encrypt all data in transit and at rest
   - Implement least-privilege access principles
   - Continuous monitoring and validation

3. **Secure External Integration**
   - All MCP integrations require security validation
   - Sanitize all external inputs and outputs
   - Monitor integration security continuously
   - Implement secure credential management

4. **Incident Response**
   - Automated threat detection and response
   - Constitutional escalation procedures
   - Comprehensive logging and forensics
   - Regular security drills and testing

## 🔐 Security Configuration

### Environment Variables

```bash
# Security Configuration
SECURITY_ENCRYPTION_KEY=<constitutional_encryption_key>
JWT_SECRET_KEY=<jwt_secret_for_token_signing>
MFA_SECRET_KEY=<multi_factor_auth_secret>

# Logfire Security Monitoring
LOGFIRE_TOKEN=<security_monitoring_token>
LOGFIRE_SECURITY_ALERTS=true

# Constitutional Authority Keys
LEGISLATIVE_BRANCH_KEY=<planner_agent_key>
EXECUTIVE_BRANCH_KEY=<executor_agent_key>
JUDICIAL_BRANCH_KEY=<evaluator_agent_key>
CROWN_AUTHORITY_KEY=<overwatch_agent_key>

# External Integration Security
MCP_SECURITY_TOKENS=<mcp_server_security_tokens>
A2A_ENCRYPTION_KEY=<agent_communication_key>
```

This constitutional security architecture ensures that the AI Triad Model maintains the highest security standards while preserving the democratic principles of accountability, transparency, and distributed authority that define the system's core philosophy.