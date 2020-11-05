#!/usr/bin/env python
try:
    import sys
    import os
    import threading
    import time
    from random import seed, randint
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
    import pygame

    from pygame_cards import game_app, controller, deck, card_holder, enums, animation
except ImportError as err:
    print("Fail loading a module in file:", __file__, "\n", err)
    sys.exit(2)


# Constants
MESSAGE_ID = "screen_message"


class GameState:
    """List of possible states for the war game to be in."""
    paused = 0,     # Game not in progress.
    next_card = 1,  # Time for players to play their next card.
    evaluate = 2,   # Cards have been placed; time to compare them.
    war = 3,        # War in progress.
    game_over = 4   # Someone has won.


class WarController(controller.Controller):
    def __init__(self, objects_list=None, gui_interface=None, settings_json=None):
        super(WarController, self).__init__(objects_list, gui_interface, settings_json)

        self.state = GameState.paused

        # Set up the player's deck.
        pos = self.settings_json["player_deck"]["position"]
        offset = self.settings_json["player_deck"]["offset"]
        self.player_deck = card_holder.CardsHolder(pos, offset)
        self.add_rendered_object(self.player_deck)

        # Set up the AI opponent's deck.
        pos = self.settings_json["ai_deck"]["position"]
        offset = self.settings_json["ai_deck"]["offset"]
        self.ai_deck = card_holder.CardsHolder(pos, offset)
        self.add_rendered_object(self.ai_deck)

        # Set up the player's stage.
        pos = self.settings_json["player_stage"]["position"]
        offset = self.settings_json["player_stage"]["offset"]
        self.player_stage = card_holder.CardsHolder(pos, offset)
        self.add_rendered_object(self.player_stage)

        # Set up the API opponent's stage.
        pos = self.settings_json["ai_stage"]["position"]
        offset = self.settings_json["ai_stage"]["offset"]
        self.ai_stage = card_holder.CardsHolder(pos, offset)
        self.add_rendered_object(self.ai_stage)

        # Starter deck (for restarting the game; not shown on screen.)
        self.start_deck = deck.Deck(enums.DeckType.full, (0, 0), (0, 0), None)

        # Other game properties
        self.evaluate_delay_ms = self.settings_json["game_behavior"]["evaluate_delay_ms"]
        self.ai_min_delay_ms = self.settings_json["ai_behavior"]["min_delay_ms"]
        self.ai_max_delay_ms = self.settings_json["ai_behavior"]["max_delay_ms"]

        # UI
        self.gui_interface.show_button(self.settings_json["gui"]["restart_button"],
                                       self.restart_game, "Restart")

    def restart_game(self):
        for animation_ in self.animations:
            animation_.is_completed = True
        self.player_deck.move_all_cards(self.start_deck)
        self.ai_deck.move_all_cards(self.start_deck)
        self.player_stage.move_all_cards(self.start_deck)
        self.ai_stage.move_all_cards(self.start_deck)
        self.start_game()
    
    def start_game(self):
        self.start_deck.shuffle()

        # Split the deck between the players.
        while len(self.start_deck.cards) > 0:
            # Deal card to opponent.
            card_ = self.start_deck.pop_top_card()
            self.ai_deck.add_card(card_)

            # Deal card to player.
            card_ = self.start_deck.pop_top_card()
            self.player_deck.add_card(card_)

        # Reset game state.
        self.state = GameState.next_card
        self.player_locked = False
        self.ai_locked = False
        self.awaiting_card_transfers = 0
        self.player_war_buildup = 0
        self.ai_war_buildup = 0
        self.bg_pulse_animation = None

        # Reset UI
        self.clear_message()

    def execute_game(self):
        if self.state == GameState.next_card:
            if self.cards_played():
                self.evaluate_match()
            elif self.anyone_out_of_cards():
                self.end_game()
        elif self.state == GameState.war:
            if self.cards_played() and self.player_war_buildup >= 3 and self.ai_war_buildup >= 3:
                self.stop_war()
                self.evaluate_match()
            elif self.anyone_out_of_cards():
                self.stop_war()
                self.end_game()
        self.ai_execute()

    def evaluate_match(self):
        """Evaluate the current cards placed down; see who wins or if it's a war."""
        self.state = GameState.evaluate
        player_card = self.player_stage.cards[-1]
        ai_card = self.ai_stage.cards[-1]
        if player_card.rank == ai_card.rank:
            # Matching ranks. It's WAR!!!
            self.start_war()
        elif player_card.rank > ai_card.rank:
            # Player wins the round.
            self.on_player_wins()
        else:
            # AI opponent wins the round.
            self.on_ai_wins()

    def start_war(self):
        """Begin a state of war."""
        self.state = GameState.war
        self.player_war_buildup = 0
        self.ai_war_buildup = 0

        # Start background color pulse.
        self.bg_pulse_animation = self.create_bgcolor_pulse_animation()
        self.add_animation(self.bg_pulse_animation)
        self.show_message("WAR!!!")

    def create_bgcolor_pulse_animation(self):
        """Set up animation to pulse the background with war colors.
        """
        color1 = self.settings_json["gui"]["war_background"]["color1"]
        color2 = self.settings_json["gui"]["war_background"]["color2"]
        period_ms = self.settings_json["gui"]["war_background"]["period_ms"]

        def set_color(color):
            self.background_color = color

        def on_complete():
            self.background_color = None

        return animation.ColorPulseAnimation(color1, color2, period_ms, set_color, on_complete)

    def stop_war(self):
        self.clear_message()
        self.bg_pulse_animation.is_completed = True

    def on_player_wins(self):
        """Finish the round in the player's favor."""
        def act():
            self.send_staged_cards_to_player()

        threading.Timer(self.evaluate_delay_ms / 1000, act).start()

    def on_ai_wins(self):
        """Finish the round in the AI opponent's favor."""
        def act():
            self.send_staged_cards_to_ai()

        threading.Timer(self.evaluate_delay_ms / 1000, act).start()

    def send_staged_cards_to_deck(self, deck_):
        """Send all the cards in center stage to someone's deck."""
        self.awaiting_card_transfers = 2

        def drop_card(holder_):
            for card_ in holder_.cards:
                card_.back_up = True
                deck_.add_card(card_, on_top=False)
            self.awaiting_card_transfers = self.awaiting_card_transfers - 1
            if self.awaiting_card_transfers == 0:
                self.state = GameState.next_card

        # Animate player stage cards towards deck.
        cards = self.player_stage.pop_all_cards()
        self.animate_cards(cards, deck_.next_card_pos, \
            on_complete=drop_card)

        # Animate AI opponent stage cards towards deck.
        cards = self.ai_stage.pop_all_cards()
        self.animate_cards(cards, deck_.next_card_pos, \
            on_complete=drop_card)

    def send_staged_cards_to_player(self):
        """Send all the cards in center stage to player's deck."""
        self.send_staged_cards_to_deck(self.player_deck)

    def send_staged_cards_to_ai(self):
        """Send all the cards in center stage to AI opponent's deck."""
        self.send_staged_cards_to_deck(self.ai_deck)

    def player_played(self):
        """Has the player played an open card?"""
        return self.player_stage.any_cards and not self.player_stage.cards[-1].back_up

    def ai_played(self):
        """Has the opponent AI played an open card?"""
        return self.ai_stage.any_cards and not self.ai_stage.cards[-1].back_up

    def cards_played(self):
        """Have both player and opponent played an open card?"""
        return self.player_played() and self.ai_played()
    
    def anyone_out_of_cards(self):
        return not self.player_deck.any_cards or not self.ai_deck.any_cards

    def process_mouse_event(self, pos, down, double_click):
        #print(f'process_mouse_event pos=${pos}, down=${down}, dbl-click=${double_click}')
        if down and self.player_deck.is_clicked(pos):
            self.on_player_deck_clicked()

    def on_player_deck_clicked(self):
        if self.player_deck.any_cards:
            if self.state == GameState.war and self.player_war_buildup < 3:
                self.player_play(back_up=True)
            elif self.state in {GameState.next_card, GameState.war} and not self.player_played():
                self.player_play(back_up=False)

    def player_play(self, back_up):
        """Player to deal card from their deck to their stage."""
        if not self.player_locked and self.player_deck.any_cards:
            def drop_card(holder_):
                card_ = holder_.pop_top_card()
                card_.back_up = back_up
                self.player_stage.add_card(card_)
                if back_up:
                    self.player_war_buildup += 1
                self.player_locked = False

            self.player_locked = True
            card_ = self.player_deck.pop_top_card()
            self.animate_cards([card_], self.player_stage.next_card_pos, \
                on_complete=drop_card)

    def ai_execute(self):
        """Have the AI opponent act if it can."""
        if not self.ai_locked:
            if self.state == GameState.war and self.ai_war_buildup < 3:
                self.ai_locked = True
                self.ai_delay(self.get_ai_play(back_up=True))
            elif self.state in {GameState.next_card, GameState.war} and not self.ai_played():
                self.ai_locked = True
                self.ai_delay(self.get_ai_play(back_up=False))

    def ai_delay(self, on_delay_complete):
        """Simulate AI opponent waiting before making its move."""
        delay_ms = randint(self.ai_min_delay_ms, self.ai_max_delay_ms)
        if self.state == GameState.war:
            delay_ms /= 2
        threading.Timer(delay_ms / 1000, on_delay_complete).start()

    def get_ai_play(self, back_up):
        """Function generator: returns function for AI opponent to deal card
        from their deck to their stage.
        """
        def drop_card(holder_):
            card_ = holder_.pop_top_card()
            card_.back_up = back_up
            self.ai_stage.add_card(card_)
            if back_up:
                self.ai_war_buildup += 1
            self.ai_locked = False

        def play():
            if self.ai_deck.any_cards:
                card_ = self.ai_deck.pop_top_card()
                self.animate_cards([card_], self.ai_stage.next_card_pos, \
                    on_complete=drop_card)
            else:
                self.ai_locked = False

        return play

    def end_game(self):
        self.state = GameState.game_over
        if not self.player_deck.any_cards:
            self.show_message("Opponent wins!")
        else:
            self.show_message("You win!")

    def clear_message(self):
        self.gui_interface.hide_by_id(MESSAGE_ID)

    def show_message(self, text, color=None):
        pos = self.settings_json["gui"]["message"]["pos"]
        size = self.settings_json["gui"]["message"]["text_size"]
        color = color or self.settings_json["gui"]["message"]["text_color"]
        self.clear_message()
        self.gui_interface.show_label(position=pos, text=text, text_size=size,
                                      timeout=0, color=color, id_=MESSAGE_ID)

def main():
    # Seed random number generator.
    seed(int(round(time.time() * 1000)))

    json_path = os.path.join(os.getcwd(), 'settings.json')
    war_app = game_app.GameApp(json_path=json_path, controller_cls=WarController)
    war_app.execute()

if __name__ == '__main__':
    main()
