from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str

    USE_REF: bool = True
    REF_ID: str = 'ref_7270017507'

    ENABLE_AUTO_TASKS: bool = True
    ENABLE_AUTO_PLAY_GAMES: bool = True
    MAX_GAME_POINTS: int = 200

    USE_RANDOM_DELAY_IN_RUN: bool = True
    RANDOM_DELAY_IN_RUN: list[int] = [5, 60]

    RANDOM_DELAY_BETWEEN_CYCLES: list[int] = [20, 40, 60, 80]

    BLACK_LIST_TASKS: list[str] = []

    USE_PROXY_FROM_FILE: bool = True


settings = Settings()


