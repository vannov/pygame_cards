#!/usr/bin/env python
try:
    import sys
    import os
    import pygame

    from pygame_cards import game_app, controller, deck, card_holder, enums
    import holders
except ImportError as err:
    print("Fail loading a module in file:", __file__, "\n", err)
    sys.exit(2)


class KlondikeController(controller.Controller):

    def restart_game(self):
        self.deck_discard.move_all_cards(self.deck)
        self.stack.move_all_cards(self.deck)

        for foundation in self.foundations:
            foundation.move_all_cards(self.deck)

        for pile in self.piles:
            pile.move_all_cards(self.deck)

        if isinstance(self.gui_interface, game_app.GameApp.GuiInterface):
            self.gui_interface.hide_by_id("win_label1")
            self.gui_interface.hide_by_id("win_label2")
        self.start_game()

    def start_game(self):

        self.deck.shuffle()
        #self.deal_cards()

        for i in range(1, 8):
            for j in range(0, i):
                card_ = self.deck.pop_top_card()
                if j == i - 1:
                    card_.flip()

                self.piles[i-1].add_card(card_)

        self.game_start_time = pygame.time.get_ticks()

    def __init__(self, objects_list=None, gui_interface=None, settings_json=None):
        super(KlondikeController, self).__init__(objects_list, gui_interface, settings_json)

        setattr(deck.Deck, "render", holders.draw_empty_card_pocket)

        deck_pos = self.settings_json["deck"]["position"]
        deck_offset = self.settings_json["deck"]["offset"]
        self.deck = deck.Deck(enums.DeckType.full, deck_pos, deck_offset, None)

        self.deck_discard = holders.DeckDiscard()

        deck_pos = self.deck.pos
        x_offset = self.settings_json["stack"]["deck_offset"][0] \
                   + self.settings_json["card"]["size"][0]
        y_offset = self.settings_json["stack"]["deck_offset"][1]
        stack_pos = deck_pos[0] + x_offset, deck_pos[1] + y_offset
        stack_offset = self.settings_json["stack"]["inner_offset"]
        self.stack = card_holder.CardsHolder(stack_pos, stack_offset, enums.GrabPolicy.can_single_grab)

        self.add_rendered_object((self.deck, self.stack))

        self.piles = []
        pile_pos = self.settings_json["pile"]["position"]
        pile_offset = self.settings_json["pile"]["offset"]
        pile_inner_offset = self.settings_json["pile"]["inner_offset"]
        for i in range(1, 8):
            pile = holders.Pile(pile_pos, pile_inner_offset, enums.GrabPolicy.can_multi_grab)
            pile_pos = pile_pos[0] + pile_offset[0], pile_pos[1] + pile_offset[1]
            self.add_rendered_object(pile)
            self.piles.append(pile)

        foundation_pos = self.settings_json["foundation"]["position"]
        foundation_offset = self.settings_json["foundation"]["offset"]
        foundation_inner_offset = self.settings_json["foundation"]["inner_offset"]
        self.foundations = []
        for i in range(0, 4):
            self.foundations.append(holders.Foundation(foundation_pos, foundation_inner_offset))
            foundation_pos = (foundation_pos[0] + foundation_offset[0],
                              foundation_pos[1] + foundation_offset[1])
            self.add_rendered_object(self.foundations[i])

        self.grabbed_cards_holder = holders.GrabbedCardsHolder((0, 0), pile_inner_offset)
        self.add_rendered_object(self.grabbed_cards_holder)
        self.owner_of_grabbed_card = None

        self.gui_interface.show_button(self.settings_json["gui"]["restart_button"],
                                       self.restart_game, "Restart")

        self.game_start_time = None

    def check_win(self):
        win = True
        for found in self.foundations:
            if len(found.cards) > 0 and found.cards[-1].rank == enums.Rank.king:
                continue
            else:
                win = False
                break
        if win:
            self.show_win_ui()

    def show_win_ui(self):
        text = "You won, congrats!"
        pos = self.settings_json["gui"]["win_label"]
        size = self.settings_json["gui"]["win_text_size"]
        self.gui_interface.show_label(position=pos, text=text, text_size=size, timeout=0,
                                      id_="win_label1")
        if self.game_start_time is not None:
            total_seconds = (pygame.time.get_ticks() - self.game_start_time)/1000
            minutes = str(total_seconds / 60)
            seconds = str(total_seconds % 60)
            if len(seconds) == 1:
                seconds = "0" + seconds
            game_time = str(minutes) + ":" + str(seconds)
            text = "Game time: " + str(game_time)
            pos = pos[0], pos[1] + size
            self.gui_interface.show_label(position=pos, text=text, text_size=size, timeout=0,
                                          id_="win_label2")

    def execute_game(self):
        pass

    def process_mouse_event(self, pos, down, double_click=False):
        if down:
            self.process_mouse_down(pos)
        else:
            self.process_mouse_up(pos)
        if double_click:
            self.process_double_click(pos)

    def process_mouse_down(self, pos):
        if self.deck.is_clicked(pos):
            self.process_deck_click()
            return

        if len(self.grabbed_cards_holder.cards) == 0:
            for obj in self.rendered_objects:
                grabbed_cards = obj.try_grab_card(pos)
                if grabbed_cards is not None:
                    for card_ in grabbed_cards:
                        self.grabbed_cards_holder.add_card(card_)
                    self.owner_of_grabbed_card = obj
                    break

    def process_mouse_up(self, pos):
        if len(self.grabbed_cards_holder.cards) > 0:
            for obj in self.rendered_objects:
                dropped_cards = False
                if hasattr(obj, "can_drop_card") and hasattr(obj, "check_collide"):
                    if (obj.check_collide(self.grabbed_cards_holder.cards[0]) and
                            obj.can_drop_card(self.grabbed_cards_holder.cards[0])):
                        dropped_cards = True
                        while len(self.grabbed_cards_holder.cards) != 0:
                            obj.add_card(self.grabbed_cards_holder.pop_bottom_card())
                        break
            if self.owner_of_grabbed_card is not None:
                while len(self.grabbed_cards_holder.cards) != 0:
                    self.owner_of_grabbed_card.add_card(
                        self.grabbed_cards_holder.pop_bottom_card())
                if dropped_cards:
                    if isinstance(self.owner_of_grabbed_card, holders.Pile):
                        self.owner_of_grabbed_card.open_top_card()
                    elif isinstance(self.owner_of_grabbed_card, holders.Foundation):
                        self.check_win()
                self.owner_of_grabbed_card = None
                _ = pos

    def process_deck_click(self):
        while len(self.stack.cards) != 0:
            card_ = self.stack.pop_bottom_card()
            if card_ is not None:
                card_.flip()
                self.deck_discard.add_card(card_)

        if len(self.deck.cards) == 0:
            if len(self.deck_discard.cards) == 0:
                return  # Cards in Deck ended
            else:
                self.deck_discard.move_all_cards(self.deck)
                return  # Not drawing cards to stack when flipped the deck

        for i in range(0, 3):
            card_ = self.deck.pop_top_card()
            if card_ is None:
                break
            card_.flip()
            self.stack.add_card(card_)
            _ = i

    def process_double_click(self, pos):
        search_list = self.piles + [self.stack]
        for holder in search_list:
            if holder.is_top_card_clicked(pos):
                card_ = holder.cards[-1]
                for found in self.foundations:
                    if found.can_drop_card(card_):
                        card_ = holder.pop_top_card()
                        self.add_move([card_], found.pos)  # animate card move to foundation
                        found.add_card(card_)
                        self.check_win()
                        if isinstance(holder, holders.Pile):
                            holder.open_top_card()
                        break
                break


def main():
    json_path = os.path.join(os.getcwd(), 'settings.json')
    klondike_app = game_app.GameApp(json_path=json_path, controller_cls=KlondikeController)
    klondike_app.execute()

if __name__ == '__main__':
    main()
