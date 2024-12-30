#src/pages/projects/conftest.py

import pytest
from pages.projects.basepage import BasePage
from util_tools.check_whiteout import load_whiteout_texts

@pytest.fixture
def base_page(request):
    """BasePage 객체 생성"""
    # request.cls.whiteout_texts를 사용하여 BasePage 생성
    whiteout_texts = getattr(request.cls, "whiteout_texts", [])
    return BasePage(request.cls.page, whiteout_texts)

@pytest.fixture
def resource_board_page(base_page):
    """ResourceBoardPage 객체 생성"""
    return ResourceBoardPage(base_page.page, base_page.whiteout_texts)
