import math

class CentroidTracker:
    def __init__(self, max_distance=80, max_missing=30, history_length=30):
        self.next_id = 0
        self.objects = {}           # {id: (x, y)}
        self.missing = {}           # {id: berapa frame nggak kelihatan}
        self.history = {}                    # ← {id: [(x,y), (x,y), ...]}
        self.max_distance = max_distance
        self.max_missing = max_missing     # toleransi hilang (frame)
        self.history_length = history_length # berapa posisi terakhir disimpan
    def update(self, centroids, heights=None):
        if heights is None:
            heights = [0] * len(centroids)

        # nggak ada deteksi → tambah counter, jangan langsung hapus
        if len(centroids) == 0:
            for obj_id in list(self.objects.keys()):
                self.missing[obj_id] += 1
                if self.missing[obj_id] > self.max_missing:
                    del self.objects[obj_id]
                    del self.missing[obj_id]
            return self.objects

        new_objects = {}
        new_missing = {}
        used_ids = set()

        for i, c in enumerate(centroids):
            best_id = None
            best_dist = self.max_distance

            for obj_id, pos in self.objects.items():
                if obj_id in used_ids:
                    continue
                dist = math.dist(c, pos)
                if dist < best_dist:
                    best_dist = dist
                    best_id = obj_id

            if best_id is not None:                    # orang lama
                new_objects[best_id] = c
                new_missing[best_id] = 0
                used_ids.add(best_id)
                self._record(best_id, c, heights[i])
            else:                                      # orang baru
                new_objects[self.next_id] = c
                new_missing[self.next_id] = 0
                self._record(self.next_id, c, heights[i])
                self.next_id += 1

        # pertahankan objek lama yang nggak kecocok frame ini
        for obj_id, pos in self.objects.items():
            if obj_id not in used_ids:
                miss = self.missing.get(obj_id, 0) + 1
                if miss <= self.max_missing:
                    new_objects[obj_id] = pos
                    new_missing[obj_id] = miss

        self.objects = new_objects
        self.missing = new_missing
        return self.objects
    def _record(self, obj_id, centroid, height=0):
        if obj_id not in self.history:
            self.history[obj_id] = []
        self.history[obj_id].append((centroid[0], centroid[1], height))   # (x, y, h)
        if len(self.history[obj_id]) > self.history_length:
            self.history[obj_id].pop(0)