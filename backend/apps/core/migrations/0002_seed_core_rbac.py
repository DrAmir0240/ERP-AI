from django.db import migrations


MODULES = [
    ("core", "Core"),
    ("inventory", "Inventory"),
    ("accounts", "Accounts"),
    ("orders", "Orders"),
    ("repair", "Repair"),
    ("procurement", "Procurement"),
    ("accounting", "Accounting"),
    ("hr", "HR"),
    ("tasks", "Tasks"),
    ("crm", "CRM"),
    ("notifications", "Notifications"),
    ("ecommerce", "E-commerce"),
    ("documents", "Documents"),
]

ROLES = [
    ("admin", "Admin"),
    ("cashier", "Cashier"),
    ("account_setter", "Account Setter"),
    ("accountant", "Accountant"),
    ("warehouse", "Warehouse"),
    ("customer", "Customer"),
    ("b2b_customer", "B2B Customer"),
    ("repair_technician", "Repair Technician"),
]


def seed_core_rbac(apps, schema_editor):
    Module = apps.get_model("core", "Module")
    Role = apps.get_model("core", "Role")
    Permission = apps.get_model("core", "Permission")
    modules = {}
    for name, display_name in MODULES:
        module, _ = Module.objects.get_or_create(name=name, defaults={"display_name": display_name})
        modules[name] = module
    for name, display_name in ROLES:
        role, _ = Role.objects.get_or_create(name=name, defaults={"display_name": display_name, "is_default": True})
        for module in modules.values():
            Permission.objects.get_or_create(
                role=role,
                module=module,
                defaults={"can_read": name == "admin", "can_write": name == "admin"},
            )


def unseed_core_rbac(apps, schema_editor):
    Role = apps.get_model("core", "Role")
    Module = apps.get_model("core", "Module")
    Role.objects.filter(name__in=[name for name, _display_name in ROLES]).delete()
    Module.objects.filter(name__in=[name for name, _display_name in MODULES]).delete()


class Migration(migrations.Migration):
    dependencies = [("core", "0001_initial")]
    operations = [migrations.RunPython(seed_core_rbac, unseed_core_rbac)]
