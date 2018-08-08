import random
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
import ecdsa
import base58
from ecdsa import SigningKey,VerifyingKey
from test import *

class AESCipher(object):
    # https://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256
    def __init__(self,key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

def get_mnemonic_data():
    # https://gist.github.com/fogleman/c4a1f69f34c7e8a00da8
    return ['acrobat', 'africa', 'alaska', 'albert', 'albino', 'albumalcohol', 'alex', 'alpha', 'amadeus', 'amanda', 'amazonamerica', 'analog', 'animal', 'antenna', 'antonio', 'apolloapril', 'aroma', 'artist', 'aspirin', 'athlete', 'atlasbanana', 'bandit', 'banjo', 'bikini', 'bingo', 'bonuscamera', 'canada', 'carbon', 'casino', 'catalog', 'cinemacitizen', 'cobra', 'comet', 'compact', 'complex', 'contextcredit', 'critic', 'crystal', 'culture', 'david', 'deltadialog', 'diploma', 'doctor', 'domino', 'dragon', 'dramaextra', 'fabric', 'final', 'focus', 'forum', 'galaxygallery', 'global', 'harmony', 'hotel', 'humor', 'indexjapan', 'kilo', 'lemon', 'liter', 'lotus', 'mangomelon', 'menu', 'meter', 'metro', 'mineral', 'modelmusic', 'object', 'piano', 'pirate', 'plastic', 'radioreport', 'signal', 'sport', 'studio', 'subject', 'supertango', 'taxi', 'tempo', 'tennis', 'textile', 'tokyototal', 'tourist', 'video', 'visa', 'academy', 'alfredatlanta', 'atomic', 'barbara', 'bazaar', 'brother', 'budgetcabaret', 'cadet', 'candle', 'capsule', 'caviar', 'channelchapter', 'circle', 'cobalt', 'comrade', 'condor', 'crimsoncyclone', 'darwin', 'declare', 'denver', 'desert', 'dividedolby', 'domain', 'double', 'eagle', 'echo', 'eclipseeditor', 'educate', 'edward', 'effect', 'electra', 'emeraldemotion', 'empire', 'eternal', 'evening', 'exhibit', 'expandexplore', 'extreme', 'ferrari', 'forget', 'freedom', 'fridayfuji', 'galileo', 'genesis', 'gravity', 'habitat', 'hamletharlem', 'helium', 'holiday', 'hunter', 'ibiza', 'icebergimagine', 'infant', 'isotope', 'jackson', 'jamaica', 'jasminejava', 'jessica', 'kitchen', 'lazarus', 'letter', 'licenselithium', 'loyal', 'lucky', 'magenta', 'manual', 'marblemaxwell', 'mayor', 'monarch', 'monday', 'money', 'morningmother', 'mystery', 'native', 'nectar', 'nelson', 'networknikita', 'nobel', 'nobody', 'nominal', 'norway', 'nothingnumber', 'october', 'office', 'oliver', 'opinion', 'optionorder', 'outside', 'package', 'pandora', 'panther', 'papapattern', 'pedro', 'pencil', 'people', 'phantom', 'philipspioneer', 'pluto', 'podium', 'portal', 'potato', 'processproxy', 'pupil', 'python', 'quality', 'quarter', 'quietrabbit', 'radical', 'radius', 'rainbow', 'ramirez', 'ravioliraymond', 'respect', 'respond', 'result', 'resume', 'richardriver', 'roger', 'roman', 'rondo', 'sabrina', 'salarysalsa', 'sample', 'samuel', 'saturn', 'savage', 'scarletscorpio', 'sector', 'serpent', 'shampoo', 'sharon', 'silencesimple', 'society', 'sonar', 'sonata', 'soprano', 'spartaspider', 'sponsor', 'abraham', 'action', 'active', 'actoradam', 'address', 'admiral', 'adrian', 'agenda', 'agentairline', 'airport', 'alabama', 'aladdin', 'alarm', 'algebraalibi', 'alice', 'alien', 'almond', 'alpine', 'amberamigo', 'ammonia', 'analyze', 'anatomy', 'angel', 'annualanswer', 'apple', 'archive', 'arctic', 'arena', 'arizonaarmada', 'arnold', 'arsenal', 'arthur', 'asia', 'aspectathena', 'audio', 'august', 'austria', 'avenue', 'averageaxiom', 'aztec', 'bagel', 'baker', 'balance', 'balladballet', 'bambino', 'bamboo', 'baron', 'basic', 'basketbattery', 'belgium', 'benefit', 'berlin', 'bermuda', 'bernardbicycle', 'binary', 'biology', 'bishop', 'blitz', 'blockblonde', 'bonjour', 'boris', 'boston', 'bottle', 'boxerbrandy', 'bravo', 'brazil', 'bridge', 'british', 'bronzebrown', 'bruce', 'bruno', 'brush', 'burger', 'burmacabinet', 'cactus', 'cafe', 'cairo', 'calypso', 'camelcampus', 'canal', 'cannon', 'canoe', 'cantina', 'canvascanyon', 'capital', 'caramel', 'caravan', 'career', 'cargocarlo', 'carol', 'carpet', 'cartel', 'cartoon', 'castlecastro', 'cecilia', 'cement', 'center', 'century', 'ceramicchamber', 'chance', 'change', 'chaos', 'charlie', 'charmcharter', 'cheese', 'chef', 'chemist', 'cherry', 'chesschicago', 'chicken', 'chief', 'china', 'cigar', 'circuscity', 'clara', 'classic', 'claudia', 'clean', 'clientclimax', 'clinic', 'clock', 'club', 'cockpit', 'coconutcola', 'collect', 'colombo', 'colony', 'color', 'combatcomedy', 'command', 'company', 'concert', 'connect', 'consulcontact', 'contour', 'control', 'convert', 'copy', 'cornercorona', 'correct', 'cosmos', 'couple', 'courage', 'cowboycraft', 'crash', 'cricket', 'crown', 'cuba', 'dallasdance', 'daniel', 'decade', 'decimal', 'degree', 'deletedeliver', 'delphi', 'deluxe', 'demand', 'demo', 'denmarkderby', 'design', 'detect', 'develop', 'diagram', 'diamonddiana', 'diego', 'diesel', 'diet', 'digital', 'dilemmadirect', 'disco', 'disney', 'distant', 'dollar', 'dolphindonald', 'drink', 'driver', 'dublin', 'duet', 'dynamicearth', 'east', 'ecology', 'economy', 'edgar', 'egyptelastic', 'elegant', 'element', 'elite', 'elvis', 'emailempty', 'energy', 'engine', 'english', 'episode', 'equatorescape', 'escort', 'ethnic', 'europe', 'everest', 'evidentexact', 'example', 'exit', 'exotic', 'export', 'expressfactor', 'falcon', 'family', 'fantasy', 'fashion', 'fiberfiction', 'fidel', 'fiesta', 'figure', 'film', 'filterfinance', 'finish', 'finland', 'first', 'flag', 'flashflorida', 'flower', 'fluid', 'flute', 'folio', 'fordforest', 'formal', 'formula', 'fortune', 'forward', 'fragilefrance', 'frank', 'fresh', 'friend', 'frozen', 'futuregabriel', 'gamma', 'garage', 'garcia', 'garden', 'garlicgemini', 'general', 'genetic', 'genius', 'germany', 'gloriagold', 'golf', 'gondola', 'gong', 'good', 'gordongorilla', 'grand', 'granite', 'graph', 'green', 'groupguide', 'guitar', 'guru', 'hand', 'happy', 'harborharvard', 'havana', 'hawaii', 'helena', 'hello', 'henryhilton', 'history', 'horizon', 'house', 'human', 'iconidea', 'igloo', 'igor', 'image', 'impact', 'importindia', 'indigo', 'input', 'insect', 'instant', 'irisitalian', 'jacket', 'jacob', 'jaguar', 'janet', 'jargonjazz', 'jeep', 'john', 'joker', 'jordan', 'judojumbo', 'june', 'jungle', 'junior', 'jupiter', 'karatekarma', 'kayak', 'kermit', 'king', 'koala', 'korealabor', 'lady', 'lagoon', 'laptop', 'laser', 'latinlava', 'lecture', 'left', 'legal', 'level', 'lexiconliberal', 'libra', 'lily', 'limbo', 'limit', 'lindalinear', 'lion', 'liquid', 'little', 'llama', 'lobbylobster', 'local', 'logic', 'logo', 'lola', 'londonlucas', 'lunar', 'machine', 'macro', 'madam', 'madonnamadrid', 'maestro', 'magic', 'magnet', 'magnum', 'mailboxmajor', 'mama', 'mambo', 'manager', 'manila', 'marcomarina', 'market', 'mars', 'martin', 'marvin', 'marymaster', 'matrix', 'maximum', 'media', 'medical', 'megamelody', 'memo', 'mental', 'mentor', 'mercury', 'messagemetal', 'meteor', 'method', 'mexico', 'miami', 'micromilk', 'million', 'minimum', 'minus', 'minute', 'miraclemirage', 'miranda', 'mister', 'mixer', 'mobile', 'modemmodern', 'modular', 'moment', 'monaco', 'monica', 'monitormono', 'monster', 'montana', 'morgan', 'motel', 'motifmotor', 'mozart', 'multi', 'museum', 'mustang', 'naturalneon', 'nepal', 'neptune', 'nerve', 'neutral', 'nevadanews', 'next', 'ninja', 'nirvana', 'normal', 'novanovel', 'nuclear', 'numeric', 'nylon', 'oasis', 'observeocean', 'octopus', 'olivia', 'olympic', 'omega', 'operaoptic', 'optimal', 'orange', 'orbit', 'organic', 'orientorigin', 'orlando', 'oscar', 'oxford', 'oxygen', 'ozonepablo', 'pacific', 'pagoda', 'palace', 'pamela', 'panamapancake', 'panda', 'panel', 'panic', 'paradox', 'pardonparis', 'parker', 'parking', 'parody', 'partner', 'passagepassive', 'pasta', 'pastel', 'patent', 'patient', 'patriotpatrol', 'pegasus', 'pelican', 'penguin', 'pepper', 'percentperfect', 'perfume', 'period', 'permit', 'person', 'peruphone', 'photo', 'picasso', 'picnic', 'picture', 'pigmentpilgrim', 'pilot', 'pixel', 'pizza', 'planet', 'plasmaplaza', 'pocket', 'poem', 'poetic', 'poker', 'polarispolice', 'politic', 'polo', 'polygon', 'pony', 'popcornpopular', 'postage', 'precise', 'prefix', 'premium', 'presentprice', 'prince', 'printer', 'prism', 'private', 'prizeproduct', 'profile', 'program', 'project', 'protect', 'protonpublic', 'pulse', 'puma', 'pump', 'pyramid', 'queenradar', 'ralph', 'random', 'rapid', 'rebel', 'recordrecycle', 'reflex', 'reform', 'regard', 'regular', 'relaxreptile', 'reverse', 'ricardo', 'right', 'ringo', 'riskritual', 'robert', 'robot', 'rocket', 'rodeo', 'romeoroyal', 'russian', 'safari', 'salad', 'salami', 'salmonsalon', 'salute', 'samba', 'sandra', 'santana', 'sardineschool', 'scoop', 'scratch', 'screen', 'script', 'scrollsecond', 'secret', 'section', 'segment', 'select', 'seminarsenator', 'senior', 'sensor', 'serial', 'service', 'shadowsharp', 'sheriff', 'shock', 'short', 'shrink', 'sierrasilicon', 'silk', 'silver', 'similar', 'simon', 'singlesiren', 'slang', 'slogan', 'smart', 'smoke', 'snakesocial', 'soda', 'solar', 'solid', 'solo', 'sonicsource', 'soviet', 'special', 'speed', 'sphere', 'spiralspirit', 'spring', 'static', 'status', 'stereo', 'stonestop', 'street', 'strong', 'student', 'style', 'sultansusan', 'sushi', 'suzuki', 'switch', 'symbol', 'systemtactic', 'tahiti', 'talent', 'tarzan', 'telex', 'texastheory', 'thermos', 'tiger', 'titanic', 'tomato', 'topictornado', 'toronto', 'torpedo', 'totem', 'tractor', 'traffictransit', 'trapeze', 'travel', 'tribal', 'trick', 'tridenttrilogy', 'tripod', 'tropic', 'trumpet', 'tulip', 'tunaturbo', 'twist', 'ultra', 'uniform', 'union', 'uraniumvacuum', 'valid', 'vampire', 'vanilla', 'vatican', 'velvetventura', 'venus', 'vertigo', 'veteran', 'victor', 'viennaviking', 'village', 'vincent', 'violet', 'violin', 'virtualvirus', 'vision', 'visitor', 'visual', 'vitamin', 'vivavocal', 'vodka', 'volcano', 'voltage', 'volume', 'voyagewater', 'weekend', 'welcome', 'western', 'window', 'winterwizard', 'wolf', 'world', 'xray', 'yankee', 'yogayogurt', 'yoyo', 'zebra', 'zero', 'zigzag', 'zipperzodiac', 'zoom', 'acid', 'adios', 'agatha', 'alamoalert', 'almanac', 'aloha', 'andrea', 'anita', 'arcadeaurora', 'avalon', 'baby', 'baggage', 'balloon', 'bankbasil', 'begin', 'biscuit', 'blue', 'bombay', 'botanicbrain', 'brenda', 'brigade', 'cable', 'calibre', 'carmencello', 'celtic', 'chariot', 'chrome', 'citrus', 'civilcloud', 'combine', 'common', 'cool', 'copper', 'coralcrater', 'cubic', 'cupid', 'cycle', 'depend', 'doordream', 'dynasty', 'edison', 'edition', 'enigma', 'equaleric', 'event', 'evita', 'exodus', 'extend', 'famousfarmer', 'food', 'fossil', 'frog', 'fruit', 'genevagentle', 'george', 'giant', 'gilbert', 'gossip', 'gramgreek', 'grille', 'hammer', 'harvest', 'hazard', 'heavenherbert', 'heroic', 'hexagon', 'husband', 'immune', 'incainch', 'initial', 'isabel', 'ivory', 'jason', 'jeromejoel', 'joshua', 'journal', 'judge', 'juliet', 'jumpjustice', 'kimono', 'kinetic', 'leonid', 'leopard', 'limamaze', 'medusa', 'member', 'memphis', 'michael', 'miguelmilan', 'mile', 'miller', 'mimic', 'mimosa', 'missionmonkey', 'moral', 'moses', 'mouse', 'nancy', 'natashanebula', 'nickel', 'nina', 'noise', 'orchid', 'oreganoorigami', 'orinoco', 'orion', 'othello', 'paper', 'paprikaprelude', 'prepare', 'pretend', 'promise', 'prosper', 'providepuzzle', 'remote', 'repair', 'reply', 'rival', 'rivierarobin', 'rose', 'rover', 'rudolf', 'saga', 'saharascholar', 'shelter', 'ship', 'shoe', 'sigma', 'sistersleep', 'smile', 'spain', 'spark', 'split', 'spraysquare', 'stadium', 'star', 'storm', 'story', 'strangestretch', 'stuart', 'subway', 'sugar', 'sulfur', 'summersurvive', 'sweet', 'swim', 'table', 'taboo', 'targetteacher', 'telecom', 'temple', 'tibet', 'ticket', 'tinatoday', 'toga', 'tommy', 'tower', 'trivial', 'tunnelturtle', 'twin', 'uncle', 'unicorn', 'unique', 'updatevalery', 'vega', 'version', 'voodoo', 'warning', 'williamwonder', 'year', 'yellow', 'young', 'absent', 'absorbabsurd', 'accent', 'alfonso', 'alias', 'ambient', 'anagramandy', 'anvil', 'appear', 'apropos', 'archer', 'arielarmor', 'arrow', 'austin', 'avatar', 'axis', 'baboonbahama', 'bali', 'balsa', 'barcode', 'bazooka', 'beachbeast', 'beatles', 'beauty', 'before', 'benny', 'bettybetween', 'beyond', 'billy', 'bison', 'blast', 'blessbogart', 'bonanza', 'book', 'border', 'brave', 'breadbreak', 'broken', 'bucket', 'buenos', 'buffalo', 'bundlebutton', 'buzzer', 'byte', 'caesar', 'camilla', 'canarycandid', 'carrot', 'cave', 'chant', 'child', 'choicechris', 'cipher', 'clarion', 'clark', 'clever', 'cliffclone', 'conan', 'conduct', 'congo', 'costume', 'cottoncover', 'crack', 'current', 'danube', 'data', 'decidedeposit', 'desire', 'detail', 'dexter', 'dinner', 'donordruid', 'drum', 'easy', 'eddie', 'enjoy', 'enricoepoxy', 'erosion', 'except', 'exile', 'explain', 'famefast', 'father', 'felix', 'field', 'fiona', 'firefish', 'flame', 'flex', 'flipper', 'float', 'floodfloor', 'forbid', 'forever', 'fractal', 'frame', 'freddiefront', 'fuel', 'gallop', 'game', 'garbo', 'gategelatin', 'gibson', 'ginger', 'giraffe', 'gizmo', 'glassgoblin', 'gopher', 'grace', 'gray', 'gregory', 'gridgriffin', 'ground', 'guest', 'gustav', 'gyro', 'hairhalt', 'harris', 'heart', 'heavy', 'herman', 'hippiehobby', 'honey', 'hope', 'horse', 'hostel', 'hydroimitate', 'info', 'ingrid', 'inside', 'invent', 'investinvite', 'ivan', 'james', 'jester', 'jimmy', 'joinjoseph', 'juice', 'julius', 'july', 'kansas', 'karlkevin', 'kiwi', 'ladder', 'lake', 'laura', 'learnlegacy', 'legend', 'lesson', 'life', 'light', 'listlocate', 'lopez', 'lorenzo', 'love', 'lunch', 'maltamammal', 'margin', 'margo', 'marion', 'mask', 'matchmayday', 'meaning', 'mercy', 'middle', 'mike', 'mirrormodest', 'morph', 'morris', 'mystic', 'nadia', 'natonavy', 'needle', 'neuron', 'never', 'newton', 'nicenight', 'nissan', 'nitro', 'nixon', 'north', 'oberonoctavia', 'ohio', 'olga', 'open', 'opus', 'orcaoval', 'owner', 'page', 'paint', 'palma', 'parentparlor', 'parole', 'paul', 'peace', 'pearl', 'performphoenix', 'phrase', 'pierre', 'pinball', 'place', 'plateplato', 'plume', 'pogo', 'point', 'polka', 'ponchopowder', 'prague', 'press', 'presto', 'pretty', 'primepromo', 'quest', 'quick', 'quiz', 'quota', 'racerachel', 'raja', 'ranger', 'region', 'remark', 'rentreward', 'rhino', 'ribbon', 'rider', 'road', 'rodentround', 'rubber', 'ruby', 'rufus', 'sabine', 'saddlesailor', 'saint', 'salt', 'scale', 'scuba', 'seasonsecure', 'shake', 'shallow', 'shannon', 'shave', 'shelfsherman', 'shine', 'shirt', 'side', 'sinatra', 'sinceresize', 'slalom', 'slow', 'small', 'snow', 'sofiasong', 'sound', 'south', 'speech', 'spell', 'spendspoon', 'stage', 'stamp', 'stand', 'state', 'stellastick', 'sting', 'stock', 'store', 'sunday', 'sunsetsupport', 'supreme', 'sweden', 'swing', 'tape', 'tavernthink', 'thomas', 'tictac', 'time', 'toast', 'tobaccotonight', 'torch', 'torso', 'touch', 'toyota', 'tradetribune', 'trinity', 'triton', 'truck', 'trust', 'typeunder', 'unit', 'urban', 'urgent', 'user', 'valuevendor', 'venice', 'verona', 'vibrate', 'virgo', 'visiblevista', 'vital', 'voice', 'vortex', 'waiter', 'watchwave', 'weather', 'wedding', 'wheel', 'whiskey', 'wisdomandroid', 'annex', 'armani', 'cake', 'confide', 'dealdefine', 'dispute', 'genuine', 'idiom', 'impress', 'includeironic', 'null', 'nurse', 'obscure', 'prefer', 'prodigyego', 'fax', 'jet', 'job', 'rio', 'ski', 'yes']

def generate_mnemonic_phrase(length):
    result = ''
    for i in range(length):
        result += random.choice(get_mnemonic_data()) + ' '
    return result

def enc_sha256(hash_string):
    return hashlib.sha256(hash_string.encode()).hexdigest()

def dec_sha256(enc):
    return hashlib.sha256(enc.decode()).hexdigest()



# Phrase
d = 'VkcqbwWTo0nVhnTE+dkILOgY8M5EytQESdy7HfqnLPg8ythKpjY5pPC3ALMlsg3c'
token = '1234567890abcdefghijklmnopqrtsuvwxyz'
key = enc_sha256(token)[10:26]
# key = generate_mnemonic_phrase(length=15)
# phrase = AESCipher(key).encrypt(key)
print(key)
a = AESCipher(key).decrypt(d)
print(a)
# print(key)
# print(phrase)
#
# seed = genb58seed(phrase)
# print seed
#
# # seed_mn = seed2mnemonic(seed)
# mn_seed = mnemonic2seed(key)
# # print(seed_mn)
# print(mn_seed)

# Entropy
# entropy = phrase
# entropy = hashlib.sha256(entropy + int2data(ecdsa.util.randrange( 2**128 ), 16)).digest()[:16]
# print(entropy)

# print(dec)

# Seed
# sk = SigningKey.generate(curve=ecdsa.SECP256k1)
# vk = sk.get_verifying_key()
# sig = sk.sign(b"message")
# # vk_string = vk.to_string()
# # vk2 = VerifyingKey.from_string(vk_string, curve=ecdsa.SECP256k1)
# encoded_string = base58.b58encode(sk.to_string())
# print(sk)
# print(vk)
# # print(vk2)
# print(sig)
# print(encoded_string)
# print vk.verify(sig, b"message")

# Seed 2

# seed = genb58seed(enc)
# fpgadd, accadd, accid = seed2accid(seed)
#
# print(seed)
# print(fpgadd)
# print(accadd)
# print(accid)


# Seed_hash
# enc_256 = enc_sha256(key)
# dec_256 = dec_sha256(enc_256)
# print(key)
# print(enc_256)
# print(dec_256)

# wordcount = 1626

# Note about US patent no 5892470: Here each word does not represent a given digit.
# Instead, the digit represented by a word is variable, it depends on the previous word.

# def mn_encode( message ):
#     assert len(message) % 8 == 0
#     out = []
#     for i in range(len(message)/8):
#         word = message[8*i:8*i+8]
#         x = int(word, 16)
#         w1 = (x%wordcount)
#         w2 = ((x/wordcount) + w1)%wordcount
#         w3 = ((x/wordcount/wordcount) + w2)%wordcount
#         out += [ words[w1], words[w2], words[w3] ]
#     return out
#
# def mn_decode( wlist ):
#     out = ''
#     for i in range(len(wlist)/3):
#         word1, word2, word3 = wlist[3*i:3*i+3]
#         w1 =  words.index(word1)
#         w2 = (words.index(word2))%wordcount
#         w3 = (words.index(word3))%wordcount
#         x = w1 +wordcount*((w2-w1)%wordcount) +wordcount*wordcount*((w3-w2)%wordcount)
#         out += '%08x'%x
#     return out
