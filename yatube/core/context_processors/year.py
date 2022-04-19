import datetime as dt


def year(request):
    """Adds a variable with the current year."""
    year = dt.datetime.now().year
    return {'year': year}
