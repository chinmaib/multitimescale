import json
from typing import List

from tomcat_viz.Common.Constants import Constants


class TimeSeries:
    def __init__(self, name: str, values: List[List[float]], labels: List[str] = None):
        assert labels is None or len(labels) == len(values)

        self.name = name
        self.values = values
        self.cardinality = len(values)
        self.size = len(values[0]) if self.cardinality > 0 else 0
        self.labels = [str(i) for i in range(self.cardinality)] if labels is None else labels


class Estimates:
    def __init__(self, filepath: str):
        self._parse(filepath)

    def _parse(self, filepath: str):
        with open(filepath, "r") as f:
            jsonOutput = json.load(f)

            self.playerSeries: List[List[TimeSeries]] = [[] for _ in range(Constants.NUM_ROLES)]
            self.teamSeries = []

            for estimator in jsonOutput["estimation"]["agent"]["estimators"]:
                # If there are multiple executions in the file, we only get the first one. Also, if there are estimates
                # for multiple mission trials in the file, we only get the first one. To use with the iMAP, we recommend
                # one trial per file to be consistent with the trial being watched.
                values = []
                for estimates in estimator["executions"][0]["estimates"]:
                    values.append(list(map(float, estimates[:estimates.find("\n")].split())))

                color = estimator["node_label"].split("_")[-1].lower()
                terms = estimator["node_label"].split("_")
                categories = estimator.get("categories", None)
                if color in ["red", "green", "blue"]:
                    # We remove the color identification from the variable name and replace
                    # underscores with blank spaces. This is just for aesthetics because the the variable name will
                    # be used as the title of the plot.
                    variableName = " ".join(terms[:-1])
                    series = TimeSeries(variableName, values, categories)
                    self.playerSeries[Constants.PLAYER_COLOR_MAP[color].value].append(series)
                else:
                    variableName = " ".join(terms)
                    series = TimeSeries(variableName, values, categories)
                    self.teamSeries.append(series)
