# src/pages/common_page.py
from playwright.sync_api import Page

class Navigation:
    def __init__(self, page):
        self.page = page

    def navigate(self, url):
        """지정된 URL로 이동"""
        self.page.goto(url, timeout=5000)
        self.page.wait_for_load_state('networkidle')
