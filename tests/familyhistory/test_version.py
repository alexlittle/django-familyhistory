import importlib
from importlib.metadata import PackageNotFoundError
from unittest.mock import patch

import familyhistory


def test_version_fallback():
    # Patch the source (importlib.metadata.version), not familyhistory.version:
    # reload() re-runs `from importlib.metadata import version`, which would
    # overwrite a patch applied to the familyhistory namespace.
    try:
        with patch(
            "importlib.metadata.version",
            side_effect=PackageNotFoundError("familyhistory"),
        ):
            importlib.reload(familyhistory)
            assert familyhistory.__version__ == "dev"
    finally:
        # restore the real value so other tests aren't affected
        importlib.reload(familyhistory)
