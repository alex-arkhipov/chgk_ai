#!/usr/bin/env python3

from __future__ import annotations
import asyncio
import pathlib
from yandex_cloud_ml_sdk import AsyncYCloudML
from yandex_cloud_ml_sdk.auth import YandexCloudCLIAuth


def local_path(path: str) -> pathlib.Path:
    return pathlib.Path(__file__).parent / path


async def main() -> None:

    sdk = AsyncYCloudML(
        folder_id="b1gi8t3st6d9elkg5aqp",
        auth="aje1paj5o9d7n1poqf4l",
    )

    # Создаем датасет для дообучения базовой модели YandexGPT Lite
    dataset_draft = sdk.datasets.draft_from_path(
        task_type="TextToTextGeneration",
        path="<путь_к_файлу>",
        upload_format="jsonlines",
        name="YandexGPT tuning",
    )

    # Дождемся окончания загрузки данных и создания датасета
    operation = await dataset_draft.upload_deferred()
    dataset = await operation
    print(f"new {dataset=}")


if __name__ == "__main__":
    asyncio.run(main=main())
