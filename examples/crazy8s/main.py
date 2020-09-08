#!/usr/bin/env python
try:
    import sys
    import os
    import threading
    import time
    import collections
    from random import seed, randint
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
    import pygame

    from pygame_cards import game_app, controller, deck, card_holder, enums, animation
    import opponent
except ImportError as err:
    print("Fail loading a module in file:", __file__, "\n", err)
    sys.exit(2)


# Constants
DIALOG_MESSAGE = "dialog_message"


OpponentRecord = collections.namedtuple('OpponentRecord', 'hand, info')
DealState = collections.namedtuple('DealState', 'cards_per_player, round, next_player')


class Crazy8sController(controller.Controller):
    def __init__(self, objects_list=None, gui_interface=None, settings_json=None):
        super(Crazy8sController, self).__init__(objects_list, gui_interface, settings_json)

        # Set up the stockpile.
        pos = self.settings_json["stockpile"]["position"]
        offset = self.settings_json["stockpile"]["offset"]
        self.stockpile = deck.Deck(enums.DeckType.full, pos, offset, None)
        self.add_rendered_object(self.stockpile)

        # Set up the discard pile.
        pos = self.settings_json["discard"]["position"]
        offset = self.settings_json["discard"]["offset"]
        self.discard = card_holder.CardsHolder(pos, offset)
        self.add_rendered_object(self.discard)

        # Set up the player's hand.
        pos = self.settings_json["player_hand"]["position"]
        offset = self.settings_json["player_hand"]["offset"]
        self.player_hand = card_holder.CardsHolder(pos, offset)
        self.add_rendered_object(self.player_hand)

        # Set up data structure for opponent hands.
        # Each item in the list will be an Opponent named tuple.
        self.num_opponents = 0
        self.opponents = []
        self.dealer = 0 # index of player who is dealer; 0 is human player

        # UI
        self.gui_interface.show_button(self.settings_json["gui"]["restart_button"],
                                       self.restart_game, "Restart")

    def restart_game(self):
        for animation_ in self.animations:
            animation_.is_completed = True
        self.discard.move_all_cards(self.stockpile)
        self.player_hand.move_all_cards(self.stockpile)

        self.clear_opponents()
        self.dealer = 0
        self.start_game()

    def start_game(self):
        self.stockpile.shuffle()
        self.show_num_opponents_dialog()

    def on_choose_num_opponents(self, num_opponents):
        self.num_opponents = num_opponents
        self.hide_num_opponents_dialog()
        self.load_opponents()
        self.dealer = randint(0, self.num_opponents)
        self.deal()

    def load_opponents(self):
        # Determine position of opponents' hands.
        y = self.settings_json["opponent_hand"]["position_y"]
        x_range = self.settings_json["opponent_hand"]["x_range"]
        width = x_range[1] - x_range[0]
        width_per_opponent = width / self.num_opponents
        card_width = self.settings_json["card"]["size"][0]
        offset = self.settings_json["opponent_hand"]["offset"]

        for i in range(0, self.num_opponents):
            x = x_range[0] + ((i+0.5)*width_per_opponent) - (card_width/2)
            hand = card_holder.CardsHolder((x, y), offset)
            self.add_rendered_object(hand)
            opponent_info = opponent.Opponent()
            self.opponents.append(OpponentRecord(hand, opponent_info))

    def show_num_opponents_dialog(self):
        """Show dialog offering the user a choice of how many opponents they
        want.
        """
        self.show_message("How many opponents would you like?")
        pos = self.settings_json["gui"]["dialog"]["content"]["position"]
        button_size = self.settings_json["gui"]["dialog"]["content"]["button_size"]
        x_base = pos[0]
        y = pos[1]
        button_margin = self.settings_json["gui"]["dialog"]["content"]["button_margin"]

        def choose(num_opponents):
            def on_choose():
                self.on_choose_num_opponents(num_opponents)
            return on_choose

        for i in range(1, 7):
            button_x = x_base + (button_size[0] * (i-1)) + (button_margin * (i-1))
            button_pos = (button_x, y)
            button_rect = [*button_pos, *button_size]
            self.gui_interface.show_button(button_rect, choose(i), f"   {i}   ",
                                            id_=f"opponent_button{i}")

    def hide_num_opponents_dialog(self):
        self.clear_message()
        for i in range(1, 7):
            self.gui_interface.hide_by_id(f"opponent_button{i}")

    def deal(self):
        """Deal the cards for the start of a game."""
        num_cards = 7 if self.num_opponents == 1 else 5
        next_player = (self.dealer + 1) % (self.num_opponents + 1)
        deal_state = DealState(cards_per_player=num_cards, round=0, next_player=next_player)
        self.deal_next_card(deal_state)

    def deal_next_card(self, deal_state: DealState):
        """Deal the next card, in the middle of a deal."""
        if deal_state.round >= deal_state.cards_per_player: return # Done dealing.

        card_ = self.stockpile.pop_top_card()
        to_hand = self.player_hand\
                    if deal_state.next_player == 0\
                    else self.opponents[deal_state.next_player-1].hand

        def on_card_dealt(holder_):
            # Finish dealing the current card.
            back_side_up = to_hand != self.player_hand
            holder_.move_all_cards(to_hand, back_side_up)
            
            # Prepare next card to deal.
            round_ = deal_state.round+1\
                if deal_state.next_player == self.dealer\
                else deal_state.round
            next_player = (deal_state.next_player + 1) % (self.num_opponents + 1)
            next_deal_state = DealState(deal_state.cards_per_player, round_, next_player)
            self.deal_next_card(next_deal_state)

        self.animate_cards([card_], to_hand.next_card_pos, on_complete=on_card_dealt)

    def clear_opponents(self):
        for i in range(0, len(self.opponents)):
            self.opponents[i].hand.move_all_cards(self.stockpile)
            self.remove_rendered_object(self.opponents[i].hand)

        self.num_opponents = 0
        self.opponents = []

    def clear_message(self):
        self.gui_interface.hide_by_id(DIALOG_MESSAGE)

    def show_message(self, text, color=None):
        pos = self.settings_json["gui"]["dialog"]["message"]["position"]
        size = self.settings_json["gui"]["dialog"]["message"]["text_size"]
        color = color or self.settings_json["gui"]["dialog"]["message"]["text_color"]
        self.clear_message()
        self.gui_interface.show_label(position=pos, text=text, text_size=size,
                                      timeout=0, color=color, id_=DIALOG_MESSAGE)

    def process_mouse_event(self, pos, down, double_click):
        print(f'process_mouse_event pos=${pos}, down=${down}, dbl-click=${double_click}')


def main():
    # Seed random number generator.
    seed(int(round(time.time() * 1000)))

    json_path = os.path.join(os.getcwd(), 'settings.json')
    crazy8s_app = game_app.GameApp(json_path=json_path, controller_cls=Crazy8sController)
    crazy8s_app.execute()

if __name__ == '__main__':
    main()
