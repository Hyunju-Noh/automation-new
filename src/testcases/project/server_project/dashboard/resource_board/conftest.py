# src/testcases/project/server_project/dashboard/resource_board/conftest.py

import pytest
import util_tools.logging as log_utils
from pages.projects.conftest import base_page
from pages.projects.server_project.dashboard.resourceboardpage import ResourceBoardPage

@pytest.fixture(scope="session", autouse=True)
def setup_logging_once():
    """ResourceBoardPage 전용 로그 설정"""
    log_utils.setup_logging_resourceboardpage()

@pytest.fixture
def resource_board_page(base_page, request):
    """ResourceBoardPage 객체 생성"""
    save_path = getattr(request.cls, "save_path", None)
    return ResourceBoardPage(base_page.page, base_page.whiteout_texts, save_path=save_path)
