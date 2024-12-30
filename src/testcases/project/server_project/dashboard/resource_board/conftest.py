import pytest
import util_tools.logging as log_utils
from pages.projects.conftest import base_page
from pages.projects.server_project.dashboard.resourceboardpage import ResourceBoardPage

@pytest.fixture(scope="session", autouse=True)
def setup_logging_once():
    """ResourceBoardPage 전용 로그 설정"""
    log_utils.setup_logging_resourceboardpage()

@pytest.fixture
def resource_board_page(base_page):
    """ResourceBoardPage 객체 생성"""
    return ResourceBoardPage(base_page.page, base_page.whiteout_texts)
