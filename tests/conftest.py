"""Test configuration and fixtures for iPXE menu generator tests."""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    tmpdir = tempfile.mkdtemp()
    yield Path(tmpdir)
    shutil.rmtree(tmpdir)


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        'menu': {
            'title': 'Test Menu',
            'default_item': 'test_menu',
            'timeout': 10000
        },
        'distributions': {
            'test_distro': {
                'enabled': True,
                'label': 'Test Distribution',
                'type': 'static',
                'versions': [
                    {'version': '1.0', 'label': 'Test 1.0'},
                    {'version': '2.0', 'label': 'Test 2.0'}
                ],
                'url_template': 'http://example.com/{version}',
                'boot_files': {
                    'kernel': 'vmlinuz',
                    'initrd': 'initrd.img'
                },
                'boot_params': 'test=param'
            }
        },
        'additional_items': [
            {'id': 'shell', 'label': 'Shell', 'type': 'shell'},
            {'id': 'exit', 'label': 'Exit', 'type': 'exit'}
        ]
    }


@pytest.fixture
def minimal_config():
    """Minimal valid configuration."""
    return {
        'menu': {
            'title': 'Minimal Menu',
            'default_item': 'shell',
            'timeout': 5000
        },
        'distributions': {},
        'additional_items': [
            {'id': 'shell', 'label': 'Shell', 'type': 'shell'}
        ]
    }


@pytest.fixture
def fedora_metadata():
    """Sample Fedora releases.json metadata."""
    return [
        {
            'version': '41',
            'variant': 'Server',
            'arch': 'x86_64',
            'link': 'http://example.com/fedora/41'
        },
        {
            'version': '40',
            'variant': 'Server',
            'arch': 'x86_64',
            'link': 'http://example.com/fedora/40'
        },
        {
            'version': '41',
            'variant': 'Workstation',
            'arch': 'x86_64',
            'link': 'http://example.com/fedora/41-workstation'
        }
    ]


@pytest.fixture
def boot_entry_data():
    """Sample boot entry data."""
    return {
        'id': 'test_entry',
        'label': 'Test Entry',
        'kernel_url': 'http://example.com/vmlinuz',
        'initrd_url': 'http://example.com/initrd.img',
        'boot_params': 'test=param'
    }


@pytest.fixture
def distribution_menu_data():
    """Sample distribution menu data."""
    return {
        'id': 'test_menu',
        'label': 'Test Menu',
        'entries': [
            {
                'id': 'entry1',
                'label': 'Entry 1',
                'kernel_url': 'http://example.com/vmlinuz1',
                'initrd_url': 'http://example.com/initrd1.img',
                'boot_params': 'param1'
            },
            {
                'id': 'entry2',
                'label': 'Entry 2',
                'kernel_url': 'http://example.com/vmlinuz2',
                'initrd_url': 'http://example.com/initrd2.gz',
                'boot_params': ''
            }
        ]
    }
