#!/usr/bin/env python
try:
    import sys
    from pygame_cards import globals, enums
except ImportError as err:
    print "Fail loading a module: %s", err
    sys.exit(2)


class DealingLogic:
    """ Exposes static methods to that run game specific logic """

    @staticmethod
    def need_to_move_self_card(players_list, active_index, deck_type):
        # Don't move if has only 1 card
        if len(players_list[active_index].cards) < 2:
            return False

        # Don't move if ranks of top 2 cards match
        if DealingLogic.is_drop_ranks_match(deck_type, players_list[active_index].cards[-1].rank, players_list[active_index].cards[-2].rank):
            return False

        lcard = players_list[active_index].cards[-1]
        for p in players_list:
            if p.name == players_list[active_index].name:
                continue
            if DealingLogic.is_drop_ranks_match(deck_type, lcard.rank, p.cards[-1].rank):
                return True

        return False

    @staticmethod
    def can_drop_card(deck_type, card, player, players_list, active_index):
        if DealingLogic.is_drop_ranks_match(deck_type, card.rank, player.cards[-1].rank):
            return True
        elif player.name == players_list[active_index].name:
            should_drop_to_other_player = False
            for p in players_list:
                if p.name == players_list[active_index].name:
                    continue
                else:
                    if DealingLogic.is_drop_ranks_match(deck_type, card.rank, p.cards[-1].rank):
                        should_drop_to_other_player = True
                        break
            if not should_drop_to_other_player:
                return True
        return False

    @staticmethod
    def is_drop_ranks_match(deck_type, drop_rank, current_rank):
        lowest_rank = enums.Rank.two
        if deck_type == enums.DeckType.short:
            lowest_rank = enums.Rank.six
        if drop_rank - current_rank == 1 or \
            drop_rank == lowest_rank and current_rank == enums.Rank.ace:
            return True
        else:
            return False


class PlayingLogic:
    """ Methods for the game playing logic for bot-players
    """
    trump = None

    def __init__(self, trump):
        PlayingLogic.trump = trump

    @staticmethod
    def get_min_by_rank(list_):
        if len(list_) > 1:
            def sort_by_rank(c):
                return c.rank
            return min(*list_, key=sort_by_rank)
        elif len(list_) == 1:
            return list_[-1]
        else:
            return None

    @staticmethod
    def choose_card_to_move(heap_top_card, cards):
        if len(cards) > 0:
            def filter_by_match(c):
                return PlayingLogic.is_card_match_heap(heap_top_card, c)
            match_list = filter(filter_by_match, cards)

            def filter_non_trump_suit(c):
                return c.suit is not PlayingLogic.trump
            non_trump_match_list = filter(filter_non_trump_suit, match_list)
            if len(non_trump_match_list) > 0:
                return PlayingLogic.get_min_by_rank(non_trump_match_list)
            else:
                return PlayingLogic.get_min_by_rank(match_list)
        else:
            return None

    @staticmethod
    def is_card_match_heap(heap_top_card, card_):
        if heap_top_card is None:
            return True
        else:
            if heap_top_card.suit == card_.suit:
                if heap_top_card.rank < card_.rank:
                    return True
            elif card_.suit == PlayingLogic.trump and heap_top_card.suit != enums.Suit.spades:
                return True
        print "selected card does not match heap top card!"
        return False


