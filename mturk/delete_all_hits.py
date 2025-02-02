from mturk_base import MTurkBase

base_cls = MTurkBase(stage="sandbox")
deleted_hit_ids = base_cls._delete_all_hits()
print(deleted_hit_ids)
