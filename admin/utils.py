from collections import OrderedDict
from models import models

def filter_results():
    results = models.Result.select().where(
        (models.Result.level == 'state') | (models.Result.level == None)
    ).order_by(models.Result.statepostal, models.Result.party, models.Result.last)

    return results

def group_results_by_race(results):
    grouped = OrderedDict()
    for result in results:
        if result.raceid not in grouped:
            grouped[result.raceid] = []

        grouped[result.raceid].append(result)

    return grouped