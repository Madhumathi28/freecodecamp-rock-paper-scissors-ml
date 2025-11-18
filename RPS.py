import random

def player(prev_play, opponent_history=None):
    """
    Rock-Paper-Scissors player for freeCodeCamp ML project.

    - Uses internal state stored at player.st (initialized on first call).
    - Resets state when prev_play == "" (start of a new match).
    - Combines n-gram (3 and 2) predictors, pattern detection (quincy),
      heuristics for kris/abbey, and a frequency fallback.
    - Returns "R", "P", or "S".
    """

    # Helper: what beats what
    beats = {"R": "P", "P": "S", "S": "R"}

    # Initialize persistent state on the function object (once)
    if not hasattr(player, "st") or player.st is None:
        player.st = {
            "my": [],
            "opp": [],
            "pair_counts": {k: 0 for k in ["RR","RP","RS","PR","PP","PS","SR","SP","SS"]},
            "opp_ng2": {k: {"R":0,"P":0,"S":0} for k in ["RR","RP","RS","PR","PP","PS","SR","SP","SS"]},
            "opp_ng3": {},  # mapping of 3-char context -> counts of next moves
            "scores": {"ng2":0, "ng3":0, "quincy":0, "kris":0, "abbey":0},
            "last_recs": {}
        }

    st = player.st  # local ref

    # New match init: freeCodeCamp signals start of a match with prev_play == ""
    if prev_play == "":
        # Reset histories and counters
        st["my"] = []
        st["opp"] = []
        for k in st["pair_counts"].keys():
            st["pair_counts"][k] = 0
        for k in st["opp_ng2"].keys():
            st["opp_ng2"][k] = {"R":0,"P":0,"S":0}
        st["opp_ng3"] = {}
        st["scores"] = {"ng2":0, "ng3":0, "quincy":0, "kris":0, "abbey":0}
        st["last_recs"] = {}
        # For the very first move, play a deterministic opening (helps some bots)
        return "R"

    # Append opponent's last move to history
    st["opp"].append(prev_play)

    # Evaluate how previous recommendations fared against the actual prev_play
    # last_recs maps predictor name -> recommended move for previous round
    for name, rec in st["last_recs"].items():
        if rec is None:
            continue
        # If recommended move would have been beaten by opponent's actual prev_play, penalize
        if beats[rec] == prev_play:
            st["scores"][name] -= 1
        # If recommended move would have beaten the actual prev_play, reward
        elif beats[prev_play] == rec:
            st["scores"][name] += 1

    # Update n-gram models using the opponent history
    # Update opp_ng2: context of length 2 -> next move counts
    if len(st["opp"]) >= 3:
        ctx2 = st["opp"][-3] + st["opp"][-2]   # previous two moves as context
        next_move = st["opp"][-1]
        if ctx2 in st["opp_ng2"]:
            st["opp_ng2"][ctx2][next_move] += 1

    # Update opp_ng3: context of length 3 -> next move counts
    if len(st["opp"]) >= 4:
        ctx3 = "".join(st["opp"][-4:-1])  # last three moves (positions -4,-3,-2) predicting -1
        next_move = st["opp"][-1]
        st["opp_ng3"].setdefault(ctx3, {"R":0,"P":0,"S":0})
        st["opp_ng3"][ctx3][next_move] += 1

    # Update pair_counts of our moves -> used to approximate abbey behavior
    if st["my"]:
        pair = st["my"][-1] + prev_play
        if pair in st["pair_counts"]:
            st["pair_counts"][pair] += 1

    # Build recommendations from different predictors (recommendation = our move)
    recs = {"ng3": None, "ng2": None, "quincy": None, "kris": None, "abbey": None}

    # Predictor: ng3 (predict opponent next using last 3-opponent moves)
    if len(st["opp"]) >= 3:
        ctx3 = "".join(st["opp"][-3:])
        counts = st["opp_ng3"].get(ctx3)
        if counts and sum(counts.values()) > 0:
            pred = max(counts, key=counts.get)
            recs["ng3"] = beats[pred]

    # Predictor: ng2 (predict opponent next using last 2-opponent moves)
    if len(st["opp"]) >= 2:
        ctx2 = "".join(st["opp"][-2:])
        counts2 = st["opp_ng2"].get(ctx2)
        if counts2 and sum(counts2.values()) > 0:
            pred2 = max(counts2, key=counts2.get)
            recs["ng2"] = beats[pred2]

    # Predictor: quincy (pattern detector: repeating R R P P S ...)
    # If the opponent aligns strongly to the repeating pattern, predict next
    if len(st["opp"]) >= 10:
        pattern = ["R","R","P","P","S"]  # known pattern of Quincy-like bot
        best_align = 0
        best_o = 0
        # try offsets 0..4 for best alignment over last 10 moves
        for o in range(5):
            m = sum(1 for i in range(10) if st["opp"][-10+i] == pattern[(o+i) % 5])
            if m > best_align:
                best_align, best_o = m, o
        # If alignment is high, predict next element in pattern
        if best_align >= 8:
            idx = (best_o + len(st["opp"])) % 5
            recs["quincy"] = beats[pattern[idx]]

    # Predictor: kris (assumes opponent counters our last move)
    # If opponent tends to counter our last move, they play beats[my_last]; so we should play beats[beats[my_last]]
    if st["my"]:
        recs["kris"] = beats[beats[st["my"][-1]]]

    # Predictor: abbey (tries to anticipate what we will play based on pair counts)
    if st["my"]:
        last_my = st["my"][-1]
        options = [last_my + "R", last_my + "P", last_my + "S"]
        sub = {opt: st["pair_counts"].get(opt, 0) for opt in options}
        if sum(sub.values()) > 0:
            # predicted_our is the move we are likely to play next (according to pair_counts)
            predicted_our = max(sub, key=sub.get)[-1]
            # abbey would play the counter to predicted_our, so we play the counter to that
            recs["abbey"] = beats[beats[predicted_our]]

    # Choose the recommendation from the predictor with best score so far
    best_name = None
    best_score = -10**9
    for name, move in recs.items():
        if move is None:
            continue
        score = st["scores"].get(name, 0)
        if score > best_score:
            best_score = score
            best_name = name

    # Fallback: frequency of recent opponent moves (last 20)
    if best_name is None:
        window = st["opp"][-20:]
        if window:
            freq = {"R": window.count("R"), "P": window.count("P"), "S": window.count("S")}
            guess = max(freq, key=freq.get)
        else:
            guess = "R"
        move = beats[guess]
    else:
        move = recs[best_name]

    # Save last recommendations for scoring in the next round
    st["last_recs"] = recs

    # Record our chosen move
    st["my"].append(move)

    return move
