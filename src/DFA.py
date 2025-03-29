from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

STATE = TypeVar('STATE')

@dataclass
class DFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], STATE]
    F: set[STATE]

    def accept(self, word: str) -> bool:
        current_state = self.q0
        #Parcurgem cuvantul
        for symbol in word:
            #Verificam daca exista tranzitia
            if (current_state, symbol) in self.d:
                #Urmatoarea stare
                current_state = self.d[(current_state, symbol)]
            else:
                #Reject
                return False
            #Accept
        return current_state in self.F

    def remap_states[OTHER_STATE](self, f: Callable[[STATE], 'OTHER_STATE']) -> 'DFA[OTHER_STATE]':
        # optional, but might be useful for subset construction and the lexer to avoid state name conflicts.
        # this method generates a new dfa, with renamed state labels, while keeping the overall structure of the
        # automaton.

        # for example, given this dfa:

        # > (0) -a,b-> (1) ----a----> ((2))
        #               \-b-> (3) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

        # applying the x -> x+2 function would create the following dfa:

        # > (2) -a,b-> (3) ----a----> ((4))
        #               \-b-> (5) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

        pass

    def minimize(self) -> 'DFA[STATE]':
        # Inițializarea partițiilor
        non_final_states = self.K - self.F #Stari nefinale
        P = {frozenset(self.F), frozenset(non_final_states)} #Partitiile
        #Initializarea W cu partitia mai mica
        if len(self.F) <= len(non_final_states):
            W = {frozenset(self.F)}
        else:
            W = {frozenset(non_final_states)}
        #Parcurgem W
        while W:
            #Scoatem cate un element din W
            A = W.pop()
            #Parcurgem alfabetul
            for c in self.S:
                X = set()
                #Parcurgem starile
                for state in self.K:
                    next_state = self.d.get((state, c))
                    #Verificam daca exista tranzitia
                    if next_state in A:
                        X.add(state)

                new_P = set()
                #Parcurgem partitiile
                for Y in P:
                    #Calculam intersectia si diferenta
                    intersection = X & Y
                    difference = Y - X
                    #Verificam daca sunt nevide
                    if intersection and difference:
                        #Adaugam in partitii daca sunt nevide
                        new_P.add(frozenset(intersection))
                        new_P.add(frozenset(difference))
                        #Verificam daca exista in W
                        if Y in W:
                            #Scoatem Y din W si adaugam intersectia si diferenta
                            W.remove(Y)
                            W.add(frozenset(intersection))
                            W.add(frozenset(difference))
                        else:
                            #Adaugam in W partitia mai mica
                            if len(intersection) <= len(difference):
                                W.add(frozenset(intersection))
                            else:
                                W.add(frozenset(difference))
                    else:
                        #Adaugam in partitii daca sunt vide
                        new_P.add(Y)

                P = new_P

        # Construim DFA-ul minimizat
        state_mapping = {}
        #Parcurgem partitiile
        for i, block in enumerate(P):
            for state in block:
                state_mapping[state] = i
        #Initializam noile stari, tranzitii si starile finale
        new_states = set(state_mapping.values())
        new_transitions = {}
        #Parcurgem tranzitiile
        for (s, c), t in self.d.items():
            #Verificam daca exista tranzitia
            if s in state_mapping and t in state_mapping:
                new_transitions[(state_mapping[s], c)] = state_mapping[t]

        new_final_states = set()
        #Parcurgem starile finale
        for s in self.F:
            #Verificam daca exista in partitii
            if s in state_mapping:
                #Adaugam in starile finale
                new_final_states.add(state_mapping[s])

        new_initial_state = state_mapping[self.q0]
        #Returnam DFA-ul minimizat
        return DFA(
            S=self.S,
            K=new_states,
            q0=new_initial_state,
            d=new_transitions,
            F=new_final_states
        )



