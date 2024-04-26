import pytest

from src.source_parsing.token_extractor import FirstChannelTokenExtractor, SecondChannelTokenExtractor


def read_token_extractors_test_data() -> dict[int, list[str]]:
    test_data = {
        1: open("test_data/first_channel_token_extractor_test_data.txt", "r").read().split("{!}"),
        2: open("test_data/second_channel_token_extractor_test_data.txt", "r").read().split("{!}"),
        3: open("test_data/third_channel_token_extractor_test_data.txt", "r").read().split("{!}")
    }
    return test_data


class TestFirstChannelTokenExtractor:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "message_text, token",
        [
            (read_token_extractors_test_data()[1][0],
             "27ZcxBcd4AXf1Cecpx65wpNRfsSUmfjfFZSAVhM3gVju"),
            (read_token_extractors_test_data()[1][1],
             "firZUS42cb5kqh5sykWusSX8QZF98XUWpo6u3UcUNCK")
        ]
    )
    async def test_get_token_from_message(self, message_text, token):
        assert await FirstChannelTokenExtractor().get_token_from_message(message_text) == token


class TestSecondChannelTokenExtractor:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "message_text, token",
        [
            (read_token_extractors_test_data()[2][0],
             "GGkhidDrHQGtSffVkwf1WdTPuLuwjSTCUUyR57wN3saY"),
            (read_token_extractors_test_data()[2][1],
             "u4Yy6k5C3ajNAvZWMKDU4tgkhbe5fju1GpT5ji5nQVw")
        ]
    )
    async def test_get_token_message(self, message_text: str, token: str):
        assert await SecondChannelTokenExtractor().get_token_from_message(message_text) == token
