from tracemalloc import Snapshot, StatisticDiff
import tracemalloc
import typing

class MemTrace:
    def __init__(self):
        self.snapshots: list[Snapshot] = []
        tracemalloc.start()
        snap: Snapshot = tracemalloc.take_snapshot()
        self.snapshots.append(snap)

    def end(self):
        snap: Snapshot = tracemalloc.take_snapshot()
        self.snapshots.append(snap)
        self.top_stats: list[StatisticDiff] = self.snapshots[-1].compare_to(self.snapshots[0], 'lineno')

    def print_stat(self):
        print("[ Top 10 ]")
        for stat in self.top_stats[:10]:
            print(stat)

    def end_print(self):
        self.end()
        self.print_stat()

    def __del__(self):
        for s in self.snapshots:
            del s

