from collections import OrderedDict
from models import models

def filter_results():
    results = models.Result.select().where(
        (models.Result.level == 'state') | (models.Result.level == None)
    )

    return results

def group_results_by_race(results):
    grouped = OrderedDict()
    for result in results:
        if result.raceid not in grouped:
            grouped[result.raceid] = []

        grouped[result.raceid].append(result)

    return grouped