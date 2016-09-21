#!/bin/sh

rm -rf pylint_reports
mkdir pylint_reports
pylint -f html pygame_cards/pygame_cards > pylint_reports/pygame_cards.html
pylint -f html examples/klondike > pylint_reports/klondike.html
pylint -f html examples/template > pylint_reports/template.html