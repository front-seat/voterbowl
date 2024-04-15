import unittest

from django.core.exceptions import ValidationError

from .models import School


class SchoolTestCase(unittest.TestCase):
    """Test the school model."""

    def test_str(self):
        """Test the school model's string representation."""
        school = School(name="Test School")
        expected = "School: Test School"
        result = str(school)
        self.assertEqual(result, expected)

    def test_is_valid_email_true(self):
        """Test a valid email address."""
        school = School(mail_domains=["example.com"])
        email = "test@example.com"
        result = school.is_valid_email(email)
        self.assertTrue(result)

    def test_is_valid_email_false(self):
        """Test an invalid email address."""
        school = School(mail_domains=["example.com"])
        email = "test@nope.com"
        result = school.is_valid_email(email)
        self.assertFalse(result)

    def test_is_valid_email_alias_true(self):
        """Test a valid email address with an alias."""
        school = School(mail_domains=["example.com", "alias.example.com"])
        email = "test@alias.example.com"
        result = school.is_valid_email(email)
        self.assertTrue(result)

    def test_validate_email_valid(self):
        """Test a valid email address."""
        school = School(mail_domains=["example.com"])
        email = "test@example.com"
        school.validate_email(email)
        self.assertTrue(True)

    def test_validate_email_invalid(self):
        """Test an invalid email address."""
        school = School(mail_domains=["example.com"])
        email = "test@nope.com"
        with self.assertRaises(ValidationError):
            school.validate_email(email)

    def test_hash_email(self):
        """Test hashing an email address."""
        school = School(mail_domains=["example.com", "alias.example.com"])
        emails = [
            "test@example.com",
            "test+tag@example.com",
            "te.st@example.com",
            "test@alias.example.com",
            "te.st+tag@alias.example.com",
        ]
        hashed = [school.hash_email(email) for email in emails]
        self.assertEqual(len(set(hashed)), 1)

    def test_no_tag(self):
        """Test an email address with no tag separation."""
        school = School(mail_domains=["example.com"], mail_tag="")
        email = "test+tag@example.com"
        expected = "test+tag@example.com"
        result = school.normalize_email(email)
        self.assertEqual(result, expected)

    def test_no_dots(self):
        """Test an email address with no dot elimination."""
        school = School(mail_domains=["example.com"], mail_dots=False)
        email = "test.test@example.com"
        expected = "test.test@example.com"
        result = school.normalize_email(email)
        self.assertEqual(result, expected)
