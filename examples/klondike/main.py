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
        self.custom_dict["deck_discard"].move_all_cards(self.custom_dict["deck"])
        self.custom_dict["stack"].move_all_cards(self.custom_dict["deck"])

        for foundation in self.custom_dict["foundations"]:
            foundation.move_all_cards(self.custom_dict["deck"])

        for pile in self.custom_dict["piles"]:
            pile.move_all_cards(self.custom_dict["deck"])

        if isinstance(self.gui_interface, game_app.GameApp.GuiInterface):
            self.gui_interface.hide_by_id("win_label1")
            self.gui_interface.hide_by_id("win_label2")
        self.start_game()

    def start_game(self):

        self.custom_dict["deck"].shuffle()
        #self.deal_cards()

        for i in range(1, 8):
            for j in range(0, i):
                card_ = self.custom_dict["deck"].pop_top_card()
                if j == i - 1:
                    card_.flip()

                self.custom_dict["piles"][i-1].add_card(card_)

        self.custom_dict["game_start_time"] = pygame.time.get_ticks()

    def build_objects(self):
        setattr(deck.Deck, "render", holders.draw_empty_card_pocket)

        deck_pos = self.settings_json["deck"]["position"]
        deck_offset = self.settings_json["deck"]["offset"]
        self.custom_dict["deck"] = deck.Deck(enums.DeckType.full, deck_pos, deck_offset, None)

        self.custom_dict["deck_discard"] = holders.DeckDiscard()

        deck_pos = self.custom_dict["deck"].pos
        x_offset = self.settings_json["stack"]["deck_offset"][0] \
                   + self.settings_json["card"]["size"][0]
        y_offset = self.settings_json["stack"]["deck_offset"][1]
        stack_pos = deck_pos[0] + x_offset, deck_pos[1] + y_offset
        stack_offset = self.settings_json["stack"]["inner_offset"]
        self.custom_dict["stack"] = card_holder.CardsHolder(stack_pos, stack_offset,
                                                            enums.GrabPolicy.can_single_grab)

        self.add_rendered_object((self.custom_dict["deck"], self.custom_dict["stack"]))

        self.custom_dict["piles"] = []
        pile_pos = self.settings_json["pile"]["position"]
        pile_offset = self.settings_json["pile"]["offset"]
        pile_inner_offset = self.settings_json["pile"]["inner_offset"]
        for i in range(1, 8):
            pile = holders.Pile(pile_pos, pile_inner_offset, enums.GrabPolicy.can_multi_grab)
            pile_pos = pile_pos[0] + pile_offset[0], pile_pos[1] + pile_offset[1]
            self.add_rendered_object(pile)
            self.custom_dict["piles"].append(pile)

        foundation_pos = self.settings_json["foundation"]["position"]
        foundation_offset = self.settings_json["foundation"]["offset"]
        foundation_inner_offset = self.settings_json["foundation"]["inner_offset"]
        self.custom_dict["foundations"] = []
        for i in range(0, 4):
            self.custom_dict["foundations"].append(holders.Foundation(foundation_pos,
                                                                      foundation_inner_offset))
            foundation_pos = (foundation_pos[0] + foundation_offset[0],
                              foundation_pos[1] + foundation_offset[1])
            self.add_rendered_object(self.custom_dict["foundations"][i])

        self.custom_dict["grabbed_cards_holder"] = holders.GrabbedCardsHolder((0, 0),
                                                                              pile_inner_offset)
        self.add_rendered_object(self.custom_dict["grabbed_cards_holder"])
        self.custom_dict["owner_of_grabbed_card"] = None

        self.gui_interface.show_button(self.settings_json["gui"]["restart_button"],
                                       self.restart_game, "Restart")

    def check_win(self):
        win = True
        for found in self.custom_dict["foundations"]:
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
        if hasattr(self, "game_start_time") and self.custom_dict["game_start_time"] is not None:
            total_seconds = (pygame.time.get_ticks() - self.custom_dict["game_start_time"])/1000
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
        if self.custom_dict["deck"].is_clicked(pos):
            self.process_deck_click()
            return

        if len(self.custom_dict["grabbed_cards_holder"].cards) == 0:
            for obj in self.rendered_objects:
                grabbed_cards = obj.try_grab_card(pos)
                if grabbed_cards is not None:
                    for card_ in grabbed_cards:
                        self.custom_dict["grabbed_cards_holder"].add_card(card_)
                    self.custom_dict["owner_of_grabbed_card"] = obj
                    break

    def process_mouse_up(self, pos):
        if len(self.custom_dict["grabbed_cards_holder"].cards) > 0:
            for obj in self.rendered_objects:
                dropped_cards = False
                if hasattr(obj, "can_drop_card") and hasattr(obj, "check_collide"):
                    if (obj.check_collide(self.custom_dict["grabbed_cards_holder"].cards[0]) and
                            obj.can_drop_card(self.custom_dict["grabbed_cards_holder"].cards[0])):
                        dropped_cards = True
                        while len(self.custom_dict["grabbed_cards_holder"].cards) != 0:
                            obj.add_card(self.custom_dict["grabbed_cards_holder"].pop_bottom_card())
                        break
            if self.custom_dict["owner_of_grabbed_card"] is not None:
                while len(self.custom_dict["grabbed_cards_holder"].cards) != 0:
                    self.custom_dict["owner_of_grabbed_card"].add_card(
                        self.custom_dict["grabbed_cards_holder"].pop_bottom_card())
                if dropped_cards:
                    if isinstance(self.custom_dict["owner_of_grabbed_card"], holders.Pile):
                        self.custom_dict["owner_of_grabbed_card"].open_top_card()
                    elif isinstance(self.custom_dict["owner_of_grabbed_card"], holders.Foundation):
                        self.check_win()
                self.custom_dict["owner_of_grabbed_card"] = None
                _ = pos

    def process_deck_click(self):
        while len(self.custom_dict["stack"].cards) != 0:
            card_ = self.custom_dict["stack"].pop_bottom_card()
            if card_ is not None:
                card_.flip()
                self.custom_dict["deck_discard"].add_card(card_)

        if len(self.custom_dict["deck"].cards) == 0:
            if len(self.custom_dict["deck_discard"].cards) == 0:
                return  # Cards in Deck ended
            else:
                self.custom_dict["deck_discard"].move_all_cards(self.custom_dict["deck"])
                return  # Not drawing cards to stack when flipped the deck

        for i in range(0, 3):
            card_ = self.custom_dict["deck"].pop_top_card()
            if card_ is None:
                break
            card_.flip()
            self.custom_dict["stack"].add_card(card_)
            _ = i

    def process_double_click(self, pos):
        search_list = self.custom_dict["piles"] + [self.custom_dict["stack"]]
        for holder in search_list:
            if len(holder.cards) != 0 and holder.is_clicked(pos):
                card_ = holder.cards[-1]
                for found in self.custom_dict["foundations"]:
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
    klondike_app = game_app.GameApp(json_path=json_path, game_controller=KlondikeController())
    klondike_app.execute()

if __name__ == '__main__':
    main()
