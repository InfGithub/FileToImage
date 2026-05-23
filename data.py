from typing import Literal #, TypedDict

icon_b64: str = (
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAAACXBIWXMAAABHAAAARAAbKp"
    "bnAAADG0lEQVR4nAEQA+/8AOCoccyUXd+pf8mTaYyEgY+HhIq813qsx6LDyrrb4tmlf7+LZdCJV9GKWNKEVc1/UADhpW3QlF"
    "zDil7co3eSoqZ4iIyTnK+EjaB0iJOitsHO0LzGyLTr0q7t1LDn3cbo3scA6a+Do2k9nVdBoFpEh4aQkZCau5aH2bSlmZeanJ"
    "qdx6+pmoJ8zG1Lz3BOwI1xxZJ2AOqrgqVmPapYRLFfS4Fwdo59g9q4ofPRusvDwK6mo7KssnFrcchePt91VdVuR9VuRwDjon"
    "m2dUyRZWCQZF+vk4fCpprasIr3zafWzcrGvbqQnq15h5bHYETXcFTScE/WdFMA3JtzuHdPkmNdypuV49PIuamejoSHm5GUj4"
    "aLmZCVgJ20bImgil1efE9QhVBOe0ZEAOeVca9dOdVDNthGOZqPmYuAipSLknJpcIKLlqKrtpW0y36dtFlnhkNRcE9OZEtKYA"
    "DfmXmTTS2nLSa4PjeHgIm1rrfSz8rc2dTg5ua9w8PSs7qSc3qCeqNqYotXV3ViYoAA2JuCiUwzfygln0hFypaMtYF3ubizx8"
    "bBxsXEo6Khr1RTn0RDnmyPkmCDimeHmXaWANWUeqxrUYEpK4QsLrZMRZAmH5F0a+3Qx9vZ2pqYmZE9PpZCQ69zjrV5lK99or"
    "WDqADHk322gmykW1mTSkiSR0itYmOpoZ7p4d7W5urY6Oy6n5y6n5zVrKrYr63Woa3JlKAA14RzrltKy2VavlhNb1JOzbCs6/"
    "Tx2uPgrr3HipmjwqidxKqfvJmM2bap2q6tzaGgANKGdaVZSLhIPrBANm9DQsqendTo6cnd3svCw56Vlsallbybi8Sop7+jos"
    "yfoseanQC/j4Sre3DDjGjFjmqHgHatppzB2OKftsCnoaPJw8Xk29xqYWI3RFhVYnbNsq3hxsEAt5WOknBplmpFsoZh1ap/tY"
    "pfoLfIobjJpYeB2bu1pKKjRkRFYWluhIyRgV9gspCRAIx2b2tVTlJCQnNjY4ZwaWhSS0xjcWZ9i4uSn5CXpFJQVURCR2VlZ7"
    "a2uI19f1lJS0nSufWWhUvLAAAAAElFTkSuQmCC"
)

workspace: str = "./"

type CompressType = Literal["raw", "zlib", "bz2", "lzma"]
compress_types: list[CompressType] = ["raw", "zlib", "bz2", "lzma"]