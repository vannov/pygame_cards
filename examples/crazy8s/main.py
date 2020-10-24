#!/usr/bin/env python
try:
    import sys
    import os
    import threading
    import time
    import collections
    import json
    from random import seed, randint
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
    import pygame

    from pygame_cards import game_app, controller, deck, card_holder, enums, animation
    import opponent
except ImportError as err:
    print("Fail loading a module in file:", __file__, "\n", err)
    sys.exit(2)


# Constants
STATUS_NOTIFICATION = "STATUS_NOTIFICATION"
DIALOG_TITLE = "DIALOG_TITLE"
PLAYER_PROMPT = "PLAYER_PROMPT"


OpponentRecord = collections.namedtuple('OpponentRecord', 'hand, info')
DealState = collections.namedtuple('DealState', 'cards_per_player, round, next_player')
SuitInfo = collections.namedtuple('SuitInfo', 'name, symbol')


suit_info = [
    SuitInfo('hearts', '\N{Black Heart Suit}'),
    SuitInfo('diamonds', '\N{Black Diamond Suit}'),
    SuitInfo('clubs', '\N{Black Club Suit}'),
    SuitInfo('spades', '\N{Black Spade Suit}')
]


def load_opponents_json():
    opponents_json_path = os.path.join(os.getcwd(), 'opponents.json')
    with open(opponents_json_path, 'r') as json_file:
        json_dict = json.load(json_file)
    return json_dict


class Crazy8sController(controller.Controller):
    def __init__(self, objects_list=None, gui_interface=None, settings_json=None):
        super(Crazy8sController, self).__init__(objects_list, gui_interface, settings_json)

        self.opponents_json = load_opponents_json()

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
        self.player_hand = card_holder.CardsHolder(pos, offset, enums.GrabPolicy.can_single_grab_any)
        self.add_rendered_object(self.player_hand)

        # Other global behavior
        self.opponent_min_delay_ms = self.settings_json["opponent_behavior"]["min_delay_ms"]
        self.opponent_max_delay_ms = self.settings_json["opponent_behavior"]["max_delay_ms"]

        # Set up game state.
        self.num_opponents = 0
        self.opponents = [] # Each item in the list will be an OpponentRecord tuple.
        self.dealer = 0 # index of player who is dealer; 0 is human player
        self.turn = -1 # No one's turn yet
        self.chosen_suit = None
        self.must_choose_suit = False
        self.action_lock = False

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
        self.turn = -1 # No one's turn yet
        self.chosen_suit = None
        self.must_choose_suit = False
        self.action_lock = False
        self.clear_status_notification()
        self.clear_player_prompt()
        self.start_game()

    def start_game(self):
        self.stockpile.shuffle()
        self.show_status_notification("Starting game...")
        self.show_num_opponents_dialog()

    def on_choose_num_opponents(self, num_opponents):
        self.num_opponents = num_opponents
        self.hide_num_opponents_dialog()
        self.load_opponents()
        self.dealer = randint(0, self.num_opponents)
        self.deal()

    def load_opponents(self):
        available_opponents = list(self.opponents_json)

        # Determine position of opponents' hands.
        y = self.settings_json["opponent_hand"]["position_y"]
        x_range = self.settings_json["opponent_hand"]["x_range"]
        width = x_range[1] - x_range[0]
        width_per_opponent = width / self.num_opponents
        card_width = self.settings_json["card"]["size"][0]
        offset = self.settings_json["opponent_hand"]["offset"]

        for i in range(0, self.num_opponents):
            x = x_range[0] + ((i+0.5)*width_per_opponent) - (card_width/2)
            hand = card_holder.CardsHolder((x, y), offset, enums.GrabPolicy.can_single_grab_any)
            self.add_rendered_object(hand)
            opponent_idx = randint(0, len(available_opponents)-1)
            opponent_json = available_opponents[opponent_idx]
            opponent_info = opponent.Opponent(opponent_json)
            available_opponents.remove(opponent_json)
            self.opponents.append(OpponentRecord(hand, opponent_info))
            self.show_opponent_name(opponent_info.name, i, x)

    def show_opponent_name(self, name, idx, pos_x):
        name_json = self.settings_json["opponent_hand"]["name"]
        pos = (pos_x, name_json["position_y"])
        size = name_json["text_size"]
        color = name_json["text_color"]
        label_id = f"OPPONENT_{idx}_NAME"
        self.gui_interface.hide_by_id(label_id)
        self.gui_interface.show_label(position=pos, text=name, text_size=size,
                                      timeout=0, color=color, id_=label_id)

    def show_num_opponents_dialog(self):
        """Show dialog offering the user a choice of how many opponents they
        want.
        """
        self.show_dialog_title("How many opponents would you like?")
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
        self.clear_dialog_title()
        for i in range(1, 7):
            self.gui_interface.hide_by_id(f"opponent_button{i}")

    def deal(self):
        """Deal the cards for the start of a game."""
        deal_message =\
            "You are dealing..." if self.dealer == 0\
            else f"{self.opponents[self.dealer-1].info.name} is dealing..."
        self.show_status_notification(deal_message)
        num_cards = 7 if self.num_opponents == 1 else 5
        next_player = self.player_after(self.dealer)
        deal_state = DealState(cards_per_player=num_cards, round=0, next_player=next_player)
        self.deal_next_card(deal_state)

    def deal_next_card(self, deal_state: DealState):
        """Deal the next card, in the middle of a deal."""
        if deal_state.round >= deal_state.cards_per_player:
            self.on_deal_done()
            return

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
            next_player = self.player_after(deal_state.next_player)
            next_deal_state = DealState(deal_state.cards_per_player, round_, next_player)
            self.deal_next_card(next_deal_state)

        self.animate_cards([card_], to_hand.next_card_pos, on_complete=on_card_dealt)

    def on_deal_done(self):
        self.discard_top_card_from_stockpile()

    def discard_top_card_from_stockpile(self):
        def on_card_moved(holder_):
            card_ = holder_.pop_top_card()
            card_.back_up = False
            self.discard.add_card(card_, on_top=True)
            self.next_turn()

        card_ = self.stockpile.pop_top_card()
        self.animate_cards([card_], self.discard.next_card_pos, on_complete=on_card_moved)

    def next_turn(self):
        self.turn =\
            self.player_after(self.dealer) if self.turn == -1\
            else self.player_after(self.turn)
        turn_message =\
            "Your turn" if self.is_player_turn()\
            else f"{self.opponents[self.turn-1].info.name}'s turn"
        self.show_status_notification(turn_message)

    def is_player_turn(self):
        return self.turn == 0

    def can_play_card(self, card_):
        """Whether it's legal to play the given card at this time."""
        top_card = self.discard.cards[-1]
        return \
            card_.rank == 8\
            or (top_card.rank == 8 and card_.suit == self.chosen_suit)\
            or (top_card.rank != 8 and card_.rank == top_card.rank)\
            or (top_card.rank != 8 and card_.suit == top_card.suit)

    def player_after(self, player_idx):
        return (player_idx + 1) % (self.num_opponents + 1)

    def execute_game(self):
        for idx in range(0, self.num_opponents):
            self.opponent_execute(idx)

    def opponent_execute(self, idx):
        if self.turn == idx+1:
            # It's this opponent's turn.
            if not self.action_lock:
                self.action_lock = True
                def on_end_delay(): self.opponent_play(idx)
                self.opponent_delay(on_end_delay)

    def opponent_play(self, idx):
        opponent_ = self.opponents[idx]
        hand = opponent_.hand
        
        if self.must_choose_suit:
            new_suit = opponent_.info.choose_suit(hand.cards)
            self.on_choose_suit(new_suit)
        else:
            def on_complete():
                if not hand.any_cards:
                    self.game_over(idx+1)
                else:
                    self.action_lock = False
            top_discard = self.discard.cards[-1]
            card_ = opponent_.info.try_select_card(hand.cards, top_discard, self.chosen_suit)
            if card_ is not None:
                card_ = hand.try_grab_card(card_)[0]
                self.play_card(card_, on_complete)
            else:
                self.draw_card_from_stockpile(on_complete)

    def play_card(self, card_, on_complete=None):
        def on_card_played(holder_):
            card_ = holder_.pop_top_card()
            card_.back_up = False
            self.discard.add_card(card_, on_top=True)

            if card_.rank == 8:
                self.prompt_choose_suit()
            else:
                self.chosen_suit = None
                self.clear_dialog_title()
                self.next_turn()

            if not self.stockpile.any_cards:
                self.repopulate_stockpile(on_complete)
            else:
                if on_complete is not None: on_complete()

        self.animate_cards([card_], self.discard.next_card_pos, on_complete=on_card_played)

    def prompt_choose_suit(self):
        self.must_choose_suit = True
        if self.is_player_turn():
            self.show_choose_suit_dialog()
        else:
            self.show_dialog_title("Choosing suit...")

    def show_choose_suit_dialog(self):
        """Show dialog asking player to choose which suit they want the next
        player to have to play.
        """
        self.show_dialog_title("Please choose a suit:")
        pos = self.settings_json["gui"]["dialog"]["content"]["position"]
        button_size = self.settings_json["gui"]["dialog"]["content"]["button_size"]
        x_base = pos[0]
        y = pos[1]
        button_margin = self.settings_json["gui"]["dialog"]["content"]["button_margin"]

        def choose(new_suit):
            def on_choose():
                self.on_choose_suit(new_suit)
            return on_choose

        for i in range(0, len(suit_info)):
            button_x = x_base + (button_size[0] * i) + (button_margin * i)
            button_pos = (button_x, y)
            button_rect = [*button_pos, *button_size]
            caption = suit_info[i].symbol
            self.gui_interface.show_button(button_rect, choose(i), f"   {caption}   ",
                                            id_=f"suit_button{i}")

    def hide_choose_suit_dialog(self):
        self.clear_dialog_title()
        for i in range(0, len(suit_info)):
            self.gui_interface.hide_by_id(f"suit_button{i}")

    def on_choose_suit(self, new_suit):
        self.chosen_suit = new_suit
        self.must_choose_suit = False
        self.hide_choose_suit_dialog()
        suit = suit_info[new_suit]
        self.show_dialog_title(f"Suit is {suit.name}")
        self.next_turn()
        self.action_lock = False

    def draw_card_from_stockpile(self, on_complete=None):
        hand =\
            self.player_hand if self.is_player_turn()\
            else self.opponents[self.turn-1].hand

        def on_card_drawn(holder_):
            card_ = holder_.pop_top_card()
            card_.back_up = not self.is_player_turn()
            hand.add_card(card_, on_top=True)
            if not self.stockpile.any_cards:
                self.repopulate_stockpile(on_complete)
            else:
                if on_complete is not None: on_complete()

        card_ = self.stockpile.pop_top_card()
        self.animate_cards([card_], hand.next_card_pos, on_complete=on_card_drawn)

    def repopulate_stockpile(self, on_complete):
        self.repopulate_stockpile_card(on_complete)

    def repopulate_stockpile_card(self, on_complete):
        if len(self.discard.cards) <= 1:
            self.stockpile.shuffle()
            if on_complete is not None: on_complete()
        else:
            def on_card_move(holder_):
                card_ = holder_.pop_top_card()
                self.stockpile.add_card(card_)
                self.repopulate_stockpile_card(on_complete)

            card_ = self.discard.pop_bottom_card()
            card_.back_up = True
            self.animate_cards([card_], self.stockpile.next_card_pos, on_complete=on_card_move)

    def opponent_delay(self, on_delay_complete):
        """Simulate AI opponent waiting before making its move."""
        delay_ms = randint(self.opponent_min_delay_ms, self.opponent_max_delay_ms)
        threading.Timer(delay_ms / 1000, on_delay_complete).start()

    def game_over(self, winner_idx):
        message =\
            "You win!!" if winner_idx == 0\
            else f"{self.opponents[winner_idx-1].info.name} wins!!"
        self.show_status_notification(f"GAME OVER! {message}", color=(255,100,100))
        self.clear_dialog_title()

    def clear_opponents(self):
        for i in range(0, len(self.opponents)):
            self.opponents[i].hand.move_all_cards(self.stockpile)
            self.remove_rendered_object(self.opponents[i].hand)
            self.gui_interface.hide_by_id(f"OPPONENT_{i}_NAME")

        self.num_opponents = 0
        self.opponents = []

    def show_message(self, text, message_json, message_id, color):
        pos = message_json["position"]
        size = message_json["text_size"]
        color = color or message_json["text_color"]
        self.gui_interface.hide_by_id(message_id)
        self.gui_interface.show_label(position=pos, text=text, text_size=size,
                                      timeout=0, color=color, id_=message_id)

    def clear_status_notification(self):
        self.gui_interface.hide_by_id(STATUS_NOTIFICATION)

    def show_status_notification(self, text, color=None):
        self.show_message(text, self.settings_json["gui"]["message"], STATUS_NOTIFICATION, color)

    def clear_dialog_title(self):
        self.gui_interface.hide_by_id(DIALOG_TITLE)

    def show_dialog_title(self, text, color=None):
        self.show_message(text, self.settings_json["gui"]["dialog"]["title"], DIALOG_TITLE, color)

    def clear_player_prompt(self):
        self.gui_interface.hide_by_id(PLAYER_PROMPT)

    def show_player_prompt(self, text, color=None):
        self.show_message(text, self.settings_json["gui"]["player_prompt"], PLAYER_PROMPT, color)

    def process_mouse_event(self, pos, down, double_click):
        #print(f'process_mouse_event pos=${pos}, down=${down}, dbl-click=${double_click}')
        if down:
            self.on_player_click(pos)
        else:
            self.clear_player_prompt()

    def on_player_click(self, pos):
        if self.action_lock:
            # Some animation or other is in progress. No action allowed.
            return
        elif self.is_player_turn():
            if self.must_choose_suit:
                self.show_player_prompt("You played an 8 and must choose a suit!")
            elif self.player_hand.is_clicked(pos):
                card_clicked, _ = self.player_hand.card_at(pos)
                if card_clicked is not None:
                    if self.can_play_card(card_clicked):
                        cards = self.player_hand.try_grab_card(card_clicked)
                        self.action_lock = True
                        def on_complete():
                            if not self.player_hand.any_cards:
                                self.game_over(0)
                            else:
                                self.action_lock = False
                        self.play_card(cards[0], on_complete)
                    else:
                        self.show_player_prompt("You can't play that card.")
            elif self.stockpile.is_clicked(pos):
                self.action_lock = True
                def on_complete(): self.action_lock = False
                self.draw_card_from_stockpile(on_complete)
        else:
            self.show_player_prompt("It's not your turn!")


def main():
    # Seed random number generator.
    seed(int(round(time.time() * 1000)))

    json_path = os.path.join(os.getcwd(), 'settings.json')
    crazy8s_app = game_app.GameApp(json_path=json_path, controller_cls=Crazy8sController)
    crazy8s_app.execute()

if __name__ == '__main__':
    main()
