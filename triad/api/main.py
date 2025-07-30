"""
Triad Model FastAPI Application

Main FastAPI application for the Westminster Parliamentary AI System
with constitutional oversight and democratic accountability.
"""

from typing import Dict, Any
from contextlib import asynccontextmanager
import logfire
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .routes import agents, health, parliamentary
from .models import ErrorResponse
from triad.core.dependencies import get_triad_deps, TriadDeps
from triad.core.constitutional import ConstitutionalFramework


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles application startup and shutdown with constitutional
    framework initialization and parliamentary session management.
    """
    # Startup
    logfire.info("Triad Model API starting up...")
    
    # Initialize constitutional framework
    constitutional_framework = ConstitutionalFramework()
    await constitutional_framework.initialize({
        "framework_version": "Westminster_Parliamentary_v1.0",
        "constitutional_oversight": True,
        "parliamentary_accountability": True,
        "separation_of_powers": True,
        "rule_of_law": True,
        "democratic_principles": True
    })
    
    # Store framework in app state
    app.state.constitutional_framework = constitutional_framework
    
    logfire.info("Constitutional framework initialized")
    logfire.info("Triad Model API ready for parliamentary democracy")
    
    yield
    
    # Shutdown
    logfire.info("Triad Model API shutting down...")
    
    # Cleanup constitutional framework
    if hasattr(app.state, 'constitutional_framework'):
        await app.state.constitutional_framework.shutdown()
    
    logfire.info("Triad Model API shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Triad Model API",
    description="""
    Westminster Parliamentary AI System with Constitutional Oversight
    
    The Triad Model implements a Westminster-style parliamentary democracy for AI agents,
    featuring four core agents representing different branches of government:
    
    - **Planner Agent** (Legislative Branch): Policy planning and workflow design
    - **Executor Agent** (Executive Branch): Implementation and execution
    - **Evaluator Agent** (Judicial Branch): Compliance and constitutional review
    - **Overwatch Agent** (Crown): Monitoring and constitutional oversight
    
    ## Constitutional Framework
    
    The system operates under Westminster parliamentary principles:
    - **Separation of Powers**: Clear division of responsibilities
    - **Parliamentary Accountability**: Democratic oversight and transparency
    - **Rule of Law**: Constitutional compliance and legal consistency
    - **Responsible Government**: Ministerial responsibility and collective accountability
    
    ## Parliamentary Procedures
    
    - Question Period for democratic accountability
    - Parliamentary motions and voting
    - Constitutional review and oversight
    - Crisis management and emergency procedures
    
    ## API Features
    
    - Agent interaction endpoints
    - Parliamentary session management
    - Health monitoring and statistics
    - Constitutional compliance reporting
    - Democratic accountability tracking
    
    Built with Pydantic AI, FastAPI, and Logfire for comprehensive observability.
    """,
    version="1.0.0",
    contact={
        "name": "Triad Model Development Team",
        "url": "https://github.com/your-org/triad-model",
        "email": "contact@triad-model.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure Logfire for observability
logfire.configure(
    service_name="triad-model-api",
    service_version="1.0.0"
)
logfire.instrument_fastapi(app)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Include routers
app.include_router(agents.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")
app.include_router(parliamentary.router, prefix="/api/v1")


# Root endpoint
@app.get("/", response_model=Dict[str, Any])
async def root(deps: TriadDeps = Depends(get_triad_deps)) -> Dict[str, Any]:
    """
    Triad Model API root endpoint.
    
    Provides system information and constitutional status overview.
    """
    with logfire.span("api_root_endpoint"):
        await deps.log_event("api_root_accessed", {
            "constitutional_framework": "Westminster Parliamentary",
            "democratic_accountability": True
        })
        
        return {
            "name": "Triad Model API",
            "version": "1.0.0",
            "description": "Westminster Parliamentary AI System with Constitutional Oversight",
            "constitutional_framework": {
                "type": "Westminster Parliamentary Democracy",
                "version": "v1.0",
                "principles": [
                    "Separation of Powers",
                    "Parliamentary Accountability", 
                    "Rule of Law",
                    "Responsible Government",
                    "Democratic Oversight"
                ]
            },
            "agents": {
                "planner_agent": {
                    "branch": "Legislative",
                    "authority": "Policy planning and workflow design",
                    "constitutional_role": "Parliament/Legislature"
                },
                "executor_agent": {
                    "branch": "Executive", 
                    "authority": "Implementation and execution",
                    "constitutional_role": "Cabinet/Government"
                },
                "evaluator_agent": {
                    "branch": "Judicial",
                    "authority": "Compliance and constitutional review", 
                    "constitutional_role": "Courts/Judiciary"
                },
                "overwatch_agent": {
                    "branch": "Crown",
                    "authority": "Monitoring and constitutional oversight",
                    "constitutional_role": "Crown/Head of State"
                }
            },
            "api_endpoints": {
                "agents": "/api/v1/agents",
                "health": "/api/v1/health", 
                "parliamentary": "/api/v1/parliamentary",
                "documentation": "/docs",
                "openapi": "/openapi.json"
            },
            "parliamentary_procedures": [
                "Question Period",
                "Parliamentary Motions",
                "Democratic Voting",
                "Constitutional Review",
                "Crisis Management"
            ],
            "status": "operational",
            "constitutional_compliance": True,
            "parliamentary_accountability": True,
            "democratic_oversight": True
        }


# Global exception handler
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """
    Custom HTTP exception handler with constitutional logging.
    
    Ensures all errors are properly logged for parliamentary accountability
    and constitutional oversight.
    """
    with logfire.span("api_exception_handler") as span:
        span.set_attribute("status_code", exc.status_code)
        span.set_attribute("detail", str(exc.detail))
        span.set_attribute("path", str(request.url.path))
        
        # Log exception for parliamentary accountability
        try:
            deps = await get_triad_deps()
            await deps.log_event("api_exception", {
                "status_code": exc.status_code,
                "detail": str(exc.detail),
                "path": str(request.url.path),
                "method": request.method,
                "constitutional_accountability": True
            })
        except Exception as log_error:
            logfire.error("Failed to log API exception", error=str(log_error))
        
        # Return constitutional error response
        error_response = ErrorResponse(
            error_code=f"HTTP_{exc.status_code}",
            error_message=str(exc.detail),
            constitutional_violation=exc.status_code == 403,  # Forbidden indicates constitutional violation
            parliamentary_accountability=True,
            details={
                "status_code": exc.status_code,
                "path": str(request.url.path),
                "method": request.method
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump()
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.
    
    Ensures system stability and constitutional accountability
    even during unexpected errors.
    """
    with logfire.span("api_global_exception_handler") as span:
        span.set_attribute("exception_type", type(exc).__name__)
        span.set_attribute("exception_message", str(exc))
        span.set_attribute("path", str(request.url.path))
        
        logfire.error(
            "Unhandled API exception",
            exception_type=type(exc).__name__,
            exception_message=str(exc),
            path=str(request.url.path),
            method=request.method
        )
        
        # Log exception for constitutional accountability
        try:
            deps = await get_triad_deps()
            await deps.log_event("api_unhandled_exception", {
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "path": str(request.url.path),
                "method": request.method,
                "constitutional_accountability": True,
                "requires_oversight": True
            })
        except Exception as log_error:
            logfire.error("Failed to log unhandled exception", error=str(log_error))
        
        # Return constitutional error response
        error_response = ErrorResponse(
            error_code="INTERNAL_SERVER_ERROR",
            error_message="An unexpected error occurred. The incident has been logged for parliamentary oversight.",
            constitutional_violation=False,
            parliamentary_accountability=True,
            details={
                "exception_type": type(exc).__name__,
                "path": str(request.url.path),
                "method": request.method,
                "requires_constitutional_review": True
            }
        )
        
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )


# Health check middleware
@app.middleware("http")
async def constitutional_compliance_middleware(request: Request, call_next):
    """
    Constitutional compliance middleware.
    
    Ensures all requests are processed with constitutional oversight
    and parliamentary accountability.
    """
    with logfire.span("constitutional_compliance_middleware") as span:
        span.set_attribute("path", str(request.url.path))
        span.set_attribute("method", request.method)
        
        # Add constitutional headers
        request.headers.__dict__["_list"].append(
            (b"x-constitutional-oversight", b"true")
        )
        request.headers.__dict__["_list"].append(
            (b"x-parliamentary-accountability", b"true")
        )
        
        # Process request
        response = await call_next(request)
        
        # Add constitutional response headers
        response.headers["X-Constitutional-Framework"] = "Westminster-Parliamentary-v1.0"
        response.headers["X-Democratic-Accountability"] = "true"
        response.headers["X-Parliamentary-Oversight"] = "active"
        response.headers["X-Separation-Of-Powers"] = "maintained"
        
        return response


if __name__ == "__main__":
    """
    Run the Triad Model API server.
    
    Starts the FastAPI application with constitutional oversight
    and parliamentary accountability enabled.
    """
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True,
        server_header=False,
        date_header=False
    )