import os
import cwcn_instruments

# ACTIVE_PAIRS = [__ for __ in list(cwcn_instruments.POLONIEX_MAP.values()) if 'USDT_' in __]
# print(ACTIVE_PAIRS)
# input("stop!")
PH1_KEMU_MIN_VELOCITY=10 # in seconds
FARM_CONFIG_FOLDER='{}/../wajyu_data_farm/FARM'.format(os.path.dirname(os.path.abspath(__file__)))
FARM_CONFIG_EXTENSION='.poloniexdata'
# --- --- --- --- --- --- 
PAPER_TRADING = True
# --- --- --- --- --- --- 
class WAJYU_KEMU_CONFIG:
    _instrument_filters = [
        (lambda km: km._velocity is not None and km._velocity <= PH1_KEMU_MIN_VELOCITY),
        (lambda km: [not km._load_phils[__]['loop_failure'] for __ in list(km._load_phils.keys())])
    ]
    _data_interpret_map = { # very much carefull, depends on the state
        'instrument':0,
        'price':1,
        'price.delta':2,
        'timestamp':-1,
        'lowprice_24':-4,
        'highprice_24':-5,
        'highest_bid':-10,
        'lowest_ask':-11,
    }
    class PHI1:
        phi1_shang_HOURS_HORIZONS = [ # (SEQ_LEN, #HOURS)
            (450,1.5),
            (300,1),
            (150,0.5),
            (30,0.1),
        ]
        dafult_value=0.0
    class PHI2:
        phi2_shang_HOURS_HORIZON = 1
        phi2_xia_HOURS_HORIZON = 1
        phi2_shang_SEQ_LEN = 300
        phi2_xia_SEQ_LEN = int(phi2_shang_SEQ_LEN*phi2_xia_HOURS_HORIZON/phi2_shang_HOURS_HORIZON)
        class phi2_HILBER_CONFIG:
            phi2_hilbert_s = 0.25
            phi2_hilbert_n = 12
            phi2_base = 'tanh'
class WAJYU_WIKIMYEI_CONFIG:
    # --- --- --- 
    ACTIVE_AHPA=['long','short']
    UWAABO_NEAR_PERIOD_HOURS=0.0 # how often to update positions [in hours]
    # --- --- --- 
    RISK_INSTRUMENT_CAPITAL={
        'risk.long':20.0, # the capital to put in every instrument
        'risk.short':20.0, # the capital to put in every instrument
    }
    BREAK_SCORE={
        'break_score.long':0.5,
        'break_score.short':3.5,
    }
    HALT_SCORE={
        'halt_score.long':0.15, # in terms of score, how much score adventaje to shift (replace) positions
        'halt_score.short':1.5, # in terms of score, how much score adventaje to shift (replace) positions
    }
    MINIMUN_HOLDING_BALANCE={
        'min_hold_balance.long':5.0, # in USDT
        'min_hold_balance.short':5.0, # in USDT
    }
    class SIMULATION:
        initial_balance=200.0 # in USDT (the same for all _acta)
        buy_comission=0.01 # in % meaning [from 100 to 0] (the same for all instruments (active_pairs))
        sell_comission=0.01 # in % meaning [from 100 to 0] (the same for all instruments (active_pairs))
class CWCN_COLORS:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GOOD = '\033[92m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    REGULAR = '\033[0m'
    GROSS = '\033[1m'
    DANGER = '\033[41m'
    RED = '\033[31m'
    BAD = '\033[31m'
    UNDERLINE = '\033[4m'
    PRICE = '\033[0;32m'
    YELLOW = '\033[1;33m'
    DARKGRAY = '\033[1;30m'
    GRAY = '\033[0;37m'
    WHITE = '\033[1;37m'
    COLOR_ACTA = {
        'color.long':'\033[44m',
        'color.short':'\033[41m',
    }
class CWCN_CURSOR: #FIXME not in use
    UP='\033[A'
    DOWN='\033[B'
    LEFT='\033[D'
    RIGHT='\033[C'
    CLEAR_LINE='\033[K'
    CARRIER_RETURN='\r'
    NEW_LINE='\n'



ACTIVE_PAIRS = [
    'USDT_DYDX',
    'USDT_AAVE',
    'USDT_ADABULL',
    'USDT_ALICE',
    # 'USDT_API3',
    'USDT_ATOM',
    # 'USDT_AVA',
    'USDT_AXS',
    'USDT_BAT',
    'USDT_BCH',
    # 'USDT_BCHBULL',
    # 'USDT_BCHSV',
    'USDT_BEAR',
    # 'USDT_BID',
    'USDT_BNB',
    # 'USDT_BSVBULL',
    'USDT_BTC',
    'USDT_BTT',
    'USDT_BULL',
    # 'USDT_BZRX',
    # 'USDT_C98',
    'USDT_CHR',
    'USDT_CHZ',
    'USDT_DASH',
    # 'USDT_DEGO',
    'USDT_DOGE',
    'USDT_DOT',
    'USDT_ELON',
    'USDT_ENJ',
    'USDT_EOS',
    # 'USDT_EOSBEAR',
    # 'USDT_EOSBULL',
    'USDT_ETH',
    'USDT_ETHBULL',
    # 'USDT_FCT2',
    'USDT_FIL',
    'USDT_FRONT',
    'USDT_GALA',
    # 'USDT_GLYPH', # FENOMENAL!
    # 'USDT_GRT',
    # 'USDT_GTC',
    # 'USDT_HGET',
    'USDT_IDIA',
    # 'USDT_INJ',s
    'USDT_JST',
    'USDT_KLV',
    'USDT_LINK',
    'USDT_LINKBULL',
    'USDT_LPT',
    'USDT_LRC',
    'USDT_LTC',
    'USDT_LTCBEAR',
    'USDT_LTCBULL',
    'USDT_MANA',
    'USDT_MATIC',
    'USDT_MKR',
    'USDT_NEO',
    'USDT_NU',
    'USDT_OCEAN',
    'USDT_QTUM',
    'USDT_RD',
    'USDT_REEF',
    'USDT_REN',
    'USDT_RSR',
    'USDT_SAND',
    'USDT_SC',
    'USDT_SENSO',
    'USDT_SHIB',
    'USDT_SNX',
    'USDT_SRM',
    'USDT_STPT',
    'USDT_STR',
    'USDT_SUSHI',
    'USDT_SWINGBY',
    'USDT_SXP',
    'USDT_TOKE',
    'USDT_TRX',
    'USDT_TRXBULL',
    'USDT_TUSD',
    'USDT_UMA',
    'USDT_UNI',
    'USDT_WBTC',
    'USDT_WIN',
    'USDT_WNXM',
    'USDT_WOO',
    'USDT_WRX',
    'USDT_XCAD',
    'USDT_XEM',
    'USDT_XLMBEAR',
    'USDT_XLMBULL',
    'USDT_XMR',
    'USDT_XRP',
    'USDT_XRPBULL',
    'USDT_XTZ',
    'USDT_YFI',
    'USDT_YGG',
    'USDT_ZEC',
    'USDT_ZRX',
]

class WAJYU_FARM_CONFIG:
    RESET_FOLDER = True
    FARM_FOLDER = FARM_CONFIG_FOLDER
    FARM_EXTENSION = FARM_CONFIG_EXTENSION
    INSTRUMENT_FILES=dict([(__,
            os.path.join(FARM_CONFIG_FOLDER,'{}/{}{}'.format(
                __,__,
                FARM_CONFIG_EXTENSION))
        ) for __ in ACTIVE_PAIRS])
    FARM_WEBSOCKETS = [r'{"command": "subscribe", "channel": 1002}']