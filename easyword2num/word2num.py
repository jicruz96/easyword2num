from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Callable, List, Literal, Union


class UninterpretableNumberError(ValueError):
    """Raised when a string cannot be interpreted as a number."""

    pass


@dataclass
class NumberSystemToken:
    """Represents a token in a number system, with specific properties and rules.

    Attributes:
        word:                               The word representing the number or symbol.
        allowed_position:                   Specifies where this token is allowed in a sequence.
        is_unique:                          If True, this token should appear only once.
        number:                             The numeric value of the token, if any.
        is_usable_as_decimal:               If True, can be used in decimal positions. (e.g., 'three', but not 'thousand').
        is_unit:                            If True, signifies a unit (e.g., 'hundred').
        is_usable_as_regular_denominator:   If True, can be used as a denominator in fractions.
        irregular_denominator:              The word to use for its denominator, if not regular, and if usable as a denominator.
        additional_validation:              A callable to validate the token's placement within a sequence.
    """

    word: str
    allowed_position: Literal[
        "beginning",  # "negative"
        "end",  # "thousandth"
        "anywhere",  # "one"
        "anywhere-except-at-beginning",  # "thousand"
        "anywhere-except-at-end",  # "point"
        "anywhere-except-ends",  # "and"
    ]
    is_unique: bool
    number: Union[int, float, None]
    is_usable_as_decimal: bool
    is_unit: bool
    is_usable_as_regular_denominator: bool
    irregular_denominator: Union[str, None]
    additional_validation: Union[Callable[[int, List[NumberSystemToken]], bool], None]

    def _as_fractional_token(self, **kwargs: Any) -> NumberSystemToken:
        config: dict[str, Any] = {
            "number": 1 / self.number,  # type: ignore
            "allowed_position": "end",
            "is_unique": True,
            "is_unit": True,
            "is_usable_as_decimal": False,
            "is_usable_as_regular_denominator": False,
            "irregular_denominator": None,
            "additional_validation": None,
            **kwargs,
        }
        return self.__class__(**config)

    @cached_property
    def is_standalone(self) -> bool:
        return self.number is not None and self.number < 100 and not self.is_fraction

    @cached_property
    def is_fraction(self) -> bool:
        return self.number is not None and 0 < abs(self.number) < 1

    def as_fractional_tokens(self) -> List[NumberSystemToken]:
        if self.number in (0, None):
            return []

        fractional_tokens: List[NumberSystemToken] = []
        if self.is_usable_as_regular_denominator:
            fractional_tokens.extend(
                [
                    self._as_fractional_token(word=f"{self.word}th"),
                    self._as_fractional_token(
                        word=f"{self.word}ths",
                        additional_validation=lambda i, arr: arr[i - 1].word != "one",  # type: ignore
                    ),
                ]
            )
        if self.irregular_denominator:
            fractional_tokens.append(
                self._as_fractional_token(word=self.irregular_denominator)
            )
        return fractional_tokens


class NumberSystemVocabulary(ABC):
    """Abstract base class for a number system vocabulary."""

    @cached_property
    @abstractmethod
    def tokens(self) -> dict[str, NumberSystemToken]:
        """Returns a dictionary of number system tokens."""
        pass

    @cached_property
    @abstractmethod
    def negative_indicators(self) -> List[str]:
        """Returns a list of words indicating a negative number."""
        pass

    @cached_property
    @abstractmethod
    def decimal_indicators(self) -> List[str]:
        """Returns a list of words indicating a decimal point."""
        pass

    @abstractmethod
    def is_valid_sequence(
        self,
        tokens: List[NumberSystemToken],
        allow_numerical_sequences: bool,
    ) -> bool:
        """Determines if a sequence of tokens forms a valid number expression."""
        pass

    @cached_property
    @abstractmethod
    def language_code(self) -> str:
        """Returns the language code of the vocabulary."""
        pass


class AmericanNumberSystemVocabulary(NumberSystemVocabulary):
    """Defines the American English number system vocabulary."""

    @cached_property
    def language_code(self) -> str:
        return "en-us"

    @cached_property
    def negative_indicators(self) -> List[str]:
        return ["negative", "minus"]

    @cached_property
    def decimal_indicators(self) -> List[str]:
        return ["point", "dot"]

    @cached_property
    def noop_words(self) -> List[str]:
        return ["and", "&"]

    @cached_property
    def irregular_denominators(self) -> dict[str, str]:
        return {
            "two": "half",
            "four": "quarter",
            "three": "third",
            "five": "fifth",
            "eight": "eighth",
            "nine": "ninth",
            "twelve": "twelfth",
            "twenty": "twentieth",
            "thirty": "thirtieth",
            "forty": "fortieth",
            "fifty": "fiftieth",
            "sixty": "sixtieth",
            "seventy": "seventieth",
            "eighty": "eightieth",
            "ninety": "ninetieth",
        }

    @cached_property
    def tokens(self) -> dict[str, NumberSystemToken]:
        tokens = {
            token.word: token
            for token in [
                # NUMBERS
                *[
                    NumberSystemToken(
                        word=word,
                        number=i,
                        allowed_position="anywhere",
                        is_usable_as_decimal=True,
                        is_unit=False,
                        is_unique=False,
                        irregular_denominator=self.irregular_denominators.get(word),
                        is_usable_as_regular_denominator=word
                        not in self.irregular_denominators
                        # four is the only fraction with both an irregular and regular denominator
                        or word == "four",
                        additional_validation=None,
                    )
                    for i, word in enumerate(
                        start=1,
                        iterable=[
                            "one",
                            "two",
                            "three",
                            "four",
                            "five",
                            "six",
                            "seven",
                            "eight",
                            "nine",
                            "ten",
                            "eleven",
                            "twelve",
                            "thirteen",
                            "fourteen",
                            "fifteen",
                            "sixteen",
                            "seventeen",
                            "eighteen",
                            "nineteen",
                        ],
                    )
                ],
                *[
                    NumberSystemToken(
                        word=word,
                        number=i * 10,
                        allowed_position="anywhere",
                        is_unit=False,
                        is_unique=False,
                        is_usable_as_regular_denominator=False,
                        is_usable_as_decimal=False,
                        irregular_denominator=self.irregular_denominators.get(word),
                        additional_validation=None,
                    )
                    for i, word in enumerate(
                        start=2,
                        iterable=[
                            "twenty",
                            "thirty",
                            "forty",
                            "fifty",
                            "sixty",
                            "seventy",
                            "eighty",
                            "ninety",
                        ],
                    )
                ],
                NumberSystemToken(
                    word="zero",
                    number=0,
                    allowed_position="anywhere",  # not really... check additional validation
                    is_unique=True,
                    is_usable_as_decimal=True,
                    is_unit=False,
                    is_usable_as_regular_denominator=False,
                    irregular_denominator=None,
                    additional_validation=lambda i, arr: (
                        # "zero" is ok if...
                        # case 1: it's the only token (i.e. just ["zero"])
                        len(arr) == 1
                        # case 2: zero is after a decimal point (e.g. [..., "point", "zero"])
                        or any(word.word in self.decimal_indicators for word in arr[:i])
                        # case 3: ["zero", "point", ...] is ok too
                        or (i == 0 and arr[i + 1].word in self.decimal_indicators)
                    ),
                ),
                *[
                    NumberSystemToken(
                        word=zero_word,
                        number=0,
                        allowed_position="anywhere",  # not really... check additional validation
                        is_unique=True,
                        is_usable_as_decimal=True,
                        is_unit=False,
                        is_usable_as_regular_denominator=False,
                        irregular_denominator=None,
                        additional_validation=lambda i, arr: (
                            # "oh" or "o'" is ok if it's part of a numerical sequence.
                            # we can check if we're amidst a numerical sequence by checking
                            # if the previous and next tokens are standalone.
                            (i == 0 or arr[i - 1].is_standalone)
                            and ((i == len(arr) - 1) or arr[i + 1].is_standalone)
                        ),
                    )
                    for zero_word in ["oh", "o"]
                ],
                # UNITS
                NumberSystemToken(
                    word="hundred",
                    number=100,
                    allowed_position="anywhere",
                    is_unique=False,
                    is_usable_as_decimal=False,
                    is_unit=True,
                    is_usable_as_regular_denominator=True,
                    irregular_denominator=None,
                    additional_validation=None,
                ),
                *[
                    NumberSystemToken(
                        word=word,
                        number=10 ** (3 * i),
                        allowed_position="anywhere",
                        is_unique=True,
                        is_usable_as_decimal=False,
                        is_unit=True,
                        is_usable_as_regular_denominator=True,
                        irregular_denominator=None,
                        additional_validation=None,
                    )
                    for i, word in enumerate(
                        start=1,
                        iterable=[
                            "thousand",
                            "million",
                            "billion",
                            "trillion",
                            "quadrillion",
                            "quintillion",
                            "sextillion",
                            "septillion",
                            "octillion",
                            "nonillion",
                            "decillion",
                        ],
                    )
                ],
                # negatives
                *[
                    NumberSystemToken(
                        word=word,
                        number=None,
                        allowed_position="beginning",
                        is_unique=True,
                        is_usable_as_decimal=False,
                        is_unit=False,
                        is_usable_as_regular_denominator=False,
                        irregular_denominator=None,
                        additional_validation=lambda i, arr: len(arr) > 1,
                    )
                    for word in self.negative_indicators
                ],
                # decimal indicators
                *[
                    NumberSystemToken(
                        word=word,
                        number=None,
                        allowed_position="anywhere-except-at-end",
                        is_unique=True,
                        is_usable_as_decimal=False,
                        is_unit=False,
                        is_usable_as_regular_denominator=False,
                        irregular_denominator=None,
                        additional_validation=lambda i, arr: i != len(arr) - 1,
                    )
                    for word in self.decimal_indicators
                ],
                # GLUE GUYS (i.e. no-ops)
                *[
                    NumberSystemToken(
                        word=noop_word,
                        number=None,
                        allowed_position="anywhere-except-ends",
                        is_unique=False,
                        is_usable_as_decimal=False,
                        is_unit=False,
                        is_usable_as_regular_denominator=False,
                        irregular_denominator=None,
                        additional_validation=None,
                    )
                    for noop_word in self.noop_words
                ],
                # OTHER
                NumberSystemToken(
                    word="a",
                    number=1,
                    allowed_position="beginning",
                    is_unique=True,
                    is_usable_as_decimal=False,
                    is_unit=False,
                    is_usable_as_regular_denominator=False,
                    irregular_denominator=None,
                    additional_validation=None,
                ),
            ]
        }
        for token in list(tokens.values()):
            for fractional_token in token.as_fractional_tokens():
                tokens[fractional_token.word] = fractional_token
        return tokens

    def is_valid_sequence(
        self,
        tokens: List[NumberSystemToken],
        allow_numerical_sequences: bool = False,
    ) -> bool:
        if not tokens or not any(token.number is not None for token in tokens):
            return False

        seen: set[str] = set()
        highest_unique_unit: Union[float, None] = None
        is_decimal: bool = False
        prev: Union[NumberSystemToken, None] = None

        def _in_invalid_position(token: NumberSystemToken, i: int) -> bool:
            if token.allowed_position == "anywhere":
                return False
            if token.allowed_position == "anywhere-except-at-beginning":
                return i == 0
            if token.allowed_position == "anywhere-except-at-end":
                return i == len(tokens) - 1
            if token.allowed_position == "beginning":
                return i != 0
            if token.allowed_position == "end":
                return i != len(tokens) - 1
            if token.allowed_position == "anywhere-except-ends":
                return i in (0, len(tokens) - 1)
            raise ValueError(f"Invalid allowed position: {token.allowed_position}")

        def _unique_token_is_duplicated(token: NumberSystemToken) -> bool:
            return token.is_unique and token.word in seen

        def _unit_order_is_invalid(token: NumberSystemToken) -> bool:
            return highest_unique_unit is not None and (
                token.is_unit
                and token.number is not None
                and token.number > highest_unique_unit
            )

        def _is_invalid_sequence(
            token: NumberSystemToken, prev: Union[NumberSystemToken, None]
        ) -> bool:
            return (
                not is_decimal
                and not allow_numerical_sequences
                and token.number is not None
                and prev is not None
                and prev.is_standalone
                and token.is_standalone
                and (
                    token.number >= 10
                    or prev.word
                    not in [
                        "twenty",
                        "thirty",
                        "forty",
                        "fifty",
                        "sixty",
                        "seventy",
                        "eighty",
                        "ninety",
                    ]
                )
            )

        def _additional_validation(token: NumberSystemToken) -> bool:
            return token.additional_validation is None or token.additional_validation(
                i, tokens
            )

        for i, token in enumerate(tokens):
            if (
                _unique_token_is_duplicated(token)
                or _unit_order_is_invalid(token)
                or _in_invalid_position(token, i)
                or _is_invalid_sequence(token, prev)
                or (is_decimal and not token.is_usable_as_decimal)
                or not _additional_validation(token)
            ):
                return False
            if token.is_unit and token.is_unique and token.number is not None:
                highest_unique_unit = token.number
            is_decimal |= token.word in self.decimal_indicators
            seen.add(token.word)
            prev = token
        return True


class NumberSystem:
    """Interprets words representing numbers according to a specified vocabulary.

    Attributes:
        vocabulary: The vocabulary used to interpret number words.
    """

    def __init__(
        self,
        vocabulary: NumberSystemVocabulary = AmericanNumberSystemVocabulary(),
        allow_numerical_sequences: bool = False,
    ):
        """Initializes the number system with a given vocabulary.

        Args:
            vocabulary: The vocabulary for interpreting number words.
        """
        self.vocabulary = vocabulary
        self.allow_numerical_sequences = allow_numerical_sequences

    def tokenize(self, string: str) -> List[NumberSystemToken]:
        """Tokenizes a string of number words.

        Args:
            string: The string to tokenize.

        Returns:
            A list of NumberSystemToken objects representing the parsed words.

        Raises:
            UninterpretableNumberError: If the string contains unrecognized words.
        """
        try:
            tokens = [
                self.vocabulary.tokens[word]
                for word in string.replace(",", "")
                .replace("'", " ")
                .replace("-", " ")
                .lower()
                .strip()
                .split()
            ]
            assert self.vocabulary.is_valid_sequence(
                tokens,
                allow_numerical_sequences=self.allow_numerical_sequences,
            )
            return tokens
        except (KeyError, AssertionError):
            raise UninterpretableNumberError(string) from None

    def interpret(self, string: str) -> float:
        """Interprets a tokenized string of number words as a float.

        Args:
            string: The string to interpret.

        Returns:
            The numeric interpretation of the string.

        Raises:
            UninterpretableNumberError: If the string cannot be interpreted as a number.
        """
        # Handle edge case: "1.2 million" (i.e digits followed by a unit)
        if match := re.match(
            r"(?P<number>-?\d{1,3}(\.\d{1,3})?)\s+(?P<unit>(\w+?illion|thousand))",
            string,
        ):
            number = float(match.group("number"))
            unit = self.vocabulary.tokens[match.group("unit")].number
            assert unit is not None
            return number * unit
        # Handle general case
        tokens = self.tokenize(string)
        negative = False
        if tokens[0].word in self.vocabulary.negative_indicators:
            negative = True
            tokens.pop(0)
        n = 0.0
        prev: Union[NumberSystemToken, None] = None
        while tokens:
            token = tokens.pop(0)
            if token.word in self.vocabulary.decimal_indicators:
                decimals = tokens
                n += float("0." + "".join(str(word.number) for word in decimals))
                break
            if token.number is not None:
                if token.is_unit and n != 0:
                    if token.number >= 1:
                        div, mod = divmod(n, token.number)
                        n = (div + mod) * token.number
                    else:
                        n *= token.number
                elif (
                    token.is_standalone
                    and prev is not None
                    and prev.is_standalone
                    and (
                        prev.word
                        not in [
                            "twenty",
                            "thirty",
                            "forty",
                            "fifty",
                            "sixty",
                            "seventy",
                            "eighty",
                            "ninety",
                        ]
                        or token.number >= 10
                    )
                ):
                    if not self.allow_numerical_sequences:
                        raise UninterpretableNumberError(
                            f"Unexpected numerical sequence: {string!r}\n\n"
                            "This should have been caught by this library's internal validation. "
                            "This is a bug. Plese report it at https://github.com/jicruz96/easyword2num/issues"
                        )
                    n = float(f"{int(n)}{token.number}")

                else:
                    n += token.number
            prev = token
        if negative:
            n = -n
        return n


def word2num(string: str, allow_numerical_sequences: bool = False) -> float:
    """Converts a string representation of a number to a float.

    Args:
        string: The string to convert.
        allow_numerical_sequences: Whether to allow interpeting strings like "one two three" as 123.

    Returns:
        The floating-point number interpretation of the string.

    Raises:
        TypeError: If the input is not a string.
        UninterpretableNumberError: If the string cannot be interpreted as a number.
    """
    if not isinstance(string, str):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise TypeError(f"Expected a string, but got {type(string)}")
    # Handle basic case: string is a number, just float() it.
    try:
        return float(string)
    except ValueError:
        pass
    return NumberSystem(allow_numerical_sequences=allow_numerical_sequences).interpret(
        string
    )
