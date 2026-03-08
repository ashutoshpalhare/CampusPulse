#!/usr/bin/env python
import os
import sys
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
# helper: small utility for StudentManagement System
def _placeholder_util():
    return True

def get_status():
    """Return simple status dict."""
    return {"ok": True, "service": "StudentManagement System"}
