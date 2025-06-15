#!/usr/bin/env python3
import os
import sys
import venv
import subprocess
import shutil
from pathlib import Path

def print_step(message):
    """Print a formatted step message."""
    print(f"\n{'='*80}\n{message}\n{'='*80}")

def run_command(command, check=True):
    """Run a shell command and handle errors."""
    try:
        subprocess.run(command, shell=True, check=check)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error details: {e}")
        return False

def detect_package_manager():
    """Detect available system package manager."""
    if shutil.which('dnf'):
        return 'dnf'
    if shutil.which('apt'):
        return 'apt'
    if shutil.which('brew'):
        return 'brew'
    return None


def is_node_installed():
    """Check if Node.js and npm are installed."""
    return shutil.which('node') and shutil.which('npm')

def main():
    # Get the project root directory
    project_root = Path.cwd()

    print_step("Starting Dark Station Chronicles Setup")

    # Check for required system packages
    print_step("Checking system requirements...")

    # Check for Node.js and npm
    if not is_node_installed():
        pm = detect_package_manager()
        print("Node.js and npm are required but were not found.")
        if pm == 'dnf':
            print("Install them with: sudo dnf install -y nodejs npm")
        elif pm == 'apt':
            print("Install them with: sudo apt update && sudo apt install -y nodejs npm")
        elif pm == 'brew':
            print("Install them with: brew install node")
        else:
            print("Please install Node.js and npm using your system's package manager.")
        sys.exit(1)

    # Create directory structure
    print_step("Creating directory structure...")
    directories = [
        'src/api',
        'src/game_logic',
        'src/ai',
        'frontend',
        'config',
    ]

    for directory in directories:
        Path(project_root / directory).mkdir(parents=True, exist_ok=True)

    # Create virtual environment
    print_step("Creating Python virtual environment...")
    venv_dir = project_root / 'venv'
    venv.create(venv_dir, with_pip=True)

    # Create requirements.txt
    print_step("Creating requirements.txt...")
    requirements = [
        'fastapi',
        'uvicorn',
        'anthropic',
        'python-dotenv',
        'pydantic',
        'llama-cpp-python'
    ]

    with open(project_root / 'requirements.txt', 'w') as f:
        f.write('\n'.join(requirements))

    # Install Python dependencies
    print_step("Installing Python dependencies...")
    pip_path = venv_dir / 'bin' / 'pip'
    run_command(f"{pip_path} install -r requirements.txt")

    # Set up frontend
    print_step("Setting up frontend...")
    if run_command('cd frontend && npm create vite@latest . -- --template react'):
        run_command('cd frontend && npm install')
        run_command('cd frontend && npm install lucide-react @tailwindcss/typography tailwindcss postcss autoprefixer')

    # Create .env template
    print_step("Creating .env template...")
    env_template = """# API Keys
ANTHROPIC_API_KEY=your_api_key_here

# Server Configuration
HOST=localhost
PORT=8000

# Development Settings
DEBUG=True"""

    with open(project_root / '.env.template', 'w') as f:
        f.write(env_template)

    print_step("Setup completed!")
    print("\nNext steps:")
    print("1. Copy .env.template to .env and add your Anthropic API key")
    print("2. Run the start script: ./start-game.sh")

if __name__ == "__main__":
    main()
