# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for jux-sign command."""

from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest
from lxml import etree

from pytest_jux.commands.sign import main


@pytest.fixture
def test_xml(tmp_path: Path) -> Path:
    """Create a test JUnit XML file."""
    xml_path = tmp_path / "test.xml"
    xml_content = """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
    <testsuite name="test_suite" tests="1" failures="0" errors="0">
        <testcase classname="test_module" name="test_example" time="0.001"/>
    </testsuite>
</testsuites>
"""
    xml_path.write_text(xml_content)
    return xml_path


@pytest.fixture
def test_key(tmp_path: Path) -> Path:
    """Create a test RSA key."""
    from pytest_jux.commands.keygen import generate_rsa_key, save_key

    key = generate_rsa_key(2048)
    key_path = tmp_path / "test_key.pem"
    save_key(key, key_path)
    return key_path


@pytest.fixture
def test_cert(tmp_path: Path, test_key: Path) -> Path:
    """Create a test certificate."""
    from pytest_jux.commands.keygen import generate_self_signed_cert
    from pytest_jux.signer import load_private_key

    key = load_private_key(test_key)
    cert_path = tmp_path / "test_cert.crt"
    generate_self_signed_cert(key, cert_path)
    return cert_path


class TestSignCommand:
    """Tests for jux-sign command."""

    def test_signs_xml_file(
        self, test_xml: Path, test_key: Path, tmp_path: Path
    ) -> None:
        """Test signing XML file with RSA key."""
        output_path = tmp_path / "signed.xml"

        with patch(
            "sys.argv",
            [
                "jux-sign",
                "--input",
                str(test_xml),
                "--output",
                str(output_path),
                "--key",
                str(test_key),
            ],
        ):
            exit_code = main()

        assert exit_code == 0
        assert output_path.exists()

        # Verify signature is present
        signed_content = output_path.read_text()
        assert "Signature" in signed_content

    def test_signs_with_certificate(
        self, test_xml: Path, test_key: Path, test_cert: Path, tmp_path: Path
    ) -> None:
        """Test signing XML with key and certificate."""
        output_path = tmp_path / "signed.xml"

        with patch(
            "sys.argv",
            [
                "jux-sign",
                "--input",
                str(test_xml),
                "--output",
                str(output_path),
                "--key",
                str(test_key),
                "--cert",
                str(test_cert),
            ],
        ):
            exit_code = main()

        assert exit_code == 0
        signed_content = output_path.read_text()
        assert "Signature" in signed_content
        assert "X509Certificate" in signed_content

    def test_preserves_xml_content(
        self, test_xml: Path, test_key: Path, tmp_path: Path
    ) -> None:
        """Test that signing preserves original XML content."""
        output_path = tmp_path / "signed.xml"

        # Read original testcase name
        original_tree = etree.parse(str(test_xml))
        original_testcase = original_tree.find(".//testcase")
        assert original_testcase is not None
        original_name = original_testcase.get("name")

        with patch(
            "sys.argv",
            [
                "jux-sign",
                "--input",
                str(test_xml),
                "--output",
                str(output_path),
                "--key",
                str(test_key),
            ],
        ):
            main()

        # Verify content preserved
        signed_tree = etree.parse(str(output_path))
        signed_testcase = signed_tree.find(".//testcase")
        assert signed_testcase is not None
        assert signed_testcase.get("name") == original_name

    def test_writes_to_stdout(self, test_xml: Path, test_key: Path) -> None:
        """Test writing signed XML to stdout."""
        from io import BytesIO, TextIOWrapper

        # A real stream, not a Mock: Python 3.14's argparse probes
        # sys.stdout.fileno() to decide on colour output.
        captured_output = BytesIO()
        mock_stdout = TextIOWrapper(captured_output, encoding="utf-8")

        with patch(
            "sys.argv", ["jux-sign", "--input", str(test_xml), "--key", str(test_key)]
        ):
            with patch("sys.stdout", mock_stdout):
                exit_code = main()

        assert exit_code == 0
        output = captured_output.getvalue().decode("utf-8")
        assert "Signature" in output
        assert "<?xml" in output

    def test_reads_from_stdin(
        self, test_xml: Path, test_key: Path, tmp_path: Path
    ) -> None:
        """Test reading XML from stdin."""
        output_path = tmp_path / "signed.xml"
        xml_content = test_xml.read_text()

        with patch(
            "sys.argv",
            ["jux-sign", "--output", str(output_path), "--key", str(test_key)],
        ):
            with patch("sys.stdin", StringIO(xml_content)):
                exit_code = main()

        assert exit_code == 0
        assert output_path.exists()
        signed_content = output_path.read_text()
        assert "Signature" in signed_content

    def test_stdin_to_stdout(self, test_xml: Path, test_key: Path) -> None:
        """Test reading from stdin and writing to stdout (pipeline mode)."""
        from io import BytesIO, TextIOWrapper

        xml_content = test_xml.read_text()
        # A real stream, not a Mock: see test_writes_to_stdout.
        captured_output = BytesIO()
        mock_stdout = TextIOWrapper(captured_output, encoding="utf-8")

        with patch("sys.argv", ["jux-sign", "--key", str(test_key)]):
            with patch("sys.stdin", StringIO(xml_content)):
                with patch("sys.stdout", mock_stdout):
                    exit_code = main()

        assert exit_code == 0
        output = captured_output.getvalue().decode("utf-8")
        assert "Signature" in output

    def test_requires_key_path(self, test_xml: Path) -> None:
        """Test that key path is required."""
        with patch("sys.argv", ["jux-sign", "--input", str(test_xml)]):
            with pytest.raises(SystemExit):
                main()

    def test_validates_key_file_exists(self, test_xml: Path, tmp_path: Path) -> None:
        """Test that key file existence is validated."""
        output_path = tmp_path / "signed.xml"
        nonexistent_key = tmp_path / "nonexistent.pem"

        with patch(
            "sys.argv",
            [
                "jux-sign",
                "--input",
                str(test_xml),
                "--output",
                str(output_path),
                "--key",
                str(nonexistent_key),
            ],
        ):
            exit_code = main()

        assert exit_code != 0  # Should fail

    def test_validates_input_file_exists(self, test_key: Path, tmp_path: Path) -> None:
        """Test that input file existence is validated."""
        output_path = tmp_path / "signed.xml"
        nonexistent_xml = tmp_path / "nonexistent.xml"

        with patch(
            "sys.argv",
            [
                "jux-sign",
                "--input",
                str(nonexistent_xml),
                "--output",
                str(output_path),
                "--key",
                str(test_key),
            ],
        ):
            exit_code = main()

        assert exit_code != 0

    def test_handles_invalid_xml(self, test_key: Path, tmp_path: Path) -> None:
        """Test handling of invalid XML input."""
        invalid_xml = tmp_path / "invalid.xml"
        invalid_xml.write_text("not valid xml content")
        output_path = tmp_path / "signed.xml"

        with patch(
            "sys.argv",
            [
                "jux-sign",
                "--input",
                str(invalid_xml),
                "--output",
                str(output_path),
                "--key",
                str(test_key),
            ],
        ):
            exit_code = main()

        assert exit_code != 0

    def test_handles_invalid_key(self, test_xml: Path, tmp_path: Path) -> None:
        """Test handling of invalid key file."""
        invalid_key = tmp_path / "invalid_key.pem"
        invalid_key.write_text("not a valid key")
        output_path = tmp_path / "signed.xml"

        with patch(
            "sys.argv",
            [
                "jux-sign",
                "--input",
                str(test_xml),
                "--output",
                str(output_path),
                "--key",
                str(invalid_key),
            ],
        ):
            exit_code = main()

        assert exit_code != 0

    def test_displays_help_text(self) -> None:
        """Test that help text is displayed."""
        with patch("sys.argv", ["jux-sign", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_supports_config_file(
        self, test_xml: Path, test_key: Path, tmp_path: Path
    ) -> None:
        """Test that config file is supported."""
        config_path = tmp_path / "jux.conf"
        config_path.write_text(f"key={test_key}\n")
        output_path = tmp_path / "signed.xml"

        with patch(
            "sys.argv",
            [
                "jux-sign",
                "--config",
                str(config_path),
                "--input",
                str(test_xml),
                "--output",
                str(output_path),
            ],
        ):
            exit_code = main()

        assert exit_code == 0
        assert output_path.exists()

    def test_overwrites_existing_output(
        self, test_xml: Path, test_key: Path, tmp_path: Path
    ) -> None:
        """Test that existing output file is overwritten."""
        output_path = tmp_path / "signed.xml"
        output_path.write_text("existing content")

        with patch(
            "sys.argv",
            [
                "jux-sign",
                "--input",
                str(test_xml),
                "--output",
                str(output_path),
                "--key",
                str(test_key),
            ],
        ):
            exit_code = main()

        assert exit_code == 0
        signed_content = output_path.read_text()
        assert "existing content" not in signed_content
        assert "Signature" in signed_content


class TestSigningWithECDSA:
    """Tests for signing with ECDSA keys."""

    @pytest.fixture
    def ecdsa_key(self, tmp_path: Path) -> Path:
        """Create a test ECDSA key."""
        from pytest_jux.commands.keygen import generate_ecdsa_key, save_key

        key = generate_ecdsa_key("P-256")
        key_path = tmp_path / "ecdsa_key.pem"
        save_key(key, key_path)
        return key_path

    def test_signs_with_ecdsa_key(
        self, test_xml: Path, ecdsa_key: Path, tmp_path: Path
    ) -> None:
        """Test signing with ECDSA key."""
        output_path = tmp_path / "signed.xml"

        with patch(
            "sys.argv",
            [
                "jux-sign",
                "--input",
                str(test_xml),
                "--output",
                str(output_path),
                "--key",
                str(ecdsa_key),
            ],
        ):
            exit_code = main()

        assert exit_code == 0
        signed_content = output_path.read_text()
        assert "Signature" in signed_content


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_handles_large_xml_file(self, test_key: Path, tmp_path: Path) -> None:
        """Test handling of large XML file."""
        large_xml = tmp_path / "large.xml"

        # Generate large XML with many test cases
        testcases = "\n".join(
            [
                f'<testcase classname="test_module" name="test_{i}" time="0.001"/>'
                for i in range(1000)
            ]
        )
        xml_content = f"""<?xml version="1.0" encoding="utf-8"?>
<testsuites>
    <testsuite name="test_suite" tests="1000" failures="0" errors="0">
        {testcases}
    </testsuite>
</testsuites>
"""
        large_xml.write_text(xml_content)
        output_path = tmp_path / "signed.xml"

        with patch(
            "sys.argv",
            [
                "jux-sign",
                "--input",
                str(large_xml),
                "--output",
                str(output_path),
                "--key",
                str(test_key),
            ],
        ):
            exit_code = main()

        assert exit_code == 0
        assert output_path.exists()

    def test_handles_xml_with_namespaces(self, test_key: Path, tmp_path: Path) -> None:
        """Test handling of XML with namespaces."""
        namespaced_xml = tmp_path / "namespaced.xml"
        xml_content = """<?xml version="1.0" encoding="utf-8"?>
<testsuites xmlns="http://junit.org/junit">
    <testsuite name="test_suite" tests="1">
        <testcase classname="test_module" name="test_example"/>
    </testsuite>
</testsuites>
"""
        namespaced_xml.write_text(xml_content)
        output_path = tmp_path / "signed.xml"

        with patch(
            "sys.argv",
            [
                "jux-sign",
                "--input",
                str(namespaced_xml),
                "--output",
                str(output_path),
                "--key",
                str(test_key),
            ],
        ):
            exit_code = main()

        assert exit_code == 0

    def test_handles_permission_error(
        self, test_xml: Path, test_key: Path, tmp_path: Path
    ) -> None:
        """Test handling of permission errors."""
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)
        output_path = readonly_dir / "signed.xml"

        with patch(
            "sys.argv",
            [
                "jux-sign",
                "--input",
                str(test_xml),
                "--output",
                str(output_path),
                "--key",
                str(test_key),
            ],
        ):
            exit_code = main()

        assert exit_code != 0
