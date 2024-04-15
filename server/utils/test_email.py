import unittest

from . import email as e


class NormalizeEmailTestCase(unittest.TestCase):
    """Test the normalize_email function."""

    def test_simple(self):
        """Test a simple email address."""
        email = "test@example.com"
        expected = "test@example.com"
        result = e.normalize_email(email)
        self.assertEqual(result, expected)

    def test_whitespace(self):
        """Test an email address with whitespace."""
        email = " test@example.com\t"
        expected = "test@example.com"
        result = e.normalize_email(email)
        self.assertEqual(result, expected)

    def test_lowercase(self):
        """Test an email address with uppercase characters."""
        email = "tEst@Example.com"
        expected = "test@example.com"
        result = e.normalize_email(email)
        self.assertEqual(result, expected)

    def test_tag(self):
        """Test an email address with a tag."""
        email = "test+tag@example.com"
        expected = "test@example.com"
        result = e.normalize_email(email)
        self.assertEqual(result, expected)

    def test_custom_tag(self):
        """Test an email address with a custom tag."""
        email = "test-tag@example.com"
        expected = "test@example.com"
        result = e.normalize_email(email, tag="-")
        self.assertEqual(result, expected)

    def test_no_tag(self):
        """Test an email address with no tag separation."""
        email = "test+tag@example.com"
        expected = "test+tag@example.com"
        result = e.normalize_email(email, tag=None)
        self.assertEqual(result, expected)

    def test_dots(self):
        """Test an email address with dots."""
        email = "test.test@example.com"
        expected = "testtest@example.com"
        result = e.normalize_email(email)
        self.assertEqual(result, expected)

    def test_no_dots(self):
        """Test an email address with no dot elimination."""
        email = "test.test@example.com"
        expected = "test.test@example.com"
        result = e.normalize_email(email, dots=False)
        self.assertEqual(result, expected)

    def test_domain_aliases(self):
        """Test an email address with domain aliases."""
        email = "test@alias.example.com"
        expected = "test@example.com"
        domains = e.Domains("example.com", ("alias.example.com",))
        result = e.normalize_email(email, domains=domains)
        self.assertEqual(result, expected)

    def test_force_ascii(self):
        """Test an email address with non-ASCII characters."""
        # This is pretty absurd behavior, but it's fine for now.
        email = "tést@éxample.com"
        expected = "tst@xample.com"
        result = e.normalize_email(email)
        self.assertEqual(result, expected)
