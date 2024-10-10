class MissingConfigException(Exception):
    def __init__(self, field_name: str):
        super().__init__(f"Missing configuration value for: {field_name}")
