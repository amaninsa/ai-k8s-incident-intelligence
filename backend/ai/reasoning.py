"""Legacy placeholder — use root_cause_analyzer.analyze_root_cause instead."""

from ai.root_cause_analyzer import analyze_root_cause

__all__ = ["analyze_root_cause"]


def analyze_cluster():
    pass


def generate_diagnosis(investigation):
    return analyze_root_cause(investigation)
