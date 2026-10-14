"""Page Objects (Page Object Model): mỗi trang một lớp, chứa locator + thao tác, KHÔNG chứa assertion."""
from .base_page import BasePage
from .login_page import LoginPage
from .search_page import SearchPage

__all__ = ["BasePage", "LoginPage", "SearchPage"]
