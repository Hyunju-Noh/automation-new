#src/pages/projects/conftest.py

import pytest
from pages.projects.basepage import BasePage
from util_tools.check_whiteout import load_whiteout_texts

#@pytest.fixture
#def base_page(request):
#    """BasePage 객체 생성"""
#    # request.cls.whiteout_texts를 사용하여 BasePage 생성
#    whiteout_texts = getattr(request.cls, "whiteout_texts", [])
#    return BasePage(request.cls.page, whiteout_texts)

#@pytest.fixture
#def resource_board_page(base_page):
#    """ResourceBoardPage 객체 생성"""
#    return ResourceBoardPage(base_page.page, base_page.whiteout_texts)

@pytest.fixture
def base_page(request):
    """BasePage 객체 생성"""
    # request.cls.whiteout_texts와 save_path를 사용하여 BasePage 생성
    whiteout_texts = getattr(request.cls, "whiteout_texts", [])
    save_path = getattr(request.cls, "save_path", None)  # save_path를 테스트 클래스에서 가져옴
    if save_path is None:
        raise AttributeError("save_path 속성이 설정되지 않았습니다. setup_playwright_context에서 설정이 필요합니다.")
    return BasePage(request.cls.page, whiteout_texts, save_path)

@pytest.fixture
def resource_board_page(base_page):
    """ResourceBoardPage 객체 생성"""
    return ResourceBoardPage(base_page.page, base_page.whiteout_texts, base_page.save_path)