import random

def player(prev_play, opponent_history=[], st={
    "my": [],
    "opp": [],
    "pair_counts": {k: 0 for k in ["RR","RP","RS","PR","PP","PS","SR","SP","SS"]},
    "opp_ng2": {k: {"R":0,"P":0,"S":0} for k in ["RR","RP","RS","PR","PP","PS","SR","SP","SS"]},
    "opp_ng3": {},
    "scores": {"ng2":0, "ng3":0, "quincy":0, "kris":0, "abbey":0},
    "last_recs": {}
}):
    beats = {"R":"P","P":"S","S":"R"}

    # New match init
    if prev_play == "":
        opponent_history.clear()
        st["my"] = []
        st["opp"] = []
        for k in st["pair_counts"].keys():
            st["pair_counts"][k] = 0
        for k in st["opp_ng2"].keys():
            st["opp_ng2"][k] = {"R":0,"P":0,"S":0}
        st["opp_ng3"] = {}
        st["scores"] = {"ng2":0, "ng3":0, "quincy":0, "kris":0, "abbey":0}
        st["last_recs"] = {}
        return "R"

    # Update histories
    opponent_history.append(prev_play)
    st["opp"].append(prev_play)

    # Score previous recommendations against actual prev_play
    for name, rec in st["last_recs"].items():
        if rec is None:
            continue
        if beats[rec] == prev_play:
            st["scores"][name] -= 1
        elif beats[prev_play] == rec:
            st["scores"][name] += 1

    # Update opponent n-gram models with new prev_play
    if len(st["opp"]) >= 2:
        key2 = st["opp"][-2] + st["opp"][ -1]
        # Increment when we have at least 3 moves (context -> next). Use previous context and current prev_play
        if len(st["opp"]) >= 3:
            ctx2 = st["opp"][-3] + st["opp"][-2]
            st["opp_ng2"][ctx2][st["opp"][-1]] += 1
    if len(st["opp"]) >= 4:
        ctx3 = "".join(st["opp"][-4:-1])
        nextm = st["opp"][-1]
        st["opp_ng3"].setdefault(ctx3, {"R":0,"P":0,"S":0})
        st["opp_ng3"][ctx3][nextm] += 1

    # Build predictions (return our recommended move for each predictor)
    recs = {}
    # ng3
    if len(st["opp"]) >= 3:
        ctx3 = "".join(st["opp"][-3:])  # last three as context for predicting next
        counts = st["opp_ng3"].get(ctx3, None)
        if counts and sum(counts.values())>0:
            pred = max(counts, key=counts.get)
            recs["ng3"] = beats[pred]
        else:
            recs["ng3"] = None
    else:
        recs["ng3"] = None
    # ng2
    if len(st["opp"]) >= 2:
        ctx2 = "".join(st["opp"][-2:])
        counts2 = st["opp_ng2"].get(ctx2, None)
        if counts2 and sum(counts2.values())>0:
            pred2 = max(counts2, key=counts2.get)
            recs["ng2"] = beats[pred2]
        else:
            recs["ng2"] = None
    else:
        recs["ng2"] = None
    # quincy
    if len(st["opp"]) >= 10:
        pattern = ["R","R","P","P","S"]
        best_align=0; best_o=0
        for o in range(5):
            m = sum(1 for i in range(10) if st["opp"][-10+i]==pattern[(o+i)%5])
            if m>best_align: best_align, best_o = m, o
        if best_align>=8:
            idx=(best_o+len(st["opp"]))%5
            recs["quincy"] = beats[pattern[idx]]
        else:
            recs["quincy"] = None
    else:
        recs["quincy"] = None
    # kris (opponent plays counter to our last)
    if st["my"]:
        recs["kris"] = beats[beats[st["my"][-1]]]
    else:
        recs["kris"] = None
    # abbey simulation based on our pair counts
    if st["my"]:
        last_my = st["my"][-1]
        options = [last_my+"R", last_my+"P", last_my+"S"]
        sub = {opt: st["pair_counts"].get(opt,0) for opt in options}
        if sum(sub.values())>0:
            predicted_our = max(sub, key=sub.get)[-1]
            recs["abbey"] = beats[beats[predicted_our]]
        else:
            recs["abbey"] = None
    else:
        recs["abbey"] = None

    # Choose best-scoring predictor with available recommendation
    best_name = None
    best_score = -10**9
    for name, move in recs.items():
        if move is None:
            continue
        score = st["scores"].get(name, 0)
        if score > best_score:
            best_score = score
            best_name = name

    # Fallback: frequency of last 20 opponent moves
    if best_name is None:
        window = st["opp"][-20:]
        freq = {"R": window.count("R"), "P": window.count("P"), "S": window.count("S")}
        guess = max(freq, key=freq.get) if window else "R"
        move = beats[guess]
    else:
        move = recs[best_name]

    # Update last recommendations for next round scoring
    st["last_recs"] = recs

    # Update our pair counts with chosen move
    if st["my"]:
        pair = st["my"][-1] + move
        if pair in st["pair_counts"]:
            st["pair_counts"][pair] += 1

    st["my"].append(move)
    return move
