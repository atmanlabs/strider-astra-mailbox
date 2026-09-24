"""Compatibility entry point: every word-game turn now uses live chat."""
import runpy
runpy.run_module("live_game", run_name="__main__")
