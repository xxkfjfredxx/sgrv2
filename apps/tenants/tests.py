from django.test import TestCase
from .models import Tenant  # Assuming you have a Tenant model defined in models.py

class TenantModelTests(TestCase):
    def setUp(self):
        # Create a tenant instance for testing
        self.tenant = Tenant.objects.create(name="Test Tenant", is_active=True)

    def test_tenant_creation(self):
        self.assertEqual(self.tenant.name, "Test Tenant")
        self.assertTrue(self.tenant.is_active)

    def test_tenant_inactive(self):
        self.tenant.is_active = False
        self.tenant.save()
        self.assertFalse(self.tenant.is_active)