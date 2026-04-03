"""Tests for core.validators field-validation utilities."""

from core.validators import (
    validate_bundle_id,
    validate_company_name,
    validate_manufacturer_code,
    validate_output_directory,
    validate_plugin_code,
    validate_product_name,
    validate_project_name,
    validate_version,
)


class TestValidateProjectName:
    def test_valid_simple_name(self):
        valid, msg = validate_project_name("MyPlugin")
        assert valid
        assert msg == ""

    def test_valid_name_with_numbers(self):
        valid, _ = validate_project_name("Plugin2025")
        assert valid

    def test_valid_name_with_hyphen(self):
        valid, _ = validate_project_name("my-plugin")
        assert valid

    def test_valid_name_with_underscore(self):
        valid, _ = validate_project_name("my_plugin")
        assert valid

    def test_empty_name_is_invalid(self):
        valid, msg = validate_project_name("")
        assert not valid
        assert msg

    def test_whitespace_only_is_invalid(self):
        valid, _ = validate_project_name("   ")
        assert not valid

    def test_name_with_space_is_invalid(self):
        valid, msg = validate_project_name("My Plugin")
        assert not valid
        assert "space" in msg.lower()

    def test_name_with_special_chars_is_invalid(self):
        valid, _ = validate_project_name("my@plugin!")
        assert not valid


class TestValidateProductName:
    def test_non_empty_name_is_valid(self):
        valid, msg = validate_product_name("My Awesome Plugin")
        assert valid
        assert msg == ""

    def test_empty_name_is_invalid(self):
        valid, msg = validate_product_name("")
        assert not valid
        assert msg

    def test_whitespace_only_is_invalid(self):
        valid, _ = validate_product_name("   ")
        assert not valid


class TestValidateCompanyName:
    def test_non_empty_name_is_valid(self):
        valid, msg = validate_company_name("DirektDSP")
        assert valid
        assert msg == ""

    def test_empty_name_is_invalid(self):
        valid, _ = validate_company_name("")
        assert not valid

    def test_whitespace_only_is_invalid(self):
        valid, _ = validate_company_name("   ")
        assert not valid


class TestValidateBundleId:
    def test_valid_three_segment_id(self):
        valid, msg = validate_bundle_id("com.company.plugin")
        assert valid
        assert msg == ""

    def test_valid_with_numbers(self):
        valid, _ = validate_bundle_id("com.company2.plugin1")
        assert valid

    def test_valid_with_hyphen(self):
        valid, _ = validate_bundle_id("com.my-company.my-plugin")
        assert valid

    def test_valid_four_segments(self):
        valid, _ = validate_bundle_id("com.company.suite.plugin")
        assert valid

    def test_empty_is_invalid(self):
        valid, msg = validate_bundle_id("")
        assert not valid
        assert msg

    def test_two_segments_is_invalid(self):
        valid, _ = validate_bundle_id("com.plugin")
        assert not valid

    def test_starts_with_digit_is_invalid(self):
        valid, _ = validate_bundle_id("1com.company.plugin")
        assert not valid

    def test_segment_starting_with_digit_is_invalid(self):
        valid, _ = validate_bundle_id("com.1company.plugin")
        assert not valid

    def test_spaces_in_id_is_invalid(self):
        valid, _ = validate_bundle_id("com.my company.plugin")
        assert not valid


class TestValidateManufacturerCode:
    def test_valid_four_char_code(self):
        valid, msg = validate_manufacturer_code("Ddsp")
        assert valid
        assert msg == ""

    def test_valid_all_caps(self):
        valid, _ = validate_manufacturer_code("ABCD")
        assert valid

    def test_empty_is_invalid(self):
        valid, _ = validate_manufacturer_code("")
        assert not valid

    def test_three_chars_is_invalid(self):
        valid, msg = validate_manufacturer_code("Abc")
        assert not valid
        assert "4" in msg

    def test_five_chars_is_invalid(self):
        valid, msg = validate_manufacturer_code("Abcde")
        assert not valid
        assert "4" in msg


class TestValidatePluginCode:
    def test_empty_is_valid(self):
        """Empty plugin code is acceptable - will be auto-generated."""
        valid, msg = validate_plugin_code("")
        assert valid
        assert msg == ""

    def test_valid_four_char_code_starting_uppercase(self):
        valid, _ = validate_plugin_code("Abcd")
        assert valid

    def test_valid_one_char_uppercase(self):
        valid, _ = validate_plugin_code("A")
        assert valid

    def test_starts_with_lowercase_is_invalid(self):
        valid, msg = validate_plugin_code("abcd")
        assert not valid
        assert "capital" in msg.lower()

    def test_five_chars_is_invalid(self):
        valid, msg = validate_plugin_code("Abcde")
        assert not valid
        assert "4" in msg


class TestValidateVersion:
    def test_valid_version(self):
        valid, msg = validate_version("1.0.0")
        assert valid
        assert msg == ""

    def test_valid_multi_digit(self):
        valid, _ = validate_version("10.20.30")
        assert valid

    def test_empty_is_invalid(self):
        valid, _ = validate_version("")
        assert not valid

    def test_two_part_version_is_invalid(self):
        valid, _ = validate_version("1.0")
        assert not valid

    def test_letters_in_version_is_invalid(self):
        valid, _ = validate_version("1.0.0-alpha")
        assert not valid

    def test_version_with_leading_v_is_invalid(self):
        valid, _ = validate_version("v1.0.0")
        assert not valid


class TestValidateOutputDirectory:
    def test_non_empty_path_is_valid(self):
        valid, msg = validate_output_directory("/home/user/projects")
        assert valid
        assert msg == ""

    def test_empty_path_is_invalid(self):
        valid, _ = validate_output_directory("")
        assert not valid

    def test_whitespace_only_is_invalid(self):
        valid, _ = validate_output_directory("   ")
        assert not valid
