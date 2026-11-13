from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("familyhistory")
except PackageNotFoundError:  # not installed (e.g. plain checkout)
    __version__ = "dev"
