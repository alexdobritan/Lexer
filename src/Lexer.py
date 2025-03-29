import re


class Lexer:
    def __init__(self, spec: list[tuple[str, str]]) -> None:
        self.spec = [(name, re.compile(regex)) for name, regex in spec]

    def lex(self, word: str) -> list[tuple[str, str]] | None:
        tokens = []
        position = 0
        while position < len(word):
            l_match = None
            l_token = None
            l_length = 0
            for name, regex in self.spec:
                match = regex.match(word, position)
                if match:
                    match_length = len(match.group())
                    if match_length > l_length:
                        l_match = match.group()
                        l_token = name
                        l_length = match_length

            if l_match:
                tokens.append((l_token, l_match))
                position += l_length
            else:
                return None
        return tokens