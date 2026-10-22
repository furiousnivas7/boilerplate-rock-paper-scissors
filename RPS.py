"""Stateful player tuned to the four freeCodeCamp challenge bots."""
from collections import Counter

_BEATS = {"R": "P", "P": "S", "S": "R"}
_MOVES = ("R", "P", "S")
_our_moves = []
_bot_inputs = []
_abbey_inputs = []
_scores = Counter()
_last_predictions = {}


def _beat(move):
    return _BEATS[move]


def _sequence_guess(history):
    """Predict the next symbol using the longest repeated suffix."""
    n = len(history)
    for width in range(min(12, n // 2), 0, -1):
        suffix = history[-width:]
        following = Counter(
            history[i + width]
            for i in range(n - width)
            if history[i:i + width] == suffix
        )
        if following:
            return following.most_common(1)[0][0]
    return Counter(history).most_common(1)[0][0] if history else "R"


def _abbey_response(inputs):
    """Reproduce Abbey's transition table and return her next response."""
    history = []
    order = {a + b: 0 for a in _MOVES for b in _MOVES}
    for move in inputs:
        move = move or "R"
        history.append(move)
        if len(history) >= 2:
            order["".join(history[-2:])] += 1

    previous = history[-1]
    options = (previous + "R", previous + "P", previous + "S")
    predicted = max(options, key=lambda pair: order[pair])[-1]
    return _beat(predicted)


def _mrugesh_response(inputs):
    """Reproduce Mrugesh's most-common-of-the-last-ten response."""
    recent = inputs[-10:]
    most_frequent = max(set(recent), key=recent.count)
    if most_frequent == "":
        most_frequent = "S"
    return _beat(most_frequent)


def player(prev_play, opponent_history=[]):
    """Return the move that beats the best prediction of the opponent."""
    global _last_predictions

    # A blank previous move marks a new match, so relearn the current bot.
    if prev_play == "":
        _scores.clear()
        _last_predictions = {}
        _our_moves.clear()
        _bot_inputs.clear()
        _abbey_inputs.clear()
        opponent_history.clear()

    # Score last round's forecasts when the new opponent move is revealed.
    if prev_play in _MOVES:
        opponent_history.append(prev_play)
        for name, guess in _last_predictions.items():
            _scores[name] += guess == prev_play

    # These bots see our previous move. Their default state persists across
    # matches, while each new match supplies an empty previous move.
    own_previous = "" if prev_play == "" else (_our_moves[-1] if _our_moves else "")
    _bot_inputs.append(own_previous)
    _abbey_inputs.append(own_previous or "R")

    predictions = {
        "quincy": _sequence_guess(opponent_history),
        "kris": _beat(own_previous or "R"),
        "mrugesh": _mrugesh_response(_bot_inputs),
        "abbey": _abbey_response(_abbey_inputs),
    }

    # Trust the bot model that has forecast the most observed moves correctly.
    # Stable tie order is useful in the opening rounds before evidence builds.
    priority = ("quincy", "abbey", "kris", "mrugesh")
    selected = max(priority, key=lambda name: _scores[name])
    move = _beat(predictions[selected])

    _last_predictions = predictions
    _our_moves.append(move)
    return move
