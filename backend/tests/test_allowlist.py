import pytest
from app.config import is_host_allowed

def test_valid_allowlisted_hosts():
    assert is_host_allowed("https://www.reuters.com/markets/middle-east") is True
    assert is_host_allowed("http://reuters.com") is True
    assert is_host_allowed("https://english.mubasher.info/countries/eg") is True
    assert is_host_allowed("https://enterprise.press/feed/") is True
    assert is_host_allowed("https://alborsaanews.com/article/123") is True
    assert is_host_allowed("https://www.egx.com.eg/en/Disclosure_Reports.aspx") is True
    assert is_host_allowed("https://fra.gov.eg") is True

def test_spoofed_or_disallowed_hosts_rejected():
    assert is_host_allowed("https://notreuters.com/fake") is False
    assert is_host_allowed("https://reuters.com.attacker.com") is False
    assert is_host_allowed("https://mubasher.fake.net") is False
    assert is_host_allowed("https://random-financial-blog.xyz") is False
    assert is_host_allowed("") is False
    assert is_host_allowed(None) is False
