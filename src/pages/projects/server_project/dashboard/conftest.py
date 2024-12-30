import pytest
from pages.projects.server_project.dashboard.resourceboardpage import ResourceBoardPage

@pytest.fixture
def resource_board_page(base_page):
    """ResourceBoardPage 객체 생성"""
    return ResourceBoardPage(base_page.page)
