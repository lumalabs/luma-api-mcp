#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.

# --- Helper Functions ---
info() {
    echo "[INFO] $1"
}

warn() {
    echo "[WARN] $1"
}

error() {
    echo "[ERROR] $1" >&2
    exit 1
}

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# --- OS Detection ---
OS="$(uname -s)"
case "$OS" in
    Linux*)     PLATFORM=linux;;
    Darwin*)    PLATFORM=macos;;
    CYGWIN*|MINGW*|MSYS*) PLATFORM=windows;;
    *)          error "Unsupported operating system: $OS";;
esac

info "Detected platform: $PLATFORM"

# --- Dependency Installation ---
JQ_INSTALLED=false
UV_INSTALLED=false

# Check for jq
if command_exists jq; then
    info "jq is already installed."
    JQ_INSTALLED=true
else
    info "jq not found. Attempting installation..."
    case "$PLATFORM" in
        linux)
            if command_exists apt-get; then
                sudo apt-get update && sudo apt-get install -y jq || warn "Failed to install jq using apt-get."
            elif command_exists yum; then
                sudo yum install -y jq || warn "Failed to install jq using yum."
            elif command_exists dnf; then
                 sudo dnf install -y jq || warn "Failed to install jq using dnf."
            elif command_exists pacman; then
                 sudo pacman -Syu --noconfirm jq || warn "Failed to install jq using pacman."
            else
                warn "Could not find apt-get, yum, dnf, or pacman. Please install jq manually."
            fi
            ;;
        macos)
            if command_exists brew; then
                brew install jq || warn "Failed to install jq using Homebrew."
            else
                warn "Homebrew not found. Please install jq manually (e.g., 'brew install jq')."
            fi
            ;;
        windows)
             if command_exists pacman; then # MSYS2/Git Bash likely has pacman
                 pacman -S --noconfirm jq || warn "Failed to install jq using pacman."
             elif command_exists choco; then
                 choco install jq || warn "Failed to install jq using Chocolatey."
             else
                warn "Could not find pacman or choco. Please install jq manually."
             fi
             ;;
    esac
    # Re-check after attempting install
    if command_exists jq; then
        info "jq installed successfully."
        JQ_INSTALLED=true
    fi
fi
if [ "$JQ_INSTALLED" = false ]; then
    error "jq is required but could not be installed. Please install it manually and re-run the script."
fi

# Check for uv
if command_exists uv; then
    info "uv is already installed."
    UV_INSTALLED=true
else
    info "uv not found. Attempting installation..."
    # Try pip first if available
    if command_exists pip; then
        pip install uv && UV_INSTALLED=true
    elif command_exists pip3; then
         pip3 install uv && UV_INSTALLED=true
    fi

    # If pip didn't work or isn't available, try curl/sh (Linux/macOS)
    if [ "$UV_INSTALLED" = false ] && [ "$PLATFORM" != "windows" ]; then
        if command_exists curl; then
             info "Attempting uv install via curl | sh ..."
             curl -LsSf https://astral.sh/uv/install.sh | sh && UV_INSTALLED=true
             # Add uv to PATH for the current session if installed this way
             if [ "$UV_INSTALLED" = true ]; then
                 export PATH="$HOME/.cargo/bin:$PATH"
                 if ! command_exists uv; then # Check again after modifying PATH
                     warn "uv installed but might not be in PATH. You may need to restart your shell or add $HOME/.cargo/bin to your PATH manually."
                     UV_INSTALLED=false # Mark as failed if not found in path
                 fi
             fi
        else
             warn "curl not found. Cannot install uv using the recommended script."
        fi
    fi

     # If still not installed, provide guidance
    if [ "$UV_INSTALLED" = false ]; then
         warn "Failed to automatically install uv. Please install it manually (e.g., using pip, pipx, or cargo) and ensure it's in your PATH."
         warn "See: https://github.com/astral-sh/uv"
    else
        # Re-check after attempting install
        if command_exists uv; then
            info "uv installed successfully."
            UV_INSTALLED=true
        else
             warn "uv installation attempted, but the 'uv' command was not found in PATH."
             UV_INSTALLED=false
        fi
    fi

fi
if [ "$UV_INSTALLED" = false ]; then
    error "uv is required but could not be installed or found in PATH. Please install it manually and re-run the script."
fi


# --- Path Configuration ---

# Get uv path
UV_PATH=$(command -v uv)
if [ -z "$UV_PATH" ]; then
    error "Could not find uv executable path even after installation checks."
fi
info "Using uv path: $UV_PATH"

# Get script directory (absolute path)
# https://stackoverflow.com/a/246128/1319998
SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
  SOURCE=$(readlink "$SOURCE")
  [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
SCRIPT_DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
info "Script directory: $SCRIPT_DIR"

# Construct server.py path
SERVER_PY_PATH="$SCRIPT_DIR/server.py"
if [ ! -f "$SERVER_PY_PATH" ]; then
    error "server.py not found in script directory: $SCRIPT_DIR"
fi
info "Using server.py path: $SERVER_PY_PATH"

# Determine Claude config path based on OS
case "$PLATFORM" in
    linux)
        CLAUDE_CONFIG_DIR="$HOME/.config/Claude"
        ;;
    macos)
        CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
        ;;
    windows)
        # Assuming Git Bash/MSYS environment where $HOME maps reasonably
        CLAUDE_CONFIG_DIR="$HOME/AppData/Roaming/Claude"
        ;;
esac
CLAUDE_CONFIG_PATH="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

info "Claude config path: $CLAUDE_CONFIG_PATH"

# --- User Input ---
read -p "Enter your LUMA_API_KEY: " LUMA_API_KEY
if [ -z "$LUMA_API_KEY" ]; then
    error "LUMA_API_KEY cannot be empty."
fi

# --- JSON Modification ---

# Ensure config directory exists
mkdir -p "$CLAUDE_CONFIG_DIR" || error "Failed to create Claude config directory: $CLAUDE_CONFIG_DIR"

# Ensure config file exists, creating a valid empty JSON object if it doesn't
if [ ! -f "$CLAUDE_CONFIG_PATH" ]; then
    info "Claude config file not found. Creating new file."
    echo "{}" > "$CLAUDE_CONFIG_PATH" || error "Failed to create Claude config file: $CLAUDE_CONFIG_PATH"
elif ! jq empty "$CLAUDE_CONFIG_PATH" > /dev/null 2>&1; then
     info "Claude config file exists but is not valid JSON. Overwriting with empty object."
     echo "{}" > "$CLAUDE_CONFIG_PATH" || error "Failed to overwrite invalid Claude config file: $CLAUDE_CONFIG_PATH"
fi


info "Updating Claude configuration..."

# Use jq to add/update the mcpServers entry
jq \
  --arg uv_path "$UV_PATH" \
  --arg server_path "$SERVER_PY_PATH" \
  --arg api_key "$LUMA_API_KEY" \
  '.mcpServers."Luma MCP" = {
      command: $uv_path,
      args: [
          "run",
          "--with", "mcp[cli]",
          "--with", "aiohttp",
          "mcp",
          "run", $server_path
      ],
      env: {
          LUMA_API_KEY: $api_key
      }
  }' "$CLAUDE_CONFIG_PATH" > "$CLAUDE_CONFIG_PATH.tmp" \
  && mv "$CLAUDE_CONFIG_PATH.tmp" "$CLAUDE_CONFIG_PATH"

if [ $? -ne 0 ]; then
    error "Failed to update Claude config file using jq."
    # Clean up temporary file if it exists
    rm -f "$CLAUDE_CONFIG_PATH.tmp"
fi

# --- Restart Claude Desktop ---
info "Attempting to restart Claude Desktop application..."
warn "Please save any unsaved work in Claude Desktop, as it will be closed forcefully."
sleep 3 # Give user a moment to read the warning

case "$PLATFORM" in
    linux)
        info "Attempting to kill Claude process on Linux..."
        pkill -f Claude || info "Claude process not found or could not be killed."
        sleep 1
        info "Attempting to launch Claude on Linux..."
        # Try common command names. This might fail depending on installation.
        (claude &) || (Claude &) || warn "Could not automatically launch Claude. Please start it manually."
        ;;
    macos)
        info "Attempting to kill Claude process on macOS..."
        killall Claude || info "Claude process not found or could not be killed."
        # Allow some time for the process to terminate
        sleep 2
        info "Attempting to launch Claude on macOS..."
        open -a Claude || warn "Could not automatically launch Claude. Please start it manually."
        ;;
    windows)
        info "Attempting to kill Claude process on Windows..."
        taskkill /IM Claude.exe /F > /dev/null 2>&1 || info "Claude process not found or could not be killed."
        sleep 1
        info "Attempting to launch Claude on Windows..."
        # Try starting via typical Program Files locations in Git Bash/MSYS
        if [ -f "/c/Program Files/Claude/Claude.exe" ]; then
           (start "" "/c/Program Files/Claude/Claude.exe" &) || warn "Could not automatically launch Claude from Program Files. Please start it manually."
        elif [ -f "/c/Program Files (x86)/Claude/Claude.exe" ]; then
            (start "" "/c/Program Files (x86)/Claude/Claude.exe" &) || warn "Could not automatically launch Claude from Program Files (x86). Please start it manually."
        else
            # Try starting assuming it's in PATH
            (start Claude.exe &) || warn "Could not automatically launch Claude (not found in common locations or PATH). Please start it manually."
        fi
        ;;
esac

sleep 2 # Give app time to potentially start before script exits

info "Successfully configured Luma MCP in Claude Desktop!"
info "You may need to restart the Claude Desktop application for changes to take effect."
