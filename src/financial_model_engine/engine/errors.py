class ModelIntegrityError(Exception):
    def __init__(self, failed_check_ids: list[str]):
        self.failed_check_ids = failed_check_ids
        super().__init__(f"failed model checks: {failed_check_ids}")
