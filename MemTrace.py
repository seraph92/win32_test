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
        self.top_stats: list[StatisticDiff] = self.snapshots[-1].compare_to(
            self.snapshots[0], "lineno"
        )

    def print_mem_trace(self):
        traces = tracemalloc.take_snapshot().statistics("traceback")
        for stat in traces[:1]:
            print(
                f"memory_blocks=[{stat.count}] size_kB=[{stat.size/1024}]", flush=True
            )
            for line in stat.traceback.format():
                print(line, flush=True)

    def print_init_stat(self, top: int = 5):
        for idx, stat in enumerate(self.snapshots[0].statistics("lineno")[:top], 1):
            print(str(stat), flush=True)

    def print_stat(self, top: int = 10):
        print("[ Top {10} ]")
        for stat in self.top_stats[:top]:
            print(stat)

    def end_print(self, top: int = 10):
        self.end()
        self.print_stat(top)

    def __del__(self):
        for s in self.snapshots:
            del s
