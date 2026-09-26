# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for jux-inspect command."""

import re
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest
from lxml import etree

from pytest_jux.canonicalizer import load_xml
from pytest_jux.commands.inspect import main
from pytest_jux.commands.keygen import (
    generate_rsa_key,
    generate_self_signed_cert,
    save_key,
)
from pytest_jux.signer import sign_xml


def _plain(text: str) -> str:
    """Strip ANSI styling, which rich emits when FORCE_COLOR is set."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


@pytest.fixture
def unsigned_xml(tmp_path: Path) -> Path:
    """Create an unsigned XML file."""
    xml_content = """<?xml version="1.0"?>
<testsuites>
    <testsuite name="test-suite" tests="10" failures="2" errors="1" skipped="1">
        <testcase name="test_pass" time="0.1"/>
        <testcase name="test_fail" time="0.2">
            <failure>Assertion failed</failure>
        </testcase>
        <testcase name="test_error" time="0.3">
            <error>RuntimeError</error>
        </testcase>
        <testcase name="test_skip" time="0.0">
            <skipped>Not implemented</skipped>
        </testcase>
    </testsuite>
</testsuites>
"""
    xml_path = tmp_path / "unsigned.xml"
    xml_path.write_text(xml_content)
    return xml_path


@pytest.fixture
def signed_xml(tmp_path: Path) -> Path:
    """Create a signed XML file."""
    xml_content = """<?xml version="1.0"?>
<testsuites>
    <testsuite name="test-suite" tests="5" failures="1" errors="0" skipped="0">
        <testcase name="test_pass" time="0.1"/>
        <testcase name="test_fail" time="0.2">
            <failure>Assertion failed</failure>
        </testcase>
    </testsuite>
</testsuites>
"""
    xml_path = tmp_path / "test.xml"
    xml_path.write_text(xml_content)

    # Generate key and certificate
    key = generate_rsa_key(2048)
    key_path = tmp_path / "key.pem"
    save_key(key, key_path)

    cert_path = tmp_path / "cert.crt"
    generate_self_signed_cert(key, cert_path)
    cert = cert_path.read_bytes()

    # Sign XML
    tree = load_xml(xml_path)
    signed_tree = sign_xml(tree, key, cert)

    # Save signed XML
    signed_path = tmp_path / "signed.xml"
    signed_path.write_bytes(
        etree.tostring(signed_tree, xml_declaration=True, encoding="utf-8")
    )

    return signed_path


class TestInspectCommand:
    """Tests for jux-inspect CLI command."""

    def test_inspects_unsigned_xml(self, unsigned_xml: Path) -> None:
        """Test inspection of unsigned XML."""
        captured_stdout = StringIO()

        with (
            patch.object(sys, "argv", ["jux-inspect", "-i", str(unsigned_xml)]),
            patch("sys.stdout", captured_stdout),
        ):
            exit_code = main()

        assert exit_code == 0
        output = _plain(captured_stdout.getvalue())
        assert "Test Report Summary" in output
        assert "Tests" in output and "10" in output
        assert "Failures" in output and "2" in output
        assert "Errors" in output and "1" in output
        assert "Skipped" in output and "1" in output
        assert "Signature: None" in output or "No signature" in output

    def test_inspects_signed_xml(self, signed_xml: Path) -> None:
        """Test inspection of signed XML."""
        captured_stdout = StringIO()

        with (
            patch.object(sys, "argv", ["jux-inspect", "-i", str(signed_xml)]),
            patch("sys.stdout", captured_stdout),
        ):
            exit_code = main()

        assert exit_code == 0
        output = _plain(captured_stdout.getvalue())
        assert "Test Report Summary" in output
        assert "Tests" in output and "5" in output
        assert "Failures" in output and "1" in output
        assert "Errors" in output and "0" in output
        assert "Skipped" in output and "0" in output
        assert "Signature: Present" in output or "Signature found" in output

    def test_inspects_from_stdin(self, unsigned_xml: Path) -> None:
        """Test inspection from stdin."""
        xml_content = unsigned_xml.read_text()
        mock_stdin = StringIO(xml_content)
        captured_stdout = StringIO()

        with (
            patch.object(sys, "argv", ["jux-inspect"]),
            patch("sys.stdin", mock_stdin),
            patch("sys.stdout", captured_stdout),
        ):
            exit_code = main()

        assert exit_code == 0
        output = _plain(captured_stdout.getvalue())
        assert "Test Report Summary" in output
        assert "Tests" in output and "10" in output

    def test_json_output(self, unsigned_xml: Path) -> None:
        """Test JSON output format."""
        captured_stdout = StringIO()

        with (
            patch.object(
                sys, "argv", ["jux-inspect", "-i", str(unsigned_xml), "--json"]
            ),
            patch("sys.stdout", captured_stdout),
        ):
            exit_code = main()

        assert exit_code == 0
        output = _plain(captured_stdout.getvalue())
        assert '"tests": 10' in output
        assert '"failures": 2' in output
        assert '"errors": 1' in output
        assert '"skipped": 1' in output
        assert '"signed": false' in output

    def test_json_output_signed(self, signed_xml: Path) -> None:
        """Test JSON output for signed XML."""
        captured_stdout = StringIO()

        with (
            patch.object(sys, "argv", ["jux-inspect", "-i", str(signed_xml), "--json"]),
            patch("sys.stdout", captured_stdout),
        ):
            exit_code = main()

        assert exit_code == 0
        output = _plain(captured_stdout.getvalue())
        assert '"tests": 5' in output
        assert '"failures": 1' in output
        assert '"signed": true' in output

    def test_shows_canonical_hash(self, unsigned_xml: Path) -> None:
        """Test display of canonical hash."""
        captured_stdout = StringIO()

        with (
            patch.object(sys, "argv", ["jux-inspect", "-i", str(unsigned_xml)]),
            patch("sys.stdout", captured_stdout),
        ):
            exit_code = main()

        assert exit_code == 0
        output = _plain(captured_stdout.getvalue())
        # SHA-256 hash should be 64 hex characters
        assert "Canonical Hash" in output or "SHA-256" in output

    def test_fails_for_missing_input_file(self) -> None:
        """Test error handling for missing input file."""
        captured_stderr = StringIO()

        with (
            patch.object(sys, "argv", ["jux-inspect", "-i", "/nonexistent.xml"]),
            patch("sys.stderr", captured_stderr),
        ):
            exit_code = main()

        assert exit_code == 1

    def test_handles_multiple_test_suites(self, tmp_path: Path) -> None:
        """Test handling of XML with multiple test suites."""
        xml_content = """<?xml version="1.0"?>
<testsuites>
    <testsuite name="suite1" tests="3" failures="1" errors="0" skipped="0">
        <testcase name="test1" time="0.1"/>
        <testcase name="test2" time="0.2">
            <failure>Failed</failure>
        </testcase>
    </testsuite>
    <testsuite name="suite2" tests="2" failures="0" errors="1" skipped="1">
        <testcase name="test3" time="0.1">
            <error>Error</error>
        </testcase>
        <testcase name="test4" time="0.0">
            <skipped>Skipped</skipped>
        </testcase>
    </testsuite>
</testsuites>
"""
        xml_path = tmp_path / "multi.xml"
        xml_path.write_text(xml_content)

        captured_stdout = StringIO()

        with (
            patch.object(sys, "argv", ["jux-inspect", "-i", str(xml_path)]),
            patch("sys.stdout", captured_stdout),
        ):
            exit_code = main()

        assert exit_code == 0
        output = _plain(captured_stdout.getvalue())
        # Should aggregate across all suites
        assert "Tests" in output and "5" in output
        assert "Failures" in output and "1" in output
        assert "Errors" in output and "1" in output
        assert "Skipped" in output and "1" in output

    def test_handles_empty_test_suite(self, tmp_path: Path) -> None:
        """Test handling of empty test suite."""
        xml_content = """<?xml version="1.0"?>
<testsuites>
    <testsuite name="empty" tests="0" failures="0" errors="0" skipped="0"/>
</testsuites>
"""
        xml_path = tmp_path / "empty.xml"
        xml_path.write_text(xml_content)

        captured_stdout = StringIO()

        with (
            patch.object(sys, "argv", ["jux-inspect", "-i", str(xml_path)]),
            patch("sys.stdout", captured_stdout),
        ):
            exit_code = main()

        assert exit_code == 0
        output = _plain(captured_stdout.getvalue())
        assert "Tests" in output and "0" in output

    def test_generic_exception_with_json(self, unsigned_xml: Path) -> None:
        """Test generic exception handling with JSON output."""
        captured_stdout = StringIO()

        # Mock load_xml to raise generic exception
        with (
            patch.object(
                sys, "argv", ["jux-inspect", "-i", str(unsigned_xml), "--json"]
            ),
            patch("sys.stdout", captured_stdout),
            patch(
                "pytest_jux.commands.inspect.load_xml",
                side_effect=RuntimeError("Unexpected error"),
            ),
        ):
            exit_code = main()

        assert exit_code == 1
        output = _plain(captured_stdout.getvalue())
        assert "error" in output.lower()
        assert "unexpected error" in output.lower()

    def test_generic_exception_normal_output(self, unsigned_xml: Path) -> None:
        """Test generic exception handling with normal output."""
        captured_stderr = StringIO()

        # Mock load_xml to raise generic exception
        with (
            patch.object(sys, "argv", ["jux-inspect", "-i", str(unsigned_xml)]),
            patch("sys.stderr", captured_stderr),
            patch(
                "pytest_jux.commands.inspect.load_xml",
                side_effect=RuntimeError("Unexpected error"),
            ),
        ):
            exit_code = main()

        assert exit_code == 1
        output = captured_stderr.getvalue()
        assert "Error:" in output
        assert "Unexpected error" in output
