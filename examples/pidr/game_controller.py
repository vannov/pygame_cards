#!/usr/bin/env python
try:
    import sys
    import time

    import pidr_enums
    import logic
    from pygame_cards import globals, enums, card_sprite
    from pygame_cards import card
    import player, heap

except ImportError as err:
    print "Fail loading a module: ", err
    sys.exit(2)


class AbstractGameController:
    def __init__(self, players, deck, gui_interface):
        self.phase = pidr_enums.GamePhase.dealing
        self.players = players
        self.active_player_index = 3
        self.deck = deck
        self.heap = None        # heap for playing game phase
        self.started = False
        self.active_played_got_card_from_deck = False
        self.gui_interface = gui_interface

    def start(self):
        pass

    def process_logic(self):
        if self.players[self.active_player_index].human:
            pass
        else:
            self.process_bots()

    # abstact method, have to be redefined in each derived class
    def process_bots(self):
        pass

    def render_objects(self, screen):
        pass


class PidrGameController(AbstractGameController):
    # class static list of moves for all players objects
    moves = []

    def __init__(self, players, deck, gui_interface):
        AbstractGameController.__init__(self, players, deck, gui_interface)
        self.deck.shuffle()
        self.trump_suit = None
        self.logic = None
        #TODO: show and hide 'End Stroke' button only when relevant (current player move)
        self.gui_interface.show_button('End Stroke', self.end_stroke_clicked)

    def start(self):
        self.started = True
        self.deal_cards()

    def execute_game(self):
        if not self.started:
            self.start()

        if self.phase == pidr_enums.GamePhase.dealing:
            if len(self.deck.cards) == 0:
                self.switch_game_phase()

        # Non-bot player action is handled by process_mouse_event()
        if self.players[self.active_player_index].bot:
            self.run_bot_action(self.players[self.active_player_index])

    def switch_game_phase(self):
        self.phase = pidr_enums.GamePhase.playing
        self.logic = logic.PlayingLogic(self.trump_suit)
        self.heap = heap.Heap(self.deck.pos)
        min_trump_card_rank = enums.Rank.ace
        first_player_index = 0
        for player in self.players:
            # if player.bot:
            #     player.flip_cards()
            player.sort_cards()
            player.reset_cards_pos()
            trump_card = next((card for card in player.cards if card.suit is self.trump_suit), None)
            if trump_card is not None:
                print("player: " + str(player.name) + " card: " + str(trump_card.rank))
                if trump_card.rank <= min_trump_card_rank:
                    min_trump_card_rank = trump_card.rank
                    first_player_index = self.players.index(player)
        print("first player index: " + str(first_player_index) + " with card: " + str(min_trump_card_rank))
        #self.force_player_to_start(first_player_index, min_trump_card_rank)
        player = self.players[first_player_index]
        if player.bot:
            self.run_bot_action(player)
        else:
            #TODO: prompt user move
            pass

    def deck_last_card_callback(self, lcard):
        if isinstance(lcard, card.Card):
            self.trump_suit = lcard.suit
            print("deck_last_card_callback() - trump suit is: " + str(self.trump_suit))
            self.gui_interface.show_label("Trump suit is: " + enums.get_suit_string_from_enum(self.trump_suit))
        else:
            print("deck_last_card_callback() - invalid argument")

    def run_bot_action(self, p):
        if self.phase is pidr_enums.GamePhase.dealing:
            # TODO: implement check of current top card and possible card drop locations !!!
            lcard = self.deck.pop_top_card()
            if isinstance(lcard, card.Card):
                self.player_add_card(p, lcard, pidr_enums.PidrCardType.open, True)
                self.change_turn()
        elif self.phase is pidr_enums.GamePhase.playing:
            heap_top_card = None
            if len(self.heap.cards) > 0:
                heap_top_card = self.heap.cards[-1]
            lcard = self.logic.choose_card_to_move(heap_top_card, p.cards)
            if lcard is None:
                # grab lowest card from heap
                self.player_add_card(p, self.heap.remove_card())
                pass
            else:
                p.remove_card(lcard)
                self.heap_add_card(lcard, p.name)
            self.change_turn()

    def change_turn(self):
        self.active_played_got_card_from_deck = False
        if self.active_player_index == len(self.players) - 1:
            self.active_player_index = 0
        else:
            self.active_player_index += 1

    def deal_cards(self):
        # Deal talons
        for x in range(0, 2):
            for p in self.players:
                time.sleep(0.2)
                self.player_add_card(p, self.deck.pop_top_card(), pidr_enums.PidrCardType.talon)

        # Deal initial open card
        for p in self.players:
            time.sleep(0.2)
            self.player_add_card(p, self.deck.pop_top_card(), pidr_enums.PidrCardType.open)

    def player_add_card(self, player_, card_, card_type=pidr_enums.PidrCardType.open, move=True):
        if move:
            PidrGameController.moves.append(card_sprite.SpriteMove([card_.sprite], player_.calc_card_pos(card_type)))
        player_.add_card(card_, card_type, move)

    def heap_add_card(self, card_, player_name, move=True):
        if move:
            PidrGameController.moves.append(card_sprite.SpriteMove([card_.sprite], self.heap.calc_card_pos(player_name)))
        self.heap.add_card(card_, player_name, move)
        if len(self.heap.cards) == len(self.players):
            time.sleep(1)
            sprites = []
            for i in range(4):
                c = self.heap.cards.pop()
                #c.flip()
                sprites.append(c.sprite)
                PidrGameController.moves.append(
                    card_sprite.SpriteMove(sprites,
                                           (0 - globals.settings_json["card"]["size"][0], 0 - globals.settings_json["card"]["size"][1]),
                                           speed=150))

    def process_card_drop(self, pos):
        #TODO: check if has to move current top card
        if self.deck.grabbed_card:
            grabbed_card = self.deck.cards[-1]
            cards_holder = self.deck
        elif self.players[self.active_player_index].grabbed_card:
            grabbed_card = self.players[self.active_player_index].cards[-1]
            cards_holder = self.players[self.active_player_index]
        else:
            return
        for p in self.players:
            if len(p.cards) > 0 and \
                    p.cards[-1].check_collide(grabbed_card) and \
                    logic.DealingLogic.can_drop_card(deck_type=self.deck.type,
                                                     card=grabbed_card,
                                                     player=p,
                                                     players_list=self.players,
                                                     active_index=self.active_player_index):
                lcard = cards_holder.drop_card()
                lcard.check_mouse(pos, False)
                self.player_add_card(p, lcard, pidr_enums.PidrCardType.open, move=False)
                if p.name == self.players[self.active_player_index].name and \
                        not logic.DealingLogic.is_drop_ranks_match(self.deck.type, p.cards[-1].rank, p.cards[-2].rank):
                    self.active_played_got_card_from_deck = True
                    self.change_turn()
                break

    def process_card_grab(self, pos):
        if self.phase is pidr_enums.GamePhase.dealing:
            return self.deck.check_grab(pos) or \
                    self.players[self.active_player_index].check_grab(pos)
        elif self.phase is pidr_enums.GamePhase.playing:
            return self.check_card_selection(pos)

    def check_card_selection(self, pos):
        selected_card = None
        for card_ in self.players[self.active_player_index].cards:
            if card_.check_mouse(pos, down=False):
                selected_card = card_
                # do not break here because cards can be overlapped, should select the top of the overlapped cards
        heap_top_card = None
        if len(self.heap.cards) > 0:
            heap_top_card = self.heap.cards[-1]
        if selected_card is not None and self.logic.is_card_match_heap(heap_top_card, selected_card):
            self.players[self.active_player_index].remove_card(selected_card)
            self.heap_add_card(selected_card, self.players[self.active_player_index].name, True)
            self.change_turn()

    def render_objects(self, screen):
        for p in self.players:
            p.render(screen)

        if self.phase is pidr_enums.GamePhase.dealing:
            self.deck.render(screen)
        elif self.phase is pidr_enums.GamePhase.playing:
            self.heap.render(screen)
        if len(PidrGameController.moves) > 0:
            PidrGameController.moves[0].update()
            if PidrGameController.moves[0].is_completed():
                PidrGameController.moves.pop(0)

    def process_mouse_event(self, pos, down):
        if len(PidrGameController.moves) > 0:
            pass
        else:
            if down and not self.players[self.active_player_index].bot:
                if self.deck.grabbed_card or self.players[self.active_player_index].grabbed_card:
                    self.process_card_drop(pos)
                else:
                    self.process_card_grab(pos)

    def end_stroke_clicked(self):
        if not self.players[self.active_player_index].bot:
            if self.active_played_got_card_from_deck and \
                    not logic.DealingLogic.need_to_move_self_card(self.players, self.active_player_index, self.deck.type):
                self.change_turn()
            else:
                self.penalty()

    def check_players_stroke_complete(self):
        return True

    def penalty(self):
        pass