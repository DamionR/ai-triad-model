#!/usr/bin/env python3
"""
Setup Prisma Database for Triad Model

Initializes Prisma database schema and generates client code
for the Westminster Parliamentary AI System.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a shell command and return success status."""
    print(f"📋 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("🔧 Setting up Prisma for Triad Model\n")
    
    # Check if we're in the right directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Set default database URL if not provided
    db_url = os.getenv("DATABASE_URL", "file:./data/triad.db")
    os.environ["DATABASE_URL"] = db_url
    
    print(f"📍 Project root: {project_root}")
    print(f"🗄️  Database URL: {db_url}\n")
    
    # Create data directory for SQLite
    if "file:" in db_url:
        data_dir = project_root / "data"
        data_dir.mkdir(exist_ok=True)
        print(f"📁 Created data directory: {data_dir}")
    
    # Setup steps
    steps = [
        ("prisma generate", "Generate Prisma client"),
        ("prisma db push", "Push schema to database"),
    ]
    
    all_success = True
    
    for command, description in steps:
        if not run_command(command, description):
            all_success = False
            break
    
    if all_success:
        print("\n✅ Prisma setup completed successfully!")
        print("\n🚀 Next steps:")
        print("   1. Start the Triad Model server: python scripts/start.py")
        print("   2. Access API docs: http://localhost:8000/docs")
        print("   3. Check constitutional status: http://localhost:8000/api/v1/parliamentary/constitutional-status")
        
        # Create initial agents if database is empty
        if run_command("python -c \"from triad.database.prisma_client import prisma_client; import asyncio; asyncio.run(prisma_client.connect()); print('Database connected')\"", "Test database connection"):
            print("\n🏛️  Database ready for Westminster Parliamentary AI System!")
        
        return 0
    else:
        print("\n❌ Prisma setup failed!")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure you're in a virtual environment")
        print("   2. Install dependencies: pip install -r requirements.txt")
        print("   3. Check DATABASE_URL environment variable")
        print("   4. For SQLite, ensure data directory is writable")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())