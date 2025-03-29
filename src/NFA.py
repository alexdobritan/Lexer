from collections import deque

from .DFA import DFA

from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs


@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        #Initializam closure cu starea data
        closure = {state}
        #Initializam stiva cu starea data
        stack = [state]
        #Parcurgem stiva
        while stack:
            #Starea curenta
            current = stack.pop()
            #Verificam daca exista tranzitii cu epsilon
            if (current, EPSILON) in self.d:
            #Adaugam starea in closure
                #Parcurgem tranzitiile cu epsilon
                for next_state in self.d[(current, EPSILON)]:
                    #Verificam daca starea nu este in closure
                    if next_state not in closure:
                        #Daca nu, adaugam starea in closure si in stiva
                        closure.add(next_state)
                        stack.append(next_state)
        #Returnam closure
        return closure

    def subset_construction(self) -> 'DFA[frozenset[STATE]]':
        # Starile din DFA
        dfa_states = []
        dfa_transitions = {}
        dfa_final_states = set()

        # Calculam epsilon-closure pentru starea inițiala a NFA
        start_closure = self.epsilon_closure(self.q0)
        start_closure = frozenset(start_closure)
        #Adaugam
        dfa_states.append(start_closure)

        # Verificăm dacă starea inițială include o stare finală din NFA
        if self.F.intersection(start_closure):
            dfa_final_states.add(start_closure)

        # Procesăm stările în ordine
        index = 0
        while index < len(dfa_states):
            # Obținem starea curentă din DFA
            current_dfa_state = dfa_states[index]
            index += 1

            # Generăm tranziții pentru fiecare simbol din alfabet (fără epsilon)
            for symbol in self.S:
                # Calculăm stările următoare în NFA pentru simbolul curent
                next_states = set()
                for nfa_state in current_dfa_state:
                    if (nfa_state, symbol) in self.d:
                        next_states.update(self.d[(nfa_state, symbol)])

                # Aplicăm epsilon-closure pentru toate stările următoare
                epsilon_closure = set()
                for state in next_states:
                    epsilon_closure.update(self.epsilon_closure(state))

                # Transformăm epsilon-closure într-o stare DFA
                next_dfa_state = frozenset(epsilon_closure)

                # Adăugăm tranziția în DFA
                dfa_transitions[(current_dfa_state, symbol)] = next_dfa_state

                # Verificăm dacă starea este deja în DFA
                if next_dfa_state not in dfa_states:
                    dfa_states.append(next_dfa_state)

                    # Dacă starea conține o stare finală din NFA, o marcăm ca finală
                    if self.F.intersection(next_dfa_state):
                        dfa_final_states.add(next_dfa_state)

        # Returnam DFA-ul rezultat
        return DFA(
            S=self.S,
            K=set(dfa_states),
            q0=frozenset(self.epsilon_closure(self.q0)),
            d=dfa_transitions,
            F=dfa_final_states,
        )

    def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
        # optional, but may be useful for the second stage of the project. Works similarly to 'remap_states'
        # from the DFA class. See the comments there for more details.

        return NFA(
            S=self.S,
            K={f(state) for state in self.K},
            q0=f(self.q0),
            d={(f(state), symbol): {f(next_state) for next_state in states} for (state, symbol), states in self.d.items()},
            F={f(state) for state in self.F},
        )
