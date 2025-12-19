#!/usr/bin/env python3
"""
Test Runner Script for Setlist Project

This script runs both backend and frontend tests to show the current TDD status.
Following the Red-Green-Refactor cycle, we expect tests to fail initially
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None, capture_output=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=capture_output,
            text=True
        )
        return result
    except Exception as e:
        print(f"Error running command '{command}': {e}")
        return None

def check_backend_tests():
    """Run backend tests and return results."""
    print("🔍 Running Backend Tests (Python/FastAPI)...")
    print("=" * 50)
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False
    
    # Check if dependencies are installed
    result = run_command("python -c 'import fastapi, pytest'", cwd=backend_dir)
    if result and result.returncode != 0:
        print("⚠️  Backend dependencies not installed. Installing...")
        install_result = run_command("pip install -r requirements.txt", cwd=backend_dir)
        if install_result and install_result.returncode != 0:
            print("❌ Failed to install backend dependencies!")
            return False
    
    # Run tests
    test_result = run_command("python -m pytest tests/ -v", cwd=backend_dir)
    
    if test_result:
        print(test_result.stdout)
        if test_result.stderr:
            print("STDERR:", test_result.stderr)
        
        if test_result.returncode == 0:
            print("✅ All backend tests passed!")
            return True
        else:
            print(f"❌ Backend tests failed (exit code: {test_result.returncode})")
            return False
    else:
        print("❌ Failed to run backend tests!")
        return False

def check_frontend_tests():
    """Run frontend tests and return results."""
    print("\n🔍 Running Frontend Tests (React/TypeScript)...")
    print("=" * 50)
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return False
    
    # Check if node_modules exists
    if not (frontend_dir / "node_modules").exists():
        print("⚠️  Frontend dependencies not installed. Installing...")
        install_result = run_command("npm install", cwd=frontend_dir)
        if install_result and install_result.returncode != 0:
            print("❌ Failed to install frontend dependencies!")
            return False
    
    # Run tests
    test_result = run_command("npm test -- --passWithNoTests", cwd=frontend_dir)
    
    if test_result:
        print(test_result.stdout)
        if test_result.stderr:
            print("STDERR:", test_result.stderr)
        
        if test_result.returncode == 0:
            print("✅ All frontend tests passed!")
            return True
        else:
            print(f"❌ Frontend tests failed (exit code: {test_result.returncode})")
            return False
    else:
        print("❌ Failed to run frontend tests!")
        return False

def check_project_structure():
    """Check if the project structure is properly set up."""
    print("🔍 Checking Project Structure...")
    print("=" * 50)
    
    required_dirs = [
        "backend",
        "backend/app",
        "backend/app/api/v1/endpoints",
        "backend/app/core",
        "backend/tests",
        "frontend",
        "frontend/src",
        "frontend/src/components",
        "frontend/src/pages",
        "frontend/src/hooks",
        "frontend/src/types",
        "frontend/src/api",
        "shared"
    ]
    
    required_files = [
        "docker-compose.yml",
        "env.example",
        "backend/requirements.txt",
        "backend/Dockerfile",
        "backend/app/main.py",
        "frontend/package.json",
        "frontend/Dockerfile",
        "frontend/vite.config.ts",
        "frontend/tsconfig.json",
        "shared/types.py"
    ]
    
    all_good = True
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - MISSING")
            all_good = False
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_good = False
    
    return all_good

def main():
    """Main function to run all checks."""
    print("🎵 Setlist Project - TDD Status Check")
    print("=" * 60)
    print("Following the Red-Green-Refactor cycle:")
    print("🔴 RED: Tests should fail initially (expected)")
    print("🟢 GREEN: Implement features to make tests pass")
    print("🔄 REFACTOR: Clean up and optimize code")
    print("=" * 60)
    
    # Check project structure
    structure_ok = check_project_structure()
    
    if not structure_ok:
        print("\n❌ Project structure incomplete. Please fix missing files/directories first.")
        return
    
    print("\n" + "=" * 60)
    
    # Run tests
    backend_ok = check_backend_tests()
    frontend_ok = check_frontend_tests()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TDD STATUS SUMMARY")
    print("=" * 60)
    
    if backend_ok and frontend_ok:
        print("🎉 All tests are passing! Ready for refactoring phase.")
        print("🔄 Next step: Refactor and optimize the code")
    elif backend_ok:
        print("🟢 Backend tests passing, 🔴 Frontend tests failing")
        print("🎯 Focus on implementing frontend features")
    elif frontend_ok:
        print("🔴 Backend tests failing, 🟢 Frontend tests passing")
        print("🎯 Focus on implementing backend features")
    else:
        print("🔴 Both backend and frontend tests failing (expected in TDD)")
        print("🎯 Next step: Implement features to make tests pass")
    
    print("\n📝 TDD Workflow:")
    print("1. Write failing tests (RED) ✅")
    print("2. Implement minimal code to pass tests (GREEN) 🔄")
    print("3. Refactor and optimize (REFACTOR) 🔄")
    
    if not (backend_ok and frontend_ok):
        print("\n💡 Expected Behavior:")
        print("- Tests are failing because features aren't implemented yet")
        print("- This is the RED phase of TDD")
        print("- Next: Implement features to make tests pass (GREEN phase)")

if __name__ == "__main__":
    main()
