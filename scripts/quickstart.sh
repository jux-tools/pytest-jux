#!/usr/bin/env bash
#
# pytest-jux Quick-Start Setup Script
#
# This script helps you get started with pytest-jux by:
# 1. Generating signing keys
# 2. Creating a configuration file
# 3. Running a sample test report
# 4. Signing and verifying the report
#
# Usage:
#   bash scripts/quickstart.sh
#   bash scripts/quickstart.sh --non-interactive  # Use defaults
#

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
RESET='\033[0m'

# Configuration
INTERACTIVE=true
JUX_DIR="${HOME}/.jux"
KEY_PATH="${JUX_DIR}/quickstart-key.pem"
CERT_PATH="${JUX_DIR}/quickstart-cert.pem"
CONFIG_PATH="${JUX_DIR}/quickstart-config"
SAMPLE_REPORT="quickstart-report.xml"
SIGNED_REPORT="quickstart-report-signed.xml"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --non-interactive)
            INTERACTIVE=false
            shift
            ;;
        --help)
            echo "pytest-jux Quick-Start Setup Script"
            echo ""
            echo "Usage: bash scripts/quickstart.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --non-interactive  Use default values without prompting"
            echo "  --help             Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${RESET}"
            exit 1
            ;;
    esac
done

# Helper functions
print_header() {
    echo ""
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "${BOLD}${BLUE}$1${RESET}"
    echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo ""
}

print_step() {
    echo -e "${GREEN}✓${RESET} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${RESET} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${RESET} $1"
}

print_error() {
    echo -e "${RED}✗${RESET} $1"
}

prompt_yes_no() {
    local prompt="$1"
    local default="${2:-y}"

    if [ "$INTERACTIVE" = false ]; then
        echo "$default"
        return
    fi

    local choice
    if [ "$default" = "y" ]; then
        read -p "$prompt [Y/n]: " choice
        choice=${choice:-y}
    else
        read -p "$prompt [y/N]: " choice
        choice=${choice:-n}
    fi

    echo "$choice"
}

prompt_input() {
    local prompt="$1"
    local default="$2"

    if [ "$INTERACTIVE" = false ]; then
        echo "$default"
        return
    fi

    local value
    read -p "$prompt [$default]: " value
    echo "${value:-$default}"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 command not found"
        return 1
    fi
    return 0
}

# Welcome message
clear
print_header "pytest-jux Quick-Start Setup"

echo -e "${BOLD}Welcome to pytest-jux!${RESET}"
echo ""
echo "This script will guide you through the initial setup:"
echo "  1. Generate signing keys"
echo "  2. Create a configuration file"
echo "  3. Generate a sample test report"
echo "  4. Sign and verify the report"
echo ""

if [ "$INTERACTIVE" = true ]; then
    read -p "Press Enter to continue..."
fi

# Step 1: Check prerequisites
print_header "Step 1: Checking Prerequisites"

MISSING_DEPS=false

print_info "Checking for required commands..."
if check_command python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_step "Python found: $PYTHON_VERSION"
else
    MISSING_DEPS=true
fi

if check_command pip; then
    print_step "pip found"
else
    MISSING_DEPS=true
fi

if [ "$MISSING_DEPS" = true ]; then
    print_error "Missing required dependencies"
    echo ""
    echo "Please install:"
    echo "  - Python 3.11+"
    echo "  - pip"
    exit 1
fi

# Check if pytest-jux is installed
if python3 -c "import pytest_jux" 2>/dev/null; then
    print_step "pytest-jux is installed"

    # Get version
    JUX_VERSION=$(python3 -c "import pytest_jux; print(pytest_jux.__version__)" 2>/dev/null || echo "unknown")
    print_info "Version: $JUX_VERSION"
else
    print_warning "pytest-jux is not installed"

    choice=$(prompt_yes_no "Would you like to install it now?")
    if [[ "$choice" =~ ^[Yy] ]]; then
        print_info "To install pytest-jux, run:"
        print_info "  pip install pytest-jux"
        print_info ""
        print_info "Then re-run this script."
        exit 1
    else
        print_info "Continuing without installation (some features may not work)"
    fi
fi

# Step 2: Setup directory structure
print_header "Step 2: Setting Up Directory Structure"

print_info "Creating $JUX_DIR directory..."
mkdir -p "$JUX_DIR"
print_step "Directory created: $JUX_DIR"

# Step 3: Generate signing keys
print_header "Step 3: Generating Signing Keys"

if [ -f "$KEY_PATH" ]; then
    print_warning "Keys already exist at $KEY_PATH"

    choice=$(prompt_yes_no "Overwrite existing keys?" "n")
    if [[ ! "$choice" =~ ^[Yy] ]]; then
        print_info "Using existing keys"
        KEY_EXISTS=true
    fi
fi

if [ "${KEY_EXISTS:-false}" = false ]; then
    print_info "Key type options:"
    echo "  1. RSA-2048 (fast, good for development)"
    echo "  2. RSA-4096 (slower, good for production)"
    echo "  3. ECDSA-P256 (fast, modern)"
    echo ""

    KEY_TYPE_CHOICE=$(prompt_input "Select key type [1-3]" "1")

    case "$KEY_TYPE_CHOICE" in
        1)
            KEY_TYPE="rsa"
            KEY_BITS="2048"
            ;;
        2)
            KEY_TYPE="rsa"
            KEY_BITS="4096"
            ;;
        3)
            KEY_TYPE="ecdsa"
            KEY_CURVE="P-256"
            ;;
        *)
            print_warning "Invalid choice, using RSA-2048"
            KEY_TYPE="rsa"
            KEY_BITS="2048"
            ;;
    esac

    print_info "Generating $KEY_TYPE keys..."

    if command -v jux-keygen &> /dev/null; then
        if [ "$KEY_TYPE" = "rsa" ]; then
            jux-keygen --type rsa --bits "$KEY_BITS" --output "$KEY_PATH" --cert
        else
            jux-keygen --type ecdsa --curve "$KEY_CURVE" --output "$KEY_PATH" --cert
        fi
        print_step "Keys generated: $KEY_PATH"
        print_step "Certificate generated: $CERT_PATH"
    else
        print_error "jux-keygen command not found"
        print_info "Skipping key generation (install pytest-jux first)"
    fi
fi

# Step 4: Create configuration
print_header "Step 4: Creating Configuration File"

if [ -f "$CONFIG_PATH" ]; then
    print_warning "Configuration already exists at $CONFIG_PATH"

    choice=$(prompt_yes_no "Overwrite existing configuration?" "n")
    if [[ ! "$choice" =~ ^[Yy] ]]; then
        print_info "Using existing configuration"
        CONFIG_EXISTS=true
    fi
fi

if [ "${CONFIG_EXISTS:-false}" = false ]; then
    print_info "Configuration templates:"
    echo "  1. Minimal (basic options)"
    echo "  2. Development (local signing, no API)"
    echo "  3. Full (all options with comments)"
    echo ""

    TEMPLATE_CHOICE=$(prompt_input "Select template [1-3]" "2")

    case "$TEMPLATE_CHOICE" in
        1) TEMPLATE="minimal" ;;
        2) TEMPLATE="development" ;;
        3) TEMPLATE="full" ;;
        *)
            print_warning "Invalid choice, using development template"
            TEMPLATE="development"
            ;;
    esac

    print_info "Creating configuration with $TEMPLATE template..."

    if command -v jux-config &> /dev/null; then
        jux-config init --path "$CONFIG_PATH" --template "$TEMPLATE" --force

        # Update configuration with generated key paths
        if [ -f "$KEY_PATH" ]; then
            sed -i.bak "s|# key_path = .*|key_path = $KEY_PATH|" "$CONFIG_PATH"
            sed -i.bak "s|# cert_path = .*|cert_path = $CERT_PATH|" "$CONFIG_PATH"
            rm -f "${CONFIG_PATH}.bak"
        fi

        print_step "Configuration created: $CONFIG_PATH"
    else
        print_error "jux-config command not found"
        print_info "Skipping configuration creation (install pytest-jux first)"
    fi
fi

# Step 5: Generate sample test report
print_header "Step 5: Generating Sample Test Report"

print_info "Creating a sample JUnit XML report..."

cat > "$SAMPLE_REPORT" << 'XMLEOF'
<?xml version="1.0" encoding="utf-8"?>
<testsuites>
  <testsuite name="pytest" errors="0" failures="0" skipped="0" tests="3" time="0.123">
    <properties>
      <property name="environment" value="quickstart"/>
      <property name="timestamp" value="2025-10-20T12:00:00"/>
    </properties>
    <testcase classname="test_sample" name="test_addition" time="0.001"/>
    <testcase classname="test_sample" name="test_subtraction" time="0.001"/>
    <testcase classname="test_sample" name="test_multiplication" time="0.001"/>
  </testsuite>
</testsuites>
XMLEOF

print_step "Sample report created: $SAMPLE_REPORT"

# Step 6: Sign the report
print_header "Step 6: Signing the Test Report"

if [ -f "$KEY_PATH" ]; then
    print_info "Signing report with generated keys..."

    if command -v jux-sign &> /dev/null; then
        jux-sign "$SAMPLE_REPORT" --key "$KEY_PATH" --cert "$CERT_PATH" --output "$SIGNED_REPORT"
        print_step "Report signed: $SIGNED_REPORT"
    else
        print_error "jux-sign command not found"
        print_info "Skipping signing (install pytest-jux first)"
    fi
else
    print_warning "No signing keys available, skipping signing"
fi

# Step 7: Verify the signature
print_header "Step 7: Verifying the Signature"

if [ -f "$SIGNED_REPORT" ]; then
    print_info "Verifying signature..."

    if command -v jux-verify &> /dev/null; then
        if jux-verify "$SIGNED_REPORT" --cert "$CERT_PATH"; then
            print_step "Signature verification: PASSED"
        else
            print_error "Signature verification: FAILED"
        fi
    else
        print_error "jux-verify command not found"
        print_info "Skipping verification (install pytest-jux first)"
    fi
else
    print_warning "No signed report available, skipping verification"
fi

# Summary
print_header "Quick-Start Complete!"

echo -e "${GREEN}${BOLD}✓ Setup completed successfully!${RESET}"
echo ""
echo "What was created:"
echo "  • Signing keys: $KEY_PATH"
echo "  • Certificate: $CERT_PATH"
echo "  • Configuration: $CONFIG_PATH"
echo "  • Sample report: $SAMPLE_REPORT"
if [ -f "$SIGNED_REPORT" ]; then
    echo "  • Signed report: $SIGNED_REPORT"
fi
echo ""
echo "Next steps:"
echo "  1. Review the configuration: cat $CONFIG_PATH"
echo "  2. Read the Quick Start tutorial: docs/tutorials/quick-start.md"
echo "  3. Try signing your own reports: jux-sign <report.xml> --key $KEY_PATH"
echo "  4. Integrate with pytest: pytest --junit-xml=report.xml --jux-sign"
echo ""
echo "Documentation: https://github.com/jux-tools/pytest-jux/blob/main/docs/INDEX.md"
echo ""
echo -e "${BOLD}Happy testing with pytest-jux!${RESET}"
echo ""
