from familyhistory import __version__


def app_version(request):
    return {"APP_VERSION": __version__}
