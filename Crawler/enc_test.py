import hashlib, sys, time
import ecdsa

URL = 'https://github.com/bip32JP/ripple-playground/blob/master/ripple.py'

__b58chars = 'rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz'
__b58base = len(__b58chars)
""" This Base58 order is specific to Ripple. Do not use with Bitcoin. """

curve_order = ecdsa.curves.SECP256k1.order
""" Used in sanity checks """

def b58encode(v):
    """ encode v, which is a string of bytes, to base58."""

    long_value = 0L
    for (i, c) in enumerate(v[::-1]):
        long_value += (256**i) * ord(c)

    result = ''
    while long_value >= __b58base:
        div, mod = divmod(long_value, __b58base)
        result = __b58chars[mod] + result
        long_value = div
    result = __b58chars[long_value] + result

    nPad = 0
    for c in v:
        if c == '\0': nPad += 1
        else: break

    return (__b58chars[0]*nPad) + result

def Hash(x):
    """ Double SHA256 """
    if type(x) is unicode: x=x.encode('utf-8')
    return hashlib.sha256(hashlib.sha256(x).digest()).digest()

def data_to_address(data, addrtype = 0):
    """
    Add header byte to data, add checksum, then b58encode data.
    data = String of any data.
    addrtype = Int of the number of the header byte in base 10.
    """
    vdata = chr(addrtype) + data
    h = Hash(vdata)
    addr = vdata + h[0:4]
    return b58encode(addr)

def int2data(int1, padded=0):
    """
    Converts integer into hex data.
    int1 = integer to convert into data
    padded = number of bytes necessary. Will pad msb with 0 bytes. If 0, no padding.
    """
    if type(padded) is not int:
        return None
    padstr = '' if padded <= 0 else '0' + str(padded*2)
    formatstr = '%' + padstr + 'x'
    hexstr = (formatstr % int1)
    if len(hexstr) % 2 == 1: hexstr = '0' + hexstr
    return hexstr.decode('hex')

def genb58seed(entropy=None):
    """
    Generate a random Family Seed for Ripple. (Private Key)
    entropy = String of any random data. Please ensure high entropy.
    ## Note: ecdsa library's randrange() uses os.urandom() to get its entropy.
    ##       This should be secure enough... but just in case, I added the ability
    ##       to include your own entropy in addition.
    """
    if entropy == None:
        entropy = int2data(ecdsa.util.randrange( 2**128 ), 16)
    else:
        entropy = hashlib.sha256(entropy + int2data(ecdsa.util.randrange( 2**128 ), 16)).digest()[:16]
    b58seed = data_to_address(entropy, 33)
    return b58seed

def b58decode(v, length):
    """ decode v into a string of len bytes."""
    long_value = 0L
    for (i, c) in enumerate(v[::-1]):
        long_value += __b58chars.find(c) * (__b58base**i)

    result = ''
    while long_value >= 256:
        div, mod = divmod(long_value, 256)
        result = chr(mod) + result
        long_value = div
    result = chr(long_value) + result

    nPad = 0
    for c in v:
        if c == __b58chars[0]: nPad += 1
        else: break

    result = chr(0)*nPad + result
    if length is not None and len(result) != length:
        return None

    return result

def DecodeBase58Check(psz):
    """
    Validate checksum and return None if invalid.
    Return b58 decoded data SANS CHECKSUM if valid.
    """
    vchRet = b58decode(psz, None)
    key = vchRet[0:-4]
    csum = vchRet[-4:]
    hash = Hash(key)
    cs32 = hash[0:4]
    if cs32 != csum:
        return None
    else:
        return key

def hSHA512(data):
    """ The first half of the SHA512 is used a lot """
    return hashlib.sha512(data).digest()[:32]

def data2int(data):
    """ To compare data as an integer, this helps. """
    return int(data.encode('hex'),16)

def get_point(secret):
    """
    Get Point object from ecdsa.
    secret = String that contains the private key data.
    """
    return ecdsa.keys.SigningKey.from_string(secret, ecdsa.curves.SECP256k1, hashlib.sha256).verifying_key.pubkey.point

def get_pubkey(point, compressed=True):
    """
    Get the Serialized pubkey from an ecdsa Point object.
    point = ecdsa Point object
    compressed = Boolean whether or not you want the pubkey compressed.
    """
    if compressed:
        return ("0" + str(2 + (1 & point.y())) + ("%064x" % point.x())).decode('hex')
    else:
        return ("04" + ("%064x" % point.x()) + ("%064x" % point.y())).decode('hex')

def hash_160(public_key):
    """ Same as Bitcoin's SHA256>>RIPEMD160 """
    try:
        md = hashlib.new('ripemd160')
        md.update(hashlib.sha256(public_key).digest())
        return md.digest()
    except Exception:
        import ripemd
        md = ripemd.new(hashlib.sha256(public_key).digest())
        return md.digest()

def seed2accid(seed, acc=1, subacc=1):
    """
    Generate a Ripple account_id (address) from a Ripple Family Seed.
    seed = String with base58 encoded Ripple "Family Seed".
    acc = Int of the index of the family you want. (Default is 1st family)
    subacc = Int of the index of the account you want. (Default is 1st account)
    ## Note: Look into how families and accounts are used in the real world.
    ##       Currently, it seems most libraries just generate fam 1 acc 1 only.
    """
    dseed = DecodeBase58Check(seed)
    assert dseed != None and dseed[:1] == chr(33), 'Invalid Secret'
    seq = 0
    for i in range(acc):
        if i != 0: seq += 1
        fpgsec = hSHA512(dseed[1:] + int2data(seq, 4))
        while data2int(fpgsec) >= curve_order or data2int(fpgsec) <= 1:
            seq += 1
            fpgsec = hSHA512(dseed[1:] + int2data(seq, 4))
    fpgpt = get_point(fpgsec)
    fpgpub = get_pubkey(fpgpt)  # Family Pubkey
    subseq = 0
    for i in range(subacc):
        if i != 0: subseq += 1
        idxsec = hSHA512(fpgpub + int2data(seq, 4) + int2data(subseq, 4))
        while data2int(idxsec) >= curve_order or data2int(idxsec) <= 1:
            subseq += 1
            idxsec = hSHA512(fpgpub + int2data(seq, 4) + int2data(subseq, 4))
    idxpt = get_point(idxsec)
    accpt = fpgpt + idxpt
    accpub = get_pubkey(accpt)  # Account Pubkey
    acc160 = hash_160(accpub)

    fpgadd = data_to_address(fpgpub, 41)  # Family Public Generator
    accadd = data_to_address(accpub, 35)  # Account Public Key
    accid = data_to_address(acc160)  # Account ID (similar to address in Bitcoin)

    return fpgadd, accadd, accid

# words = ["like", "just", "love", "know", "never", "want", "time", "out", "there", "make", "look", "eye", "down", "only", "think", "heart", "back", "then", "into", "about", "more", "away", "still", "them", "take", "thing", "even", "through", "long", "always", "world", "too", "friend", "tell", "try", "hand", "thought", "over", "here", "other", "need", "smile", "again", "much", "cry", "been", "night", "ever", "little", "said", "end", "some", "those", "around", "mind", "people", "girl", "leave", "dream", "left", "turn", "myself", "give", "nothing", "really", "off", "before", "something", "find", "walk", "wish", "good", "once", "place", "ask", "stop", "keep", "watch", "seem", "everything", "wait", "got", "yet", "made", "remember", "start", "alone", "run", "hope", "maybe", "believe", "body", "hate", "after", "close", "talk", "stand", "own", "each", "hurt", "help", "home", "god", "soul", "new", "many", "two", "inside", "should", "true", "first", "fear", "mean", "better", "play", "another", "gone", "change", "use", "wonder", "someone", "hair", "cold", "open", "best", "any", "behind", "happen", "water", "dark", "laugh", "stay", "forever", "name", "work", "show", "sky", "break", "came", "deep", "door", "put", "black", "together", "upon", "happy", "such", "great", "white", "matter", "fill", "past", "please", "burn", "cause", "enough", "touch", "moment", "soon", "voice", "scream", "anything", "stare", "sound", "red", "everyone", "hide", "kiss", "truth", "death", "beautiful", "mine", "blood", "broken", "very", "pass", "next", "forget", "tree", "wrong", "air", "mother", "understand", "lip", "hit", "wall", "memory", "sleep", "free", "high", "realize", "school", "might", "skin", "sweet", "perfect", "blue", "kill", "breath", "dance", "against", "fly", "between", "grow", "strong", "under", "listen", "bring", "sometimes", "speak", "pull", "person", "become", "family", "begin", "ground", "real", "small", "father", "sure", "feet", "rest", "young", "finally", "land", "across", "today", "different", "guy", "line", "fire", "reason", "reach", "second", "slowly", "write", "eat", "smell", "mouth", "step", "learn", "three", "floor", "promise", "breathe", "darkness", "push", "earth", "guess", "save", "song", "above", "along", "both", "color", "house", "almost", "sorry", "anymore", "brother", "okay", "dear", "game", "fade", "already", "apart", "warm", "beauty", "heard", "notice", "question", "shine", "began", "piece", "whole", "shadow", "secret", "street", "within", "finger", "point", "morning", "whisper", "child", "moon", "green", "story", "glass", "kid", "silence", "since", "soft", "yourself", "empty", "shall", "angel", "answer", "baby", "bright", "dad", "path", "worry", "hour", "drop", "follow", "power", "war", "half", "flow", "heaven", "act", "chance", "fact", "least", "tired", "children", "near", "quite", "afraid", "rise", "sea", "taste", "window", "cover", "nice", "trust", "lot", "sad", "cool", "force", "peace", "return", "blind", "easy", "ready", "roll", "rose", "drive", "held", "music", "beneath", "hang", "mom", "paint", "emotion", "quiet", "clear", "cloud", "few", "pretty", "bird", "outside", "paper", "picture", "front", "rock", "simple", "anyone", "meant", "reality", "road", "sense", "waste", "bit", "leaf", "thank", "happiness", "meet", "men", "smoke", "truly", "decide", "self", "age", "book", "form", "alive", "carry", "escape", "damn", "instead", "able", "ice", "minute", "throw", "catch", "leg", "ring", "course", "goodbye", "lead", "poem", "sick", "corner", "desire", "known", "problem", "remind", "shoulder", "suppose", "toward", "wave", "drink", "jump", "woman", "pretend", "sister", "week", "human", "joy", "crack", "grey", "pray", "surprise", "dry", "knee", "less", "search", "bleed", "caught", "clean", "embrace", "future", "king", "son", "sorrow", "chest", "hug", "remain", "sat", "worth", "blow", "daddy", "final", "parent", "tight", "also", "create", "lonely", "safe", "cross", "dress", "evil", "silent", "bone", "fate", "perhaps", "anger", "class", "scar", "snow", "tiny", "tonight", "continue", "control", "dog", "edge", "mirror", "month", "suddenly", "comfort", "given", "loud", "quickly", "gaze", "plan", "rush", "stone", "town", "battle", "ignore", "spirit", "stood", "stupid", "yours", "brown", "build", "dust", "hey", "kept", "pay", "phone", "twist", "although", "ball", "beyond", "hidden", "nose", "taken", "fail", "float", "pure", "somehow", "wash", "wrap", "angry", "cheek", "creature", "forgotten", "heat", "rip", "single", "space", "special", "weak", "whatever", "yell", "anyway", "blame", "job", "choose", "country", "curse", "drift", "echo", "figure", "grew", "laughter", "neck", "suffer", "worse", "yeah", "disappear", "foot", "forward", "knife", "mess", "somewhere", "stomach", "storm", "beg", "idea", "lift", "offer", "breeze", "field", "five", "often", "simply", "stuck", "win", "allow", "confuse", "enjoy", "except", "flower", "seek", "strength", "calm", "grin", "gun", "heavy", "hill", "large", "ocean", "shoe", "sigh", "straight", "summer", "tongue", "accept", "crazy", "everyday", "exist", "grass", "mistake", "sent", "shut", "surround", "table", "ache", "brain", "destroy", "heal", "nature", "shout", "sign", "stain", "choice", "doubt", "glance", "glow", "mountain", "queen", "stranger", "throat", "tomorrow", "city", "either", "fish", "flame", "rather", "shape", "spin", "spread", "ash", "distance", "finish", "image", "imagine", "important", "nobody", "shatter", "warmth", "became", "feed", "flesh", "funny", "lust", "shirt", "trouble", "yellow", "attention", "bare", "bite", "money", "protect", "amaze", "appear", "born", "choke", "completely", "daughter", "fresh", "friendship", "gentle", "probably", "six", "deserve", "expect", "grab", "middle", "nightmare", "river", "thousand", "weight", "worst", "wound", "barely", "bottle", "cream", "regret", "relationship", "stick", "test", "crush", "endless", "fault", "itself", "rule", "spill", "art", "circle", "join", "kick", "mask", "master", "passion", "quick", "raise", "smooth", "unless", "wander", "actually", "broke", "chair", "deal", "favorite", "gift", "note", "number", "sweat", "box", "chill", "clothes", "lady", "mark", "park", "poor", "sadness", "tie", "animal", "belong", "brush", "consume", "dawn", "forest", "innocent", "pen", "pride", "stream", "thick", "clay", "complete", "count", "draw", "faith", "press", "silver", "struggle", "surface", "taught", "teach", "wet", "bless", "chase", "climb", "enter", "letter", "melt", "metal", "movie", "stretch", "swing", "vision", "wife", "beside", "crash", "forgot", "guide", "haunt", "joke", "knock", "plant", "pour", "prove", "reveal", "steal", "stuff", "trip", "wood", "wrist", "bother", "bottom", "crawl", "crowd", "fix", "forgive", "frown", "grace", "loose", "lucky", "party", "release", "surely", "survive", "teacher", "gently", "grip", "speed", "suicide", "travel", "treat", "vein", "written", "cage", "chain", "conversation", "date", "enemy", "however", "interest", "million", "page", "pink", "proud", "sway", "themselves", "winter", "church", "cruel", "cup", "demon", "experience", "freedom", "pair", "pop", "purpose", "respect", "shoot", "softly", "state", "strange", "bar", "birth", "curl", "dirt", "excuse", "lord", "lovely", "monster", "order", "pack", "pants", "pool", "scene", "seven", "shame", "slide", "ugly", "among", "blade", "blonde", "closet", "creek", "deny", "drug", "eternity", "gain", "grade", "handle", "key", "linger", "pale", "prepare", "swallow", "swim", "tremble", "wheel", "won", "cast", "cigarette", "claim", "college", "direction", "dirty", "gather", "ghost", "hundred", "loss", "lung", "orange", "present", "swear", "swirl", "twice", "wild", "bitter", "blanket", "doctor", "everywhere", "flash", "grown", "knowledge", "numb", "pressure", "radio", "repeat", "ruin", "spend", "unknown", "buy", "clock", "devil", "early", "false", "fantasy", "pound", "precious", "refuse", "sheet", "teeth", "welcome", "add", "ahead", "block", "bury", "caress", "content", "depth", "despite", "distant", "marry", "purple", "threw", "whenever", "bomb", "dull", "easily", "grasp", "hospital", "innocence", "normal", "receive", "reply", "rhyme", "shade", "someday", "sword", "toe", "visit", "asleep", "bought", "center", "consider", "flat", "hero", "history", "ink", "insane", "muscle", "mystery", "pocket", "reflection", "shove", "silently", "smart", "soldier", "spot", "stress", "train", "type", "view", "whether", "bus", "energy", "explain", "holy", "hunger", "inch", "magic", "mix", "noise", "nowhere", "prayer", "presence", "shock", "snap", "spider", "study", "thunder", "trail", "admit", "agree", "bag", "bang", "bound", "butterfly", "cute", "exactly", "explode", "familiar", "fold", "further", "pierce", "reflect", "scent", "selfish", "sharp", "sink", "spring", "stumble", "universe", "weep", "women", "wonderful", "action", "ancient", "attempt", "avoid", "birthday", "branch", "chocolate", "core", "depress", "drunk", "especially", "focus", "fruit", "honest", "match", "palm", "perfectly", "pillow", "pity", "poison", "roar", "shift", "slightly", "thump", "truck", "tune", "twenty", "unable", "wipe", "wrote", "coat", "constant", "dinner", "drove", "egg", "eternal", "flight", "flood", "frame", "freak", "gasp", "glad", "hollow", "motion", "peer", "plastic", "root", "screen", "season", "sting", "strike", "team", "unlike", "victim", "volume", "warn", "weird", "attack", "await", "awake", "built", "charm", "crave", "despair", "fought", "grant", "grief", "horse", "limit", "message", "ripple", "sanity", "scatter", "serve", "split", "string", "trick", "annoy", "blur", "boat", "brave", "clearly", "cling", "connect", "fist", "forth", "imagination", "iron", "jock", "judge", "lesson", "milk", "misery", "nail", "naked", "ourselves", "poet", "possible", "princess", "sail", "size", "snake", "society", "stroke", "torture", "toss", "trace", "wise", "bloom", "bullet", "cell", "check", "cost", "darling", "during", "footstep", "fragile", "hallway", "hardly", "horizon", "invisible", "journey", "midnight", "mud", "nod", "pause", "relax", "shiver", "sudden", "value", "youth", "abuse", "admire", "blink", "breast", "bruise", "constantly", "couple", "creep", "curve", "difference", "dumb", "emptiness", "gotta", "honor", "plain", "planet", "recall", "rub", "ship", "slam", "soar", "somebody", "tightly", "weather", "adore", "approach", "bond", "bread", "burst", "candle", "coffee", "cousin", "crime", "desert", "flutter", "frozen", "grand", "heel", "hello", "language", "level", "movement", "pleasure", "powerful", "random", "rhythm", "settle", "silly", "slap", "sort", "spoken", "steel", "threaten", "tumble", "upset", "aside", "awkward", "bee", "blank", "board", "button", "card", "carefully", "complain", "crap", "deeply", "discover", "drag", "dread", "effort", "entire", "fairy", "giant", "gotten", "greet", "illusion", "jeans", "leap", "liquid", "march", "mend", "nervous", "nine", "replace", "rope", "spine", "stole", "terror", "accident", "apple", "balance", "boom", "childhood", "collect", "demand", "depression", "eventually", "faint", "glare", "goal", "group", "honey", "kitchen", "laid", "limb", "machine", "mere", "mold", "murder", "nerve", "painful", "poetry", "prince", "rabbit", "shelter", "shore", "shower", "soothe", "stair", "steady", "sunlight", "tangle", "tease", "treasure", "uncle", "begun", "bliss", "canvas", "cheer", "claw", "clutch", "commit", "crimson", "crystal", "delight", "doll", "existence", "express", "fog", "football", "gay", "goose", "guard", "hatred", "illuminate", "mass", "math", "mourn", "rich", "rough", "skip", "stir", "student", "style", "support", "thorn", "tough", "yard", "yearn", "yesterday", "advice", "appreciate", "autumn", "bank", "beam", "bowl", "capture", "carve", "collapse", "confusion", "creation", "dove", "feather", "girlfriend", "glory", "government", "harsh", "hop", "inner", "loser", "moonlight", "neighbor", "neither", "peach", "pig", "praise", "screw", "shield", "shimmer", "sneak", "stab", "subject", "throughout", "thrown", "tower", "twirl", "wow", "army", "arrive", "bathroom", "bump", "cease", "cookie", "couch", "courage", "dim", "guilt", "howl", "hum", "husband", "insult", "led", "lunch", "mock", "mostly", "natural", "nearly", "needle", "nerd", "peaceful", "perfection", "pile", "price", "remove", "roam", "sanctuary", "serious", "shiny", "shook", "sob", "stolen", "tap", "vain", "void", "warrior", "wrinkle", "affection", "apologize", "blossom", "bounce", "bridge", "cheap", "crumble", "decision", "descend", "desperately", "dig", "dot", "flip", "frighten", "heartbeat", "huge", "lazy", "lick", "odd", "opinion", "process", "puzzle", "quietly", "retreat", "score", "sentence", "separate", "situation", "skill", "soak", "square", "stray", "taint", "task", "tide", "underneath", "veil", "whistle", "anywhere", "bedroom", "bid", "bloody", "burden", "careful", "compare", "concern", "curtain", "decay", "defeat", "describe", "double", "dreamer", "driver", "dwell", "evening", "flare", "flicker", "grandma", "guitar", "harm", "horrible", "hungry", "indeed", "lace", "melody", "monkey", "nation", "object", "obviously", "rainbow", "salt", "scratch", "shown", "shy", "stage", "stun", "third", "tickle", "useless", "weakness", "worship", "worthless", "afternoon", "beard", "boyfriend", "bubble", "busy", "certain", "chin", "concrete", "desk", "diamond", "doom", "drawn", "due", "felicity", "freeze", "frost", "garden", "glide", "harmony", "hopefully", "hunt", "jealous", "lightning", "mama", "mercy", "peel", "physical", "position", "pulse", "punch", "quit", "rant", "respond", "salty", "sane", "satisfy", "savior", "sheep", "slept", "social", "sport", "tuck", "utter", "valley", "wolf", "aim", "alas", "alter", "arrow", "awaken", "beaten", "belief", "brand", "ceiling", "cheese", "clue", "confidence", "connection", "daily", "disguise", "eager", "erase", "essence", "everytime", "expression", "fan", "flag", "flirt", "foul", "fur", "giggle", "glorious", "ignorance", "law", "lifeless", "measure", "mighty", "muse", "north", "opposite", "paradise", "patience", "patient", "pencil", "petal", "plate", "ponder", "possibly", "practice", "slice", "spell", "stock", "strife", "strip", "suffocate", "suit", "tender", "tool", "trade", "velvet", "verse", "waist", "witch", "aunt", "bench", "bold", "cap", "certainly", "click", "companion", "creator", "dart", "delicate", "determine", "dish", "dragon", "drama", "drum", "dude", "everybody", "feast", "forehead", "former", "fright", "fully", "gas", "hook", "hurl", "invite", "juice", "manage", "moral", "possess", "raw", "rebel", "royal", "scale", "scary", "several", "slight", "stubborn", "swell", "talent", "tea", "terrible", "thread", "torment", "trickle", "usually", "vast", "violence", "weave", "acid", "agony", "ashamed", "awe", "belly", "blend", "blush", "character", "cheat", "common", "company", "coward", "creak", "danger", "deadly", "defense", "define", "depend", "desperate", "destination", "dew", "duck", "dusty", "embarrass", "engine", "example", "explore", "foe", "freely", "frustrate", "generation", "glove", "guilty", "health", "hurry", "idiot", "impossible", "inhale", "jaw", "kingdom", "mention", "mist", "moan", "mumble", "mutter", "observe", "ode", "pathetic", "pattern", "pie", "prefer", "puff", "rape", "rare", "revenge", "rude", "scrape", "spiral", "squeeze", "strain", "sunset", "suspend", "sympathy", "thigh", "throne", "total", "unseen", "weapon", "weary"]
words = ['acrobat', 'africa', 'alaska', 'albert', 'albino', 'albumalcohol', 'alex', 'alpha', 'amadeus', 'amanda', 'amazonamerica', 'analog', 'animal', 'antenna', 'antonio', 'apolloapril', 'aroma', 'artist', 'aspirin', 'athlete', 'atlasbanana', 'bandit', 'banjo', 'bikini', 'bingo', 'bonuscamera', 'canada', 'carbon', 'casino', 'catalog', 'cinemacitizen', 'cobra', 'comet', 'compact', 'complex', 'contextcredit', 'critic', 'crystal', 'culture', 'david', 'deltadialog', 'diploma', 'doctor', 'domino', 'dragon', 'dramaextra', 'fabric', 'final', 'focus', 'forum', 'galaxygallery', 'global', 'harmony', 'hotel', 'humor', 'indexjapan', 'kilo', 'lemon', 'liter', 'lotus', 'mangomelon', 'menu', 'meter', 'metro', 'mineral', 'modelmusic', 'object', 'piano', 'pirate', 'plastic', 'radioreport', 'signal', 'sport', 'studio', 'subject', 'supertango', 'taxi', 'tempo', 'tennis', 'textile', 'tokyototal', 'tourist', 'video', 'visa', 'academy', 'alfredatlanta', 'atomic', 'barbara', 'bazaar', 'brother', 'budgetcabaret', 'cadet', 'candle', 'capsule', 'caviar', 'channelchapter', 'circle', 'cobalt', 'comrade', 'condor', 'crimsoncyclone', 'darwin', 'declare', 'denver', 'desert', 'dividedolby', 'domain', 'double', 'eagle', 'echo', 'eclipseeditor', 'educate', 'edward', 'effect', 'electra', 'emeraldemotion', 'empire', 'eternal', 'evening', 'exhibit', 'expandexplore', 'extreme', 'ferrari', 'forget', 'freedom', 'fridayfuji', 'galileo', 'genesis', 'gravity', 'habitat', 'hamletharlem', 'helium', 'holiday', 'hunter', 'ibiza', 'icebergimagine', 'infant', 'isotope', 'jackson', 'jamaica', 'jasminejava', 'jessica', 'kitchen', 'lazarus', 'letter', 'licenselithium', 'loyal', 'lucky', 'magenta', 'manual', 'marblemaxwell', 'mayor', 'monarch', 'monday', 'money', 'morningmother', 'mystery', 'native', 'nectar', 'nelson', 'networknikita', 'nobel', 'nobody', 'nominal', 'norway', 'nothingnumber', 'october', 'office', 'oliver', 'opinion', 'optionorder', 'outside', 'package', 'pandora', 'panther', 'papapattern', 'pedro', 'pencil', 'people', 'phantom', 'philipspioneer', 'pluto', 'podium', 'portal', 'potato', 'processproxy', 'pupil', 'python', 'quality', 'quarter', 'quietrabbit', 'radical', 'radius', 'rainbow', 'ramirez', 'ravioliraymond', 'respect', 'respond', 'result', 'resume', 'richardriver', 'roger', 'roman', 'rondo', 'sabrina', 'salarysalsa', 'sample', 'samuel', 'saturn', 'savage', 'scarletscorpio', 'sector', 'serpent', 'shampoo', 'sharon', 'silencesimple', 'society', 'sonar', 'sonata', 'soprano', 'spartaspider', 'sponsor', 'abraham', 'action', 'active', 'actoradam', 'address', 'admiral', 'adrian', 'agenda', 'agentairline', 'airport', 'alabama', 'aladdin', 'alarm', 'algebraalibi', 'alice', 'alien', 'almond', 'alpine', 'amberamigo', 'ammonia', 'analyze', 'anatomy', 'angel', 'annualanswer', 'apple', 'archive', 'arctic', 'arena', 'arizonaarmada', 'arnold', 'arsenal', 'arthur', 'asia', 'aspectathena', 'audio', 'august', 'austria', 'avenue', 'averageaxiom', 'aztec', 'bagel', 'baker', 'balance', 'balladballet', 'bambino', 'bamboo', 'baron', 'basic', 'basketbattery', 'belgium', 'benefit', 'berlin', 'bermuda', 'bernardbicycle', 'binary', 'biology', 'bishop', 'blitz', 'blockblonde', 'bonjour', 'boris', 'boston', 'bottle', 'boxerbrandy', 'bravo', 'brazil', 'bridge', 'british', 'bronzebrown', 'bruce', 'bruno', 'brush', 'burger', 'burmacabinet', 'cactus', 'cafe', 'cairo', 'calypso', 'camelcampus', 'canal', 'cannon', 'canoe', 'cantina', 'canvascanyon', 'capital', 'caramel', 'caravan', 'career', 'cargocarlo', 'carol', 'carpet', 'cartel', 'cartoon', 'castlecastro', 'cecilia', 'cement', 'center', 'century', 'ceramicchamber', 'chance', 'change', 'chaos', 'charlie', 'charmcharter', 'cheese', 'chef', 'chemist', 'cherry', 'chesschicago', 'chicken', 'chief', 'china', 'cigar', 'circuscity', 'clara', 'classic', 'claudia', 'clean', 'clientclimax', 'clinic', 'clock', 'club', 'cockpit', 'coconutcola', 'collect', 'colombo', 'colony', 'color', 'combatcomedy', 'command', 'company', 'concert', 'connect', 'consulcontact', 'contour', 'control', 'convert', 'copy', 'cornercorona', 'correct', 'cosmos', 'couple', 'courage', 'cowboycraft', 'crash', 'cricket', 'crown', 'cuba', 'dallasdance', 'daniel', 'decade', 'decimal', 'degree', 'deletedeliver', 'delphi', 'deluxe', 'demand', 'demo', 'denmarkderby', 'design', 'detect', 'develop', 'diagram', 'diamonddiana', 'diego', 'diesel', 'diet', 'digital', 'dilemmadirect', 'disco', 'disney', 'distant', 'dollar', 'dolphindonald', 'drink', 'driver', 'dublin', 'duet', 'dynamicearth', 'east', 'ecology', 'economy', 'edgar', 'egyptelastic', 'elegant', 'element', 'elite', 'elvis', 'emailempty', 'energy', 'engine', 'english', 'episode', 'equatorescape', 'escort', 'ethnic', 'europe', 'everest', 'evidentexact', 'example', 'exit', 'exotic', 'export', 'expressfactor', 'falcon', 'family', 'fantasy', 'fashion', 'fiberfiction', 'fidel', 'fiesta', 'figure', 'film', 'filterfinance', 'finish', 'finland', 'first', 'flag', 'flashflorida', 'flower', 'fluid', 'flute', 'folio', 'fordforest', 'formal', 'formula', 'fortune', 'forward', 'fragilefrance', 'frank', 'fresh', 'friend', 'frozen', 'futuregabriel', 'gamma', 'garage', 'garcia', 'garden', 'garlicgemini', 'general', 'genetic', 'genius', 'germany', 'gloriagold', 'golf', 'gondola', 'gong', 'good', 'gordongorilla', 'grand', 'granite', 'graph', 'green', 'groupguide', 'guitar', 'guru', 'hand', 'happy', 'harborharvard', 'havana', 'hawaii', 'helena', 'hello', 'henryhilton', 'history', 'horizon', 'house', 'human', 'iconidea', 'igloo', 'igor', 'image', 'impact', 'importindia', 'indigo', 'input', 'insect', 'instant', 'irisitalian', 'jacket', 'jacob', 'jaguar', 'janet', 'jargonjazz', 'jeep', 'john', 'joker', 'jordan', 'judojumbo', 'june', 'jungle', 'junior', 'jupiter', 'karatekarma', 'kayak', 'kermit', 'king', 'koala', 'korealabor', 'lady', 'lagoon', 'laptop', 'laser', 'latinlava', 'lecture', 'left', 'legal', 'level', 'lexiconliberal', 'libra', 'lily', 'limbo', 'limit', 'lindalinear', 'lion', 'liquid', 'little', 'llama', 'lobbylobster', 'local', 'logic', 'logo', 'lola', 'londonlucas', 'lunar', 'machine', 'macro', 'madam', 'madonnamadrid', 'maestro', 'magic', 'magnet', 'magnum', 'mailboxmajor', 'mama', 'mambo', 'manager', 'manila', 'marcomarina', 'market', 'mars', 'martin', 'marvin', 'marymaster', 'matrix', 'maximum', 'media', 'medical', 'megamelody', 'memo', 'mental', 'mentor', 'mercury', 'messagemetal', 'meteor', 'method', 'mexico', 'miami', 'micromilk', 'million', 'minimum', 'minus', 'minute', 'miraclemirage', 'miranda', 'mister', 'mixer', 'mobile', 'modemmodern', 'modular', 'moment', 'monaco', 'monica', 'monitormono', 'monster', 'montana', 'morgan', 'motel', 'motifmotor', 'mozart', 'multi', 'museum', 'mustang', 'naturalneon', 'nepal', 'neptune', 'nerve', 'neutral', 'nevadanews', 'next', 'ninja', 'nirvana', 'normal', 'novanovel', 'nuclear', 'numeric', 'nylon', 'oasis', 'observeocean', 'octopus', 'olivia', 'olympic', 'omega', 'operaoptic', 'optimal', 'orange', 'orbit', 'organic', 'orientorigin', 'orlando', 'oscar', 'oxford', 'oxygen', 'ozonepablo', 'pacific', 'pagoda', 'palace', 'pamela', 'panamapancake', 'panda', 'panel', 'panic', 'paradox', 'pardonparis', 'parker', 'parking', 'parody', 'partner', 'passagepassive', 'pasta', 'pastel', 'patent', 'patient', 'patriotpatrol', 'pegasus', 'pelican', 'penguin', 'pepper', 'percentperfect', 'perfume', 'period', 'permit', 'person', 'peruphone', 'photo', 'picasso', 'picnic', 'picture', 'pigmentpilgrim', 'pilot', 'pixel', 'pizza', 'planet', 'plasmaplaza', 'pocket', 'poem', 'poetic', 'poker', 'polarispolice', 'politic', 'polo', 'polygon', 'pony', 'popcornpopular', 'postage', 'precise', 'prefix', 'premium', 'presentprice', 'prince', 'printer', 'prism', 'private', 'prizeproduct', 'profile', 'program', 'project', 'protect', 'protonpublic', 'pulse', 'puma', 'pump', 'pyramid', 'queenradar', 'ralph', 'random', 'rapid', 'rebel', 'recordrecycle', 'reflex', 'reform', 'regard', 'regular', 'relaxreptile', 'reverse', 'ricardo', 'right', 'ringo', 'riskritual', 'robert', 'robot', 'rocket', 'rodeo', 'romeoroyal', 'russian', 'safari', 'salad', 'salami', 'salmonsalon', 'salute', 'samba', 'sandra', 'santana', 'sardineschool', 'scoop', 'scratch', 'screen', 'script', 'scrollsecond', 'secret', 'section', 'segment', 'select', 'seminarsenator', 'senior', 'sensor', 'serial', 'service', 'shadowsharp', 'sheriff', 'shock', 'short', 'shrink', 'sierrasilicon', 'silk', 'silver', 'similar', 'simon', 'singlesiren', 'slang', 'slogan', 'smart', 'smoke', 'snakesocial', 'soda', 'solar', 'solid', 'solo', 'sonicsource', 'soviet', 'special', 'speed', 'sphere', 'spiralspirit', 'spring', 'static', 'status', 'stereo', 'stonestop', 'street', 'strong', 'student', 'style', 'sultansusan', 'sushi', 'suzuki', 'switch', 'symbol', 'systemtactic', 'tahiti', 'talent', 'tarzan', 'telex', 'texastheory', 'thermos', 'tiger', 'titanic', 'tomato', 'topictornado', 'toronto', 'torpedo', 'totem', 'tractor', 'traffictransit', 'trapeze', 'travel', 'tribal', 'trick', 'tridenttrilogy', 'tripod', 'tropic', 'trumpet', 'tulip', 'tunaturbo', 'twist', 'ultra', 'uniform', 'union', 'uraniumvacuum', 'valid', 'vampire', 'vanilla', 'vatican', 'velvetventura', 'venus', 'vertigo', 'veteran', 'victor', 'viennaviking', 'village', 'vincent', 'violet', 'violin', 'virtualvirus', 'vision', 'visitor', 'visual', 'vitamin', 'vivavocal', 'vodka', 'volcano', 'voltage', 'volume', 'voyagewater', 'weekend', 'welcome', 'western', 'window', 'winterwizard', 'wolf', 'world', 'xray', 'yankee', 'yogayogurt', 'yoyo', 'zebra', 'zero', 'zigzag', 'zipperzodiac', 'zoom', 'acid', 'adios', 'agatha', 'alamoalert', 'almanac', 'aloha', 'andrea', 'anita', 'arcadeaurora', 'avalon', 'baby', 'baggage', 'balloon', 'bankbasil', 'begin', 'biscuit', 'blue', 'bombay', 'botanicbrain', 'brenda', 'brigade', 'cable', 'calibre', 'carmencello', 'celtic', 'chariot', 'chrome', 'citrus', 'civilcloud', 'combine', 'common', 'cool', 'copper', 'coralcrater', 'cubic', 'cupid', 'cycle', 'depend', 'doordream', 'dynasty', 'edison', 'edition', 'enigma', 'equaleric', 'event', 'evita', 'exodus', 'extend', 'famousfarmer', 'food', 'fossil', 'frog', 'fruit', 'genevagentle', 'george', 'giant', 'gilbert', 'gossip', 'gramgreek', 'grille', 'hammer', 'harvest', 'hazard', 'heavenherbert', 'heroic', 'hexagon', 'husband', 'immune', 'incainch', 'initial', 'isabel', 'ivory', 'jason', 'jeromejoel', 'joshua', 'journal', 'judge', 'juliet', 'jumpjustice', 'kimono', 'kinetic', 'leonid', 'leopard', 'limamaze', 'medusa', 'member', 'memphis', 'michael', 'miguelmilan', 'mile', 'miller', 'mimic', 'mimosa', 'missionmonkey', 'moral', 'moses', 'mouse', 'nancy', 'natashanebula', 'nickel', 'nina', 'noise', 'orchid', 'oreganoorigami', 'orinoco', 'orion', 'othello', 'paper', 'paprikaprelude', 'prepare', 'pretend', 'promise', 'prosper', 'providepuzzle', 'remote', 'repair', 'reply', 'rival', 'rivierarobin', 'rose', 'rover', 'rudolf', 'saga', 'saharascholar', 'shelter', 'ship', 'shoe', 'sigma', 'sistersleep', 'smile', 'spain', 'spark', 'split', 'spraysquare', 'stadium', 'star', 'storm', 'story', 'strangestretch', 'stuart', 'subway', 'sugar', 'sulfur', 'summersurvive', 'sweet', 'swim', 'table', 'taboo', 'targetteacher', 'telecom', 'temple', 'tibet', 'ticket', 'tinatoday', 'toga', 'tommy', 'tower', 'trivial', 'tunnelturtle', 'twin', 'uncle', 'unicorn', 'unique', 'updatevalery', 'vega', 'version', 'voodoo', 'warning', 'williamwonder', 'year', 'yellow', 'young', 'absent', 'absorbabsurd', 'accent', 'alfonso', 'alias', 'ambient', 'anagramandy', 'anvil', 'appear', 'apropos', 'archer', 'arielarmor', 'arrow', 'austin', 'avatar', 'axis', 'baboonbahama', 'bali', 'balsa', 'barcode', 'bazooka', 'beachbeast', 'beatles', 'beauty', 'before', 'benny', 'bettybetween', 'beyond', 'billy', 'bison', 'blast', 'blessbogart', 'bonanza', 'book', 'border', 'brave', 'breadbreak', 'broken', 'bucket', 'buenos', 'buffalo', 'bundlebutton', 'buzzer', 'byte', 'caesar', 'camilla', 'canarycandid', 'carrot', 'cave', 'chant', 'child', 'choicechris', 'cipher', 'clarion', 'clark', 'clever', 'cliffclone', 'conan', 'conduct', 'congo', 'costume', 'cottoncover', 'crack', 'current', 'danube', 'data', 'decidedeposit', 'desire', 'detail', 'dexter', 'dinner', 'donordruid', 'drum', 'easy', 'eddie', 'enjoy', 'enricoepoxy', 'erosion', 'except', 'exile', 'explain', 'famefast', 'father', 'felix', 'field', 'fiona', 'firefish', 'flame', 'flex', 'flipper', 'float', 'floodfloor', 'forbid', 'forever', 'fractal', 'frame', 'freddiefront', 'fuel', 'gallop', 'game', 'garbo', 'gategelatin', 'gibson', 'ginger', 'giraffe', 'gizmo', 'glassgoblin', 'gopher', 'grace', 'gray', 'gregory', 'gridgriffin', 'ground', 'guest', 'gustav', 'gyro', 'hairhalt', 'harris', 'heart', 'heavy', 'herman', 'hippiehobby', 'honey', 'hope', 'horse', 'hostel', 'hydroimitate', 'info', 'ingrid', 'inside', 'invent', 'investinvite', 'ivan', 'james', 'jester', 'jimmy', 'joinjoseph', 'juice', 'julius', 'july', 'kansas', 'karlkevin', 'kiwi', 'ladder', 'lake', 'laura', 'learnlegacy', 'legend', 'lesson', 'life', 'light', 'listlocate', 'lopez', 'lorenzo', 'love', 'lunch', 'maltamammal', 'margin', 'margo', 'marion', 'mask', 'matchmayday', 'meaning', 'mercy', 'middle', 'mike', 'mirrormodest', 'morph', 'morris', 'mystic', 'nadia', 'natonavy', 'needle', 'neuron', 'never', 'newton', 'nicenight', 'nissan', 'nitro', 'nixon', 'north', 'oberonoctavia', 'ohio', 'olga', 'open', 'opus', 'orcaoval', 'owner', 'page', 'paint', 'palma', 'parentparlor', 'parole', 'paul', 'peace', 'pearl', 'performphoenix', 'phrase', 'pierre', 'pinball', 'place', 'plateplato', 'plume', 'pogo', 'point', 'polka', 'ponchopowder', 'prague', 'press', 'presto', 'pretty', 'primepromo', 'quest', 'quick', 'quiz', 'quota', 'racerachel', 'raja', 'ranger', 'region', 'remark', 'rentreward', 'rhino', 'ribbon', 'rider', 'road', 'rodentround', 'rubber', 'ruby', 'rufus', 'sabine', 'saddlesailor', 'saint', 'salt', 'scale', 'scuba', 'seasonsecure', 'shake', 'shallow', 'shannon', 'shave', 'shelfsherman', 'shine', 'shirt', 'side', 'sinatra', 'sinceresize', 'slalom', 'slow', 'small', 'snow', 'sofiasong', 'sound', 'south', 'speech', 'spell', 'spendspoon', 'stage', 'stamp', 'stand', 'state', 'stellastick', 'sting', 'stock', 'store', 'sunday', 'sunsetsupport', 'supreme', 'sweden', 'swing', 'tape', 'tavernthink', 'thomas', 'tictac', 'time', 'toast', 'tobaccotonight', 'torch', 'torso', 'touch', 'toyota', 'tradetribune', 'trinity', 'triton', 'truck', 'trust', 'typeunder', 'unit', 'urban', 'urgent', 'user', 'valuevendor', 'venice', 'verona', 'vibrate', 'virgo', 'visiblevista', 'vital', 'voice', 'vortex', 'waiter', 'watchwave', 'weather', 'wedding', 'wheel', 'whiskey', 'wisdomandroid', 'annex', 'armani', 'cake', 'confide', 'dealdefine', 'dispute', 'genuine', 'idiom', 'impress', 'includeironic', 'null', 'nurse', 'obscure', 'prefer', 'prodigyego', 'fax', 'jet', 'job', 'rio', 'ski', 'yes']
wordcount = 1626

def mn_decode( wlist ):
    out = ''
    for i in range(len(wlist)/3):
        word1, word2, word3 = wlist[3*i:3*i+3]
        w1 =  words.index(word1)
        w2 = (words.index(word2))%wordcount
        w3 = (words.index(word3))%wordcount
        x = w1 +wordcount*((w2-w1)%wordcount) +wordcount*wordcount*((w3-w2)%wordcount)
        out += '%08x'%x
    return out

def mn_encode( message ):
    assert len(message) % 8 == 0
    out = []
    for i in range(len(message)/8):
        word = message[8*i:8*i+8]
        x = int(word, 16)
        w1 = (x%wordcount)
        w2 = ((x/wordcount) + w1)%wordcount
        w3 = ((x/wordcount/wordcount) + w2)%wordcount
        out += [ words[w1], words[w2], words[w3] ]
    return out

def seed2mnemonic(seed):
    dseed = DecodeBase58Check(seed)
    assert dseed != None and dseed[:1] == chr(33), 'Invalid Secret'
    return ' '.join(mn_encode(dseed[1:].encode('hex')))


def mnemonic2seed(phrase):
    words = phrase.split(' ')
    hexstr = mn_decode(words)
    return data_to_address(hexstr.decode('hex'), 33)



# seed = genb58seed()
# fpgadd, accadd, accid = seed2accid(seed)
#
# print(seed)
# print(fpgadd)
# print(accadd)
# print(accid)