import random

class Opponent:
    def __init__(self, json_profile):
        self.name = json_profile["name"]
        self.methods = list(json_profile["methods"].items())

    def try_select_card(self, cards, top_discard, chosen_suit):
        """Try to select a card to play from hand.
        :param cards: Opponent's hand of cards (list)
        :param top_discard: Top card on discard pile.
        :param chosen_suit: Explicitly-chosen suit (if top card is 8).
        :return: Selected card to play, or None if there are no moves.
        """
        methods = list(self.methods)
        selected_card = None
        suit = chosen_suit if top_discard.rank == 8 else top_discard.suit

        while any(methods):
            method = self.choose_method(methods)
            methods.remove(method) # So we don't choose it again.

            if method[0] == "suit":
                selected_card = self.try_select_card_by_suit(cards, suit)
            elif method[0] == "rank":
                selected_card = self.try_select_card_by_rank(cards, top_discard.rank)
            elif method[0] == "eight":
                selected_card = self.try_select_eight(cards)
            elif method[0] == "random":
                selected_card = self.try_select_card_at_random(cards, suit, top_discard.rank)

            if selected_card is not None: return selected_card

        return selected_card # Which ought to be None by this point.

    def choose_suit(self, cards):
        """Having played an 8 previously, choose the new suit."""
        # Tally cards by suit.
        tally = {i:0 for i in range(0,4)}
        for card_ in cards:
            tally[card_.suit] += 1
        suit_with_most_cards = max(tally, key=tally.get)
        return suit_with_most_cards

    def try_select_card_by_suit(self, cards, suit):
        """Try to select a card with suit that matches that of top discard.
        :param cards: Opponent's hand of cards (list)
        :param suit: Suit to match.
        :return: Selected card to play, or None if there are no moves.
        """
        matching_cards = [card_ for card_ in cards\
                            if card_.suit == suit\
                                and card_.rank != 8]
        if any(matching_cards):
            return random.choice(matching_cards)

    def try_select_card_by_rank(self, cards, rank):
        """Try to select a card with rank that matches that of top discard.
        :param cards: Opponent's hand of cards (list)
        :param rank: Rank to match.
        :return: Selected card to play, or None if there are no moves.
        """
        matching_cards = [card_ for card_ in cards\
                            if card_.rank == rank\
                                and card_.rank != 8]
        if any(matching_cards):
            return random.choice(matching_cards)

    def try_select_eight(self, cards):
        """Try to select an 8 card.
        :param cards: Opponent's hand of cards (list)
        :return: Selected card to play, or None if there are no moves.
        """
        matching_cards = [card_ for card_ in cards\
                            if card_.rank == 8]
        if any(matching_cards):
            return random.choice(matching_cards)

    def try_select_card_at_random(self, cards, suit, rank):
        """Try to select a card at random that matches that of top discard.
        :param cards: Opponent's hand of cards (list)
        :param suit: Suit to match.
        :param rank: Rank to match.
        :return: Selected card to play, or None if there are no moves.
        """
        matching_cards = [card_ for card_ in cards\
                            if card_.suit == suit\
                                or card_.rank == rank\
                                or card_.rank == 8]
        if any(matching_cards):
            return random.choice(matching_cards)

    @staticmethod
    def choose_method(methods):
        total_weight = sum(i[1] for i in methods)
        choice = random.randint(1, total_weight)
        accum = 0
        for method in methods:
            accum += method[1]
            if accum >= choice:
                return method
