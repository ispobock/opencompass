from mmengine.config import read_base

with read_base():
    from .CLUE_cmnli_ppl_1c652a import cmnli_datasets  # noqa: F401, F403
