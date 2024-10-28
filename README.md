# easyword2num

`easyword2num` is a Python library that converts English words representing numbers into their numerical values. It supports large numbers, fractions, decimals, negative numbers, and mixed decimal-unit expressions.

## Install

```bash
pip install easyword2num
```

## Usage

```python
from easyword2num import word2num

# Basic usage
number = word2num("seven million three thousand and four point five")
print(number)  # Output: 7003004.5

# Handles negative numbers
number = word2num("negative sixteen")
print(number)  # Output: -16

# Fractions
number = word2num("one fifth")
print(number)  # Output: 0.2

# Decimals
number = word2num("two point three")
print(number)  # Output: 2.3

# Mixed decimal-unit expressions
number = word2num("1.2 million")
```

### Handling Numerical Sequences

By default, `word2num` does not interpret numerical sequences like "twenty nineteen" as `2019`. To enable this behavior, set the `allow_numerical_sequences` parameter to `True`.

```python
number = word2num("twenty nineteen", allow_numerical_sequences=True)
print(number)  # Output: 2019
```

## Error Handling

If the input string cannot be interpreted as a number, a `UninterpretableNumberError` is raised.

```python
from easyword2num import word2num, UninterpretableNumberError

try:
    number = word2num("invalid input")
except UninterpretableNumberError as e:
    print(f"Error: {e}")
```


## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request on [GitHub](https://github.com/yourusername/easyword2num).

## Development Setup

#### If you use [Poetry](https://python-poetry.org/)

```bash
poetry install
poetry run pytest
```

#### Otherwise...


```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
pytest
```

## License

This project is licensed under the [MIT License](LICENSE).
