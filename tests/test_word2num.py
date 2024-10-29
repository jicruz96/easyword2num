from typing import Type

import pytest

from easyword2num import UninterpretableNumberError, word2num


# Test cases for standard number interpretations
@pytest.mark.parametrize(
    "text, expected",
    [
        ("two million three thousand nine hundred and eighty four", 2003984),
        ("nineteen", 19),
        ("two thousand and nineteen", 2019),
        ("two million three thousand and nineteen", 2003019),
        ("three billion", 3_000_000_000),
        ("three million", 3_000_000),
        (
            "one hundred twenty three million four hundred fifty six thousand seven hundred and eighty nine",
            123456789,
        ),
        ("eleven", 11),
        ("nineteen billion and nineteen", 19000000019),
        ("one hundred and forty two", 142),
        ("112", 112),
        ("11211234", 11211234),
        ("five", 5),
        ("two million twenty three thousand and forty nine", 2023049),
        ("two point three", 2.3),
        (
            "two million twenty three thousand and forty nine point two three six nine",
            2023049.2369,
        ),
        (
            "one billion two million twenty three thousand and forty nine point two three six nine",
            1002023049.2369,
        ),
        ("point one", 0.1),
        ("point nineteen", 0.19),
        ("one hundred thirty-five point five", 135.5),
        ("a hundred", 100),
        ("thousand", 1000),
        ("million", 1000000),
        ("billion", 1000000000),
        ("nine point nine nine nine", 9.999),
        ("zero", 0),
        ("1.2 billion", 1_200_000_000),
        ("point zero one", 0.01),
        ("negative sixteen", -16),
        ("one trillion, seven-hundred million", 1_000_700_000_000),
        ("negative one hundred", -100),
        ("negative two", -2),
        ("three hundredths", 0.03),
        ("one fifth", 0.2),
        ("a hundred thousand", 100_000),
        ("twenty-one", 21),
        ("twenty-one point five", 21.5),
        ("negative one point zero zero one", -1.001),
        ("negative one point oh", -1.0),
        ("negative one point oh oh one", -1.001),
    ],
)
def test_word2num_standard_cases(text: str, expected: float):
    """Test cases for standard number interpretations."""
    assert word2num(text) == expected


# Test cases with allow_numerical_sequences flag set to True
@pytest.mark.parametrize(
    "text, expected",
    [
        ("twenty nineteen", 2019),
        ("twenty twenty", 2020),
        ("nineteen ten", 1910),
        ("nineteen o'one", 1901),
        ("nineteen oh one", 1901),
        ("nineteen one", 191),
        ("one o' one", 101),
    ],
)
def test_word2num_with_sequences(text: str, expected: float):
    """Test cases for number interpretations with numerical sequences allowed."""
    assert word2num(text, allow_numerical_sequences=True) == expected


# Test cases expected to raise exceptions
@pytest.mark.parametrize(
    "text, expected_exception",
    [
        ("one nineteen", UninterpretableNumberError),
        ("twenty nineteen", UninterpretableNumberError),
        ("nineteen one", UninterpretableNumberError),
        ("two three six nine", UninterpretableNumberError),
        ("112-", UninterpretableNumberError),
        ("-", UninterpretableNumberError),
        ("on", UninterpretableNumberError),
        ("million million", UninterpretableNumberError),
        ("three million million", UninterpretableNumberError),
        ("million four million", UninterpretableNumberError),
        ("one million, seven-hundred trillion", UninterpretableNumberError),
        ("thousand million", UninterpretableNumberError),
        (
            "one billion point two million twenty three thousand and forty nine point two three six nine",
            UninterpretableNumberError,
        ),
        ("twenty zero", UninterpretableNumberError),
        ("zero twenty", UninterpretableNumberError),
        ("zero hundred", UninterpretableNumberError),
        ("negative", UninterpretableNumberError),
        (112, TypeError),
    ],
)
def test_word2num_exceptions(text: str, expected_exception: Type[Exception]):
    """Test cases expected to raise exceptions."""
    with pytest.raises(expected_exception):
        word2num(text)
