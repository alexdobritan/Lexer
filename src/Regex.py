from dataclasses import dataclass
from typing import List
from .NFA import NFA
import re

EPSILON = ''


class Regex:
    def thompson(self) -> NFA[int]:
        raise NotImplementedError('The thompson method should be implemented in subclasses')


@dataclass
class Character(Regex):
    char: str

    def thompson(self) -> NFA[int]:
        return NFA(
            S=set([self.char]),
            K=set([0, 1]),
            q0=0,
            d={(0, self.char): set([1])},
            F=set([1])
        )


@dataclass
class Epsilon(Regex):
    def thompson(self) -> NFA[int]:
        return NFA(
            S=set([EPSILON]),
            K=set([0, 1]),
            q0=0,
            d={(0, EPSILON): set([1])},
            F=set([1])
        )


@dataclass
class Concat(Regex):
    left: Regex
    right: Regex

    def thompson(self) -> NFA[int]:
        left_nfa = self.left.thompson()
        right_nfa = self.right.thompson().remap_states(lambda s: s + len(left_nfa.K))

        new_d = {}
        for key, value in left_nfa.d.items():
            new_d[key] = set(value)
        for key, value in right_nfa.d.items():
            new_d[key] = set(value)

        for f in left_nfa.F:
            if (f, EPSILON) not in new_d:
                new_d[(f, EPSILON)] = set()
            new_d[(f, EPSILON)].add(right_nfa.q0)

        return NFA(
            S=left_nfa.S | right_nfa.S,
            K=left_nfa.K | right_nfa.K,
            q0=left_nfa.q0,
            d=new_d,
            F=right_nfa.F
        )


@dataclass
class Or(Regex):
    left: Regex
    right: Regex

    def thompson(self) -> NFA[int]:
        left_nfa = self.left.thompson().remap_states(lambda s: s + 1)
        right_nfa = self.right.thompson().remap_states(lambda s: s + len(left_nfa.K) + 1)

        new_start = 0
        new_end = len(left_nfa.K) + len(right_nfa.K) + 1

        new_d = {(new_start, EPSILON): set([left_nfa.q0, right_nfa.q0])}
        for key, value in left_nfa.d.items():
            new_d[key] = set(value)
        for key, value in right_nfa.d.items():
            new_d[key] = set(value)

        for f in left_nfa.F:
            if (f, EPSILON) not in new_d:
                new_d[(f, EPSILON)] = set()
            new_d[(f, EPSILON)].add(new_end)
        for f in right_nfa.F:
            if (f, EPSILON) not in new_d:
                new_d[(f, EPSILON)] = set()
            new_d[(f, EPSILON)].add(new_end)

        return NFA(
            S=left_nfa.S | right_nfa.S,
            K=left_nfa.K | right_nfa.K | set([new_start, new_end]),
            q0=new_start,
            d=new_d,
            F=set([new_end])
        )


@dataclass
class Star(Regex):
    expr: Regex

    def thompson(self) -> NFA[int]:
        nfa = self.expr.thompson().remap_states(lambda s: s + 1)

        new_start = 0
        new_end = len(nfa.K) + 1

        new_d = {(new_start, EPSILON): set([nfa.q0, new_end])}
        for key, value in nfa.d.items():
            new_d[key] = set(value)
        new_d[(new_end, EPSILON)] = set([new_end, nfa.q0])

        return NFA(
            S=nfa.S,
            K=nfa.K | set([new_start, new_end]),
            q0=new_start,
            d=new_d,
            F=set([new_end])
        )


@dataclass
class Plus(Regex):
    expr: Regex

    def thompson(self) -> NFA[int]:
        base_nfa = self.expr.thompson().remap_states(lambda s: s + 1)

        new_start = 0
        new_end = len(base_nfa.K) + 1

        new_d = {(new_start, EPSILON): set([base_nfa.q0])}
        for key, value in base_nfa.d.items():
            new_d[key] = set(value)
        for f in base_nfa.F:
            if (f, EPSILON) not in new_d:
                new_d[(f, EPSILON)] = set()
            new_d[(f, EPSILON)].update(set([base_nfa.q0, new_end]))

        return NFA(
            S=base_nfa.S,
            K=base_nfa.K | set([new_start, new_end]),
            q0=new_start,
            d=new_d,
            F=set([new_end])
        )


@dataclass
class Question(Regex):
    expr: Regex

    def thompson(self) -> NFA[int]:
        base_nfa = self.expr.thompson().remap_states(lambda s: s + 1)

        new_start = 0
        new_end = len(base_nfa.K) + 1

        new_d = {(new_start, EPSILON): set([base_nfa.q0, new_end])}
        for key, value in base_nfa.d.items():
            new_d[key] = set(value)

        return NFA(
            S=base_nfa.S,
            K=base_nfa.K | set([new_start, new_end]),
            q0=new_start,
            d=new_d,
            F=set([new_end])
        )

def preprocess_regex(regex: str) -> str:
    def ch_range(char_range: str) -> str:
        start, end = char_range[0], char_range[2]
        char_list = []
        for c in range(ord(start), ord(end) + 1):
            char_list.append(chr(c))
        return '(' + '|'.join(char_list) + ')'

    def replace_space(match: re.Match) -> str:
        return '<SPACE>'

    def remove_space(match: re.Match) -> str:
        return ''

    def replace_lowercase(match: re.Match) -> str:
        return ch_range('a-z')

    def replace_uppercase(match: re.Match) -> str:
        return ch_range('A-Z')

    def replace_digit(match: re.Match) -> str:
        return ch_range('0-9')

    regex = re.sub(r'\\ ', replace_space, regex)
    regex = re.sub(r'(?<!\\) ', remove_space, regex)
    regex = re.sub(r'\[a-z\]', replace_lowercase, regex)
    regex = re.sub(r'\[A-Z\]', replace_uppercase, regex)
    regex = re.sub(r'\[0-9\]', replace_digit, regex)
    regex = re.sub(r'<SPACE>', ' ', regex)

    return regex



def parse_regex(regex: str) -> Regex:
    def insert_concat_symbols(tokens: List[str]) -> List[str]:

        result = []
        for i in range(len(tokens)):
            result.append(tokens[i])
            if i + 1 < len(tokens):
                current = tokens[i]
                next_token = tokens[i + 1]
                if current not in {'(', '|'} and next_token not in {')', '|', '*', '+', '?'}:
                    result.append('`')
        return result

    def to_postfix(tokens: List[str]) -> List[str]:

        precedence = {'|': 1, '`': 2, '*': 3, '+': 3, '?': 3}

        def is_operator(token: str) -> bool:
            return token in precedence

        def handle_operator(token: str):

            while (operators and operators[-1] != '(' and
                   precedence[operators[-1]] >= precedence[token]):
                output.append(operators.pop())
            operators.append(token)

        def handle_parenthesis_close():

            while operators and operators[-1] != '(':
                output.append(operators.pop())
            if operators and operators[-1] == '(':
                operators.pop()

        output = []
        operators = []

        for token in tokens:
            if not is_operator(token) and token not in {'(', ')'}:
                output.append(token)  # Token literal
            elif is_operator(token):
                handle_operator(token)  # Operator
            elif token == '(':
                operators.append(token)  # Paranteză deschisă
            elif token == ')':
                handle_parenthesis_close()  # Paranteză închisă

        # Adaugă operatorii rămași în stivă la output
        while operators:
            output.append(operators.pop())

        return output
    #Construiește un arbore de sintaxă abstractă (AST) din lista de tokeni în notație postfixată.
    def build_ast_postfix(postfix: List[str]) -> Regex:

        stack = []

        def handle_operator(operator: str):
            if operator in {'*', '+', '?'}:
                operand = stack.pop()
                if operator == '*':
                    stack.append(Star(operand))
                elif operator == '+':
                    stack.append(Plus(operand))
                elif operator == '?':
                    stack.append(Question(operand))
            elif operator in {'`', '|'}:
                right = stack.pop()
                left = stack.pop()
                if operator == '`':
                    stack.append(Concat(left, right))
                elif operator == '|':
                    stack.append(Or(left, right))

        for token in postfix:
            if token in {'*', '+', '?', '`', '|'}:
                handle_operator(token)
            else:
                stack.append(Character(token))

        return stack[0]

    regex = preprocess_regex(regex)
    tokens = list(regex)
    tokens_with_concat = insert_concat_symbols(tokens)
    postfix_tokens = to_postfix(tokens_with_concat)
    ast = build_ast_postfix(postfix_tokens)

    return ast

