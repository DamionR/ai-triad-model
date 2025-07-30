#!/usr/bin/env python3
"""
Triad Model Startup Script

Bootstrap script for the Westminster Parliamentary AI System
with constitutional framework initialization.
"""

import asyncio
import sys
import os
from pathlib import Path
import argparse
import signal
from typing import Optional

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import logfire
from triad.core.config import load_config, ConfigurationError
from triad.core.constitutional import ConstitutionalFramework


class TriadModelServer:
    """
    Triad Model server manager.
    
    Handles server startup, shutdown, and constitutional framework
    initialization with Westminster parliamentary compliance.
    """
    
    def __init__(self, environment: Optional[str] = None):
        self.environment = environment or os.getenv("TRIAD_ENV", "development")
        self.config = None
        self.constitutional_framework = None
        self.server_process = None
        
    async def initialize(self):
        """Initialize the Triad Model system."""
        try:
            # Load configuration
            logfire.info("Loading Triad Model configuration", environment=self.environment)
            self.config = load_config(self.environment)
            
            # Initialize constitutional framework
            logfire.info("Initializing constitutional framework")
            self.constitutional_framework = ConstitutionalFramework()
            await self.constitutional_framework.initialize({
                "framework_version": self.config.constitutional.framework_version,
                "constitutional_oversight": self.config.constitutional.oversight_enabled,
                "parliamentary_accountability": self.config.constitutional.parliamentary_accountability,
                "separation_of_powers": self.config.constitutional.separation_of_powers,
                "rule_of_law": self.config.constitutional.rule_of_law,
                "democratic_principles": self.config.constitutional.democratic_principles
            })
            
            # Validate constitutional compliance
            compliance = self.constitutional_framework.validate_compliance({
                "agents": ["planner_agent", "executor_agent", "evaluator_agent", "overwatch_agent"],
                "parliamentary_procedures": True,
                "separation_of_powers": True
            })
            
            if not compliance["constitutional_compliant"]:
                raise ConfigurationError(f"Constitutional compliance failure: {compliance['violations']}")
            
            logfire.info(
                "Triad Model initialized successfully",
                environment=self.environment,
                constitutional_framework=self.config.constitutional.framework_version,
                constitutional_compliant=compliance["constitutional_compliant"]
            )
            
        except Exception as e:
            logfire.error("Failed to initialize Triad Model", error=str(e))
            raise
    
    async def start_server(self):
        """Start the FastAPI server."""
        import uvicorn
        
        try:
            logfire.info("Starting Triad Model API server", 
                        host=self.config.server.host, 
                        port=self.config.server.port)
            
            # Configure uvicorn
            uvicorn_config = uvicorn.Config(
                app="triad.api.main:app",
                host=self.config.server.host,
                port=self.config.server.port,
                reload=self.config.server.reload,
                workers=1 if self.config.server.reload else self.config.server.workers,
                log_level="info",
                access_log=True,
                server_header=False,
                date_header=False
            )
            
            # Start server
            server = uvicorn.Server(uvicorn_config)
            await server.serve()
            
        except Exception as e:
            logfire.error("Failed to start server", error=str(e))
            raise
    
    async def shutdown(self):
        """Shutdown the Triad Model system."""
        logfire.info("Shutting down Triad Model system")
        
        try:
            # Shutdown constitutional framework
            if self.constitutional_framework:
                await self.constitutional_framework.shutdown()
            
            logfire.info("Triad Model shutdown completed")
            
        except Exception as e:
            logfire.error("Error during shutdown", error=str(e))
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logfire.info("Received shutdown signal", signal=signum)
            asyncio.create_task(self.shutdown())
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """Main entry point for Triad Model server."""
    parser = argparse.ArgumentParser(description="Triad Model - Westminster Parliamentary AI System")
    parser.add_argument(
        "--environment", "-e",
        default=None,
        help="Environment to run in (development, staging, production)"
    )
    parser.add_argument(
        "--config-dir", "-c",
        default="config",
        help="Configuration directory path"
    )
    parser.add_argument(
        "--check-config", 
        action="store_true",
        help="Check configuration and exit"
    )
    parser.add_argument(
        "--constitutional-check",
        action="store_true", 
        help="Perform constitutional compliance check and exit"
    )
    
    args = parser.parse_args()
    
    # Configure Logfire
    logfire.configure(
        service_name="triad-model-startup",
        service_version="1.0.0"
    )
    
    try:
        # Initialize server
        server = TriadModelServer(args.environment)
        await server.initialize()
        
        # Configuration check mode
        if args.check_config:
            logfire.info("Configuration check passed", environment=server.environment)
            print(f"✅ Configuration valid for environment: {server.environment}")
            return 0
        
        # Constitutional compliance check mode
        if args.constitutional_check:
            compliance = server.constitutional_framework.validate_compliance({
                "agents": ["planner_agent", "executor_agent", "evaluator_agent", "overwatch_agent"],
                "parliamentary_procedures": True,
                "separation_of_powers": True
            })
            
            if compliance["constitutional_compliant"]:
                print("✅ Constitutional compliance check passed")
                print(f"   Framework: {server.config.constitutional.framework_version}")
                print(f"   Oversight: {server.config.constitutional.oversight_enabled}")
                print(f"   Parliamentary Accountability: {server.config.constitutional.parliamentary_accountability}")
                return 0
            else:
                print("❌ Constitutional compliance check failed")
                print(f"   Violations: {compliance.get('violations', [])}")
                return 1
        
        # Setup signal handlers
        server.setup_signal_handlers()
        
        # Start server
        logfire.info("Starting Westminster Parliamentary AI System")
        print("🏛️  Triad Model - Westminster Parliamentary AI System")
        print(f"   Environment: {server.environment}")
        print(f"   Constitutional Framework: {server.config.constitutional.framework_version}")
        print(f"   Server: http://{server.config.server.host}:{server.config.server.port}")
        print(f"   API Documentation: http://{server.config.server.host}:{server.config.server.port}/docs")
        print("   Constitutional Oversight: ✅ Active")
        print("   Parliamentary Accountability: ✅ Active")
        print("   Separation of Powers: ✅ Maintained")
        print("")
        
        await server.start_server()
        
    except ConfigurationError as e:
        logfire.error("Configuration error", error=str(e))
        print(f"❌ Configuration Error: {e}")
        return 1
    except KeyboardInterrupt:
        logfire.info("Received keyboard interrupt")
        print("\n🛑 Shutting down Triad Model...")
        return 0
    except Exception as e:
        logfire.error("Startup failed", error=str(e))
        print(f"❌ Startup failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))