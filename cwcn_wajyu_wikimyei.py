# --- --- --- --- --- 
import os
import sys
import ast
import time
import sched
import subprocess
from datetime import datetime
# import importlib # importlib.reload(cwcn_dwve_client_config)
# --- --- --- --- --- 
import cwcn_instruments
import cwcn_wajyu_kemu
from cwcn_wjy_config import WAJYU_KEMU_CONFIG as wjykc
from cwcn_wjy_config import WAJYU_WIKIMYEI_CONFIG as wjywc
from cwcn_wjy_config import CWCN_COLORS as colrs
import cwcn_wjy_config as wjyc
# --- --- --- --- --- 
INSTRUMENT_MAP = cwcn_instruments.POLONIEX_MAP
INV_INSTRUMENT_MAP = dict([(INSTRUMENT_MAP[__],__) for __ in list(INSTRUMENT_MAP.keys())])
# --- --- --- --- --- 
def is_farm_active():
    return True #FIXME
assert(is_farm_active())
# --- --- --- --- --- 
class WAJYU_WIKIMYEI:
    def __init__(self):
        self._uwaabo_schedule=sched.scheduler(time.time,time.sleep)
        self._reset()
        self._report()
    def _reset(self):
        self._instrument_kemu=dict([(__,cwcn_wajyu_kemu.PHI1_WAJYU_KEMU(__)) for __ in wjyc.ACTIVE_PAIRS])
        if(wjyc.PAPER_TRADING):
            self._wallet={}
            self._positions=dict([(_symb,{
                'symbol':_symb,
                'unit_price':self.fetch_instrument_price(_symb),
            }) for _symb in wjyc.ACTIVE_PAIRS])
            for _acta in wjywc.ACTIVE_AHPA:
                self._wallet.update({
                    'balance.{}'.format(_acta):wjywc.SIMULATION.initial_balance
                })
                for _symb in wjyc.ACTIVE_PAIRS:
                    self._positions[_symb].update({
                        'score.{}'.format(_acta):None,
                        'quantity.{}'.format(_acta):0,
                    })
        else:
            assert(False),"[implement!]"
    # --- --- --- --- --- --- 
    def _report(self):
        def cal_color(val):
            return colrs.WARNING if val is None else colrs.GOOD if val>0 else colrs.BAD if val<0 else colrs.WARNING
        sys.stdout.write("--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- -/- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- \n")
        sys.stdout.write("[WAJYU WIKIMYEI REPORT:]\n")
        sys.stdout.write("\t: datetime:\t{}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        sys.stdout.write("[WALLET:]\n")
        for _acta in wjywc.ACTIVE_AHPA:
            sys.stdout.write("{}{}{}\t{}:{} balance  {}:{} {}{:.4f}{}\t[USDT]\n".format(
                colrs.COLOR_ACTA['color.{}'.format(_acta)],
                _acta,
                colrs.REGULAR,
                colrs.COLOR_ACTA['color.{}'.format(_acta)],
                colrs.REGULAR,
                colrs.COLOR_ACTA['color.{}'.format(_acta)],
                colrs.REGULAR,
                colrs.GOOD,
                self._wallet['balance.{}'.format(_acta)],
                colrs.REGULAR))
            sys.stdout.write("{}{}{}\t{}:{} position {}:{} {}{:.4f}{}\t[USDT]\n".format(
                colrs.COLOR_ACTA['color.{}'.format(_acta)],
                _acta,
                colrs.REGULAR,
                colrs.COLOR_ACTA['color.{}'.format(_acta)],
                colrs.REGULAR,
                colrs.COLOR_ACTA['color.{}'.format(_acta)],
                colrs.REGULAR,
                colrs.GOOD,
                sum([_pos_state['quantity.{}'.format(_acta)]*self.fetch_instrument_price(_pos_symbol) for _pos_symbol,_pos_state in self._positions.items()]),
                colrs.REGULAR))
            
        sys.stdout.write("[POSITONS:]\n")
        for _acta in wjywc.ACTIVE_AHPA:
            flg_aux=False
            sys.stdout.write("--- ---  {}·{}  --- --- \n".format(colrs.COLOR_ACTA['color.{}'.format(_acta)],colrs.REGULAR))
            for _pos_symbol, _pos_state in self._positions.items():
                if(_pos_state['quantity.{}'.format(_acta)]>0):
                    flg_aux=True
                    sys.stdout.write(
                        f"""\
{colrs.COLOR_ACTA['color.{}'.format(_acta)]}{_acta}{colrs.REGULAR}\t \
[{_pos_symbol}]\t\
{colrs.COLOR_ACTA['color.{}'.format(_acta)]}:{colrs.REGULAR} \
{colrs.WARNING}{_pos_state['quantity.{}'.format(_acta)]:.10f}{colrs.REGULAR} [satoshi]\t\
{colrs.COLOR_ACTA['color.{}'.format(_acta)]}:{colrs.REGULAR} \
{cal_color(_pos_state['quantity.{}'.format(_acta)]*self.fetch_instrument_price(_pos_symbol)-wjywc.RISK_INSTRUMENT_CAPITAL['risk.{}'.format(_acta)])}{_pos_state['quantity.{}'.format(_acta)]*self.fetch_instrument_price(_pos_symbol):.2f}{colrs.REGULAR} [usdt]\t\
{colrs.COLOR_ACTA['color.{}'.format(_acta)]}:{colrs.REGULAR} \
{cal_color(_pos_state['score.{}'.format(_acta)])}{'' if _pos_state['score.{}'.format(_acta)]<0 else ' '}{_pos_state['score.{}'.format(_acta)]:.2f}{colrs.REGULAR} \
[{colrs.COLOR_ACTA['color.{}'.format(_acta)]}{_acta}{colrs.REGULAR}.score]\t\
{colrs.COLOR_ACTA['color.{}'.format(_acta)]}:{colrs.REGULAR} \
{self._instrument_kemu[_pos_symbol]._ph1_short_report()} [phi1.kemu]\n""")
            if(not flg_aux):
                sys.stdout.write("\t: [{}None!{}] \n".format(colrs.WARNING,colrs.REGULAR))
        sys.stdout.write("--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- -\- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- \n")
        sys.stdout.flush()
    # --- --- --- --- --- --- 
    def fetch_instrument_state(self,_symb):
        seq_aux=subprocess.check_output(['tail', '-{}'.format(1),wjyc.WAJYU_FARM_CONFIG.INSTRUMENT_FILES[_symb]]).decode('ascii').replace('\n','')
        return ast.literal_eval(seq_aux)
    def fetch_instrument_price(self,_symb):
        return self.fetch_instrument_state(_symb)[wjykc._data_interpret_map['price']]
    def fetch_instrument_best_bid(self,_symb):
        return self.fetch_instrument_state(_symb)[wjykc._data_interpret_map['highest_bid']]
    def fetch_instrument_best_ask(self,_symb):
        return self.fetch_instrument_state(_symb)[wjykc._data_interpret_map['lowest_ask']]
    # --- --- --- --- --- --- 
    def buy_instrument(self,_symb,_acta,capital=None,quantity=None):
        assert((capital is not None or quantity is not None) and (capital is None or quantity is None)), "[ERROR!] for BUY method set quantity or capital input"
        if(capital is None):
            assert(isinstance(quantity,float)),"[ERROR!] quantity must be a float"
            quantity=round(quantity,10)
            capital=self.fetch_instrument_best_bid(_symb)*quantity
        if(quantity is None):
            assert(isinstance(capital,float)),"[ERROR!] capital must be a float"
            quantity=capital/self.fetch_instrument_best_bid(_symb)
            quantity=round(quantity,10)
        if(wjyc.PAPER_TRADING):
            aplied_comission=capital*wjywc.SIMULATION.buy_comission/100
            if(self._wallet['balance.{}'.format(_acta)]<aplied_comission+capital):
                print('{}{}{} \t· [BUY:] [{}] \t: \t \t \t: {}FAILURE{}'.format(colrs.COLOR_ACTA['color.{}'.format(_acta)],_acta,colrs.REGULAR,_symb,colrs.BAD,colrs.REGULAR))
                return (False,'{}{}{} \t· [BUY:] [{}] \t: \t \t \t: {}FAILURE{}'.format(colrs.COLOR_ACTA['color.{}'.format(_acta)],_acta,colrs.REGULAR,_symb,colrs.BAD,colrs.REGULAR))
            else:
                self._wallet['balance.{}'.format(_acta)]-=aplied_comission+capital
                self._positions[_symb]['quantity.{}'.format(_acta)]+=quantity
                print('{}{}{} \t· [BUY:] [{}] \t: AMOUNT: {:.10f}   \t: {}SUCCESS{} \t: EXPENDED : {}{:.2f}{} [USDT]'.format(colrs.COLOR_ACTA['color.{}'.format(_acta)],_acta,colrs.REGULAR,_symb,quantity,colrs.GOOD,colrs.REGULAR,colrs.BAD,-(aplied_comission+capital),colrs.REGULAR))
                return (True,'{}{}{} \t· [BUY:] [{}] \t: AMOUNT: {:.10f}   \t: {}SUCCESS{} \t: EXPENDED : {}{:.2f}{} [USDT]'.format(colrs.COLOR_ACTA['color.{}'.format(_acta)],_acta,colrs.REGULAR,_symb,quantity,colrs.GOOD,colrs.REGULAR,colrs.BAD,-(aplied_comission+capital),colrs.REGULAR))
        else:
            assert(False),"[implement!]"
    def sell_instrument(self,_symb,_acta,quantity=None):
        quantity=quantity if quantity is not None else self._positions[_symb]['quantity.{}'.format(_acta)]
        if(self._positions[_symb]['quantity.{}'.format(_acta)]<=0):
            print('{}{}{} \t· [SELL:] [{}] \t: \t \t \t: {}FAILURE{} : INSUFFICIENT QUANTITY (nothing to sell)'.format(colrs.COLOR_ACTA['color.{}'.format(_acta)],_acta,colrs.REGULAR,_symb,colrs.BAD,colrs.REGULAR))
            return (False,'{}{}{} \t· [SELL:] [{}] \t: \t \t \t: {}FAILURE{} : INSUFFICIENT QUANTITY (nothing to sell)'.format(colrs.COLOR_ACTA['color.{}'.format(_acta)],_acta,colrs.REGULAR,_symb,colrs.BAD,colrs.REGULAR))
        capital=self.fetch_instrument_best_ask(_symb)*quantity
        aplied_comission=capital*wjywc.SIMULATION.sell_comission/100
        if(self._wallet['balance.{}'.format(_acta)]<aplied_comission):
            print('{}{}{} \t· [SELL:] [{}] \t: \t \t \t: {}FAILURE{} : INSUFFICIENT BALANCE'.format(colrs.COLOR_ACTA['color.{}'.format(_acta)],_acta,colrs.REGULAR,_symb,colrs.BAD,colrs.REGULAR))
            return (False,'{}{}{} \t· [SELL:] [{}] \t: \t \t \t: {}FAILURE{} : INSUFFICIENT BALANCE'.format(colrs.COLOR_ACTA['color.{}'.format(_acta)],_acta,colrs.REGULAR,_symb,colrs.BAD,colrs.REGULAR))
        else:
            self._wallet['balance.{}'.format(_acta)]+=capital-aplied_comission
            self._positions[_symb]['quantity.{}'.format(_acta)]-=quantity
            print('{}{}{} \t· [SELL:] [{}] \t: AMOUNT: {:.10f}   \t: {}SUCCESS{} \t: PROFIT : {}{}{} [USDT]'.format(colrs.COLOR_ACTA['color.{}'.format(_acta)],_acta,colrs.REGULAR,_symb,quantity,colrs.GOOD,colrs.REGULAR,colrs.GOOD,capital-aplied_comission,colrs.REGULAR))
            return (True,'{}{}{} \t· [SELL:] [{}] \t: AMOUNT: {:.10f}   \t: {}SUCCESS{} \t: PROFIT : {}{}{} [USDT]'.format(colrs.COLOR_ACTA['color.{}'.format(_acta)],_acta,colrs.REGULAR,_symb,quantity,colrs.GOOD,colrs.REGULAR,colrs.GOOD,capital-aplied_comission,colrs.REGULAR))
    def compute_kemu_instrument(self,_symb):
        self._instrument_kemu[_symb]._phi1_uwaabo()
        for _acta in wjywc.ACTIVE_AHPA:
            self._positions[_symb]['score.{}'.format(_acta)]=self._instrument_kemu[_symb].__dict__['_ph1_{}_score'.format(_acta)]
    def uwaabo_shift_in(self,_acta): # change -good into +good
        if(self._wallet['balance.{}'.format(_acta)]>=wjywc.MINIMUN_HOLDING_BALANCE['min_hold_balance.{}'.format(_acta)]+wjywc.RISK_INSTRUMENT_CAPITAL['risk.{}'.format(_acta)]):
            self.uwaabo_break_in(_acta)
        viable_instruments=[(__,self._positions[__]) for __ in wjyc.ACTIVE_PAIRS if self._positions[__]["score.{}".format(_acta)]>=wjywc.BREAK_SCORE['break_score.{}'.format(_acta)]]# and __ not in [_ki[0] for _ki in in_instruments]]
        viable_instruments=sorted(viable_instruments,key=lambda x:x[1]["score.{}".format(_acta)],reverse=True)
        for viable_simbol,viable_pos in viable_instruments:
            in_instruments=[(__,self._positions[__]) for __ in list(self._positions.keys()) if self._positions[__]['quantity.{}'.format(_acta)] > 0]
            in_instruments=sorted(in_instruments,key=lambda x:x[1]["score.{}".format(_acta)],reverse=False)
            if(self._wallet['balance.{}'.format(_acta)]>=wjywc.MINIMUN_HOLDING_BALANCE['min_hold_balance.{}'.format(_acta)]+wjywc.RISK_INSTRUMENT_CAPITAL['risk.{}'.format(_acta)]): # able to buy new instrument
                if(viable_simbol not in [_ki[0] for _ki in in_instruments]): # there is not position on viable instrument
                    for in_symbol, in_pos in in_instruments:
                        if(viable_pos["score.{}".format(_acta)]>in_pos["score.{}".format(_acta)]+wjywc.HALT_SCORE['halt_score.{}'.format(_acta)]):
                            self.sell_instrument(viable_simbol,_acta,quantity=None)
                            self.buy_instrument(in_symbol,_acta,capital=wjywc.RISK_INSTRUMENT_CAPITAL['risk.{}'.format(_acta)],quantity=None)
    def uwaabo_break_in(self,_acta): # get into good positions
        viable_instruments=[(__,self._positions[__]) for __ in wjyc.ACTIVE_PAIRS if self._positions[__]["score.{}".format(_acta)]>=wjywc.BREAK_SCORE['break_score.{}'.format(_acta)]]# and __ not in [_ki[0] for _ki in in_instruments]]
        viable_instruments=sorted(viable_instruments,key=lambda x:x[1]["score.{}".format(_acta)],reverse=True)
        for i_key,i_pos in viable_instruments:
            in_instruments=[(__,self._positions[__]) for __ in list(self._positions.keys()) if self._positions[__]['quantity.{}'.format(_acta)] > 0]
            in_instruments=sorted(in_instruments,key=lambda x:x[1]["score.{}".format(_acta)],reverse=True)
            if(self._wallet['balance.{}'.format(_acta)]>=wjywc.MINIMUN_HOLDING_BALANCE['min_hold_balance.{}'.format(_acta)]+wjywc.RISK_INSTRUMENT_CAPITAL['risk.{}'.format(_acta)]): # able to buy new instrument
                if(i_key not in [_ki[0] for _ki in in_instruments]):
                    self.buy_instrument(i_key,_acta,capital=wjywc.RISK_INSTRUMENT_CAPITAL['risk.{}'.format(_acta)],quantity=None)
    def uwaabo_break_out(self,_acta): # get out of bad positions
        in_instruments=[(__,self._positions[__]) for __ in list(self._positions.keys()) if self._positions[__]['quantity.{}'.format(_acta)] > 0]
        in_instruments=sorted(in_instruments,key=lambda x:x[1]["score.{}".format(_acta)],reverse=False)
        for __i,__p in in_instruments:
            if(self._positions[__i]["score.{}".format(_acta)]<wjywc.BREAK_SCORE['break_score.{}'.format(_acta)]):
                self.sell_instrument(__i,_acta,quantity=None)
    def uwaabo_step(self):
        self._uwaabo_schedule.enter(wjywc.UWAABO_NEAR_PERIOD_HOURS*60*60,1,self.uwaabo_step)
        # self._uwaabo_schedule.run()
        for _symb in wjyc.ACTIVE_PAIRS:
            self.compute_kemu_instrument(_symb)
        for _acta in wjywc.ACTIVE_AHPA:
            self.uwaabo_break_out(_acta)
            self.uwaabo_break_in(_acta)
            self.uwaabo_shift_in(_acta)
        self._report()
    def uwaabo_loop(self):
        self._uwaabo_schedule.enter(0,1,self.uwaabo_step)
        self._uwaabo_schedule.run()
if __name__=='__main__':
    ww=WAJYU_WIKIMYEI()
    ww.uwaabo_loop()