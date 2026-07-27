import re
from typing import Any
from typing import Final

NO_SKIP_OPTION: Final[str] = '--no-skip'
TEST_ORDER_PATTERN = re.compile(r'^test_(\d+)_')

def pytest_addoption(parser):
    parser.addoption(NO_SKIP_OPTION, action='store_true', default=False, help='also run skipped tests')

def pytest_collection_modifyitems(config,
                                  items: list[Any]):
    def item_order(item: Any) -> tuple[int, str]:
        match = TEST_ORDER_PATTERN.match(item.path.name)
        return (int(match.group(1)) if match else 1_000_000, str(item.path))

    items.sort(key=item_order)
    if config.getoption(NO_SKIP_OPTION):
        for test in items:
            test.own_markers = [marker for marker in test.own_markers if marker.name not in ('skip', 'skipif')]
