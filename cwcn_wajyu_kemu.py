# --- --- --- --- --- 
import os
import sys
import ast
import time
import numpy
import subprocess
# import importlib # importlib.reload(cwcn_dwve_client_config)
# --- --- --- --- --- 
import cwcn_instruments
from cwcn_wjy_config import WAJYU_KEMU_CONFIG as wjykc
from cwcn_wjy_config import CWCN_COLORS as colrs
import cwcn_wjy_config as wjyc
# --- --- --- --- --- 
INSTRUMENT_MAP = cwcn_instruments.POLONIEX_MAP
INV_INSTRUMENT_MAP = dict([(INSTRUMENT_MAP[__],__) for __ in list(INSTRUMENT_MAP.keys())])
# --- --- --- --- --- 
def assert_folder(_f_path):
    if(not os.path.isdir(_f_path)):
        os.mkdir(_f_path)
def purge_folder(_f_path):
    for _f in os.listdir(_f_path):
        for _f2 in os.listdir(os.path.join(_f_path,_f)):
            print("[PURGIN FILE:]",os.path.join(_f_path,_f,_f2))
            os.remove(os.path.join(_f_path,_f,_f2))
# --- --- --- --- --- 
def _hilbert_desing_matrix(x,h_type='linear'):
    assert(isinstance(x,numpy.ndarray)), "input to hilber desing mastrix must be 1d numpy array"
    # assert(x.shape==(wjykc.PHI2.phi2_shang_SEQ_LEN,1)), "input to hilbert must be of a valid size"
    _s=wjykc.PHI2.phi2_HILBER_CONFIG.phi2_hilbert_s
    _bh=numpy.linspace(-1,
        1, # 60*60*(wjykc.PHI2.phi2_shang_HOURS_HORIZON+wjykc.PHI2.phi2_xia_HOURS_HORIZON), #FIXME
        wjykc.PHI2.phi2_HILBER_CONFIG.phi2_hilbert_n)
    # x_h_matrix=numpy.copy(x)
    x_h_matrix=numpy.ones(x.shape,dtype='float')
    for __ in range(wjykc.PHI2.phi2_HILBER_CONFIG.phi2_hilbert_n):
        if(h_type in ['linear','lin']):
            _x=(x-_bh[__])/_s
        elif(h_type in ['gauss','norm']):
            _x=(x-_bh[__])**2/(2*(_s**2))
            _x=numpy.exp(-_x)
        elif(h_type in ['sig','sigmoid']):
            _x=(x-_bh[__])/_s
            _x=1/(1+numpy.exp(-_x))
        elif(h_type in ['tanh']):
            _x=(x-_bh[__])/_s
            _x=numpy.tanh(_x)
        else:
            _str="[ERROR:] Unrecognized hilber basis : {}".format(h_type)
            assert(False), _str
        x_h_matrix=numpy.c_[x_h_matrix,_x]
    import matplotlib.pyplot as plt
    for __ in range(x_h_matrix.shape[1]):
        plt.plot(x,x_h_matrix[:,__])
    plt.show()
    return x_h_matrix
# --- --- --- --- --- 
def _regular_equiparts(seq_aux,shang_hours,shang_seq_len):
    act_time=seq_aux[-1][wjykc._data_interpret_map['timestamp']]
    seq_out=[]
    for __ in seq_aux:
        if(__[wjykc._data_interpret_map['timestamp']]-act_time<=60*60*shang_hours):
            seq_out.append(__)
    for _idx,__ in enumerate(seq_out):
        seq_out[_idx][wjykc._data_interpret_map['timestamp']]=\
            seq_out[_idx][wjykc._data_interpret_map['timestamp']]\
            -seq_out[-1][wjykc._data_interpret_map['timestamp']]+1
    n=shang_seq_len
    lo=0
    hi=len(seq_out)
    linsp_index=[(hi - lo) // n * i + lo for i in range(n)] #linspace
    seq_out=[seq_out[__] for __ in linsp_index]
    norm_fact=abs(seq_out[0][wjykc._data_interpret_map['timestamp']])
    for c_idx,__ in enumerate(seq_out):
        seq_out[c_idx][wjykc._data_interpret_map['timestamp']]=seq_out[c_idx][wjykc._data_interpret_map['timestamp']]/norm_fact
        seq_out[c_idx][wjykc._data_interpret_map['timestamp']]=2*(seq_out[c_idx][wjykc._data_interpret_map['timestamp']]+0.5)
        # print(seq_out[c_idx][wjykc._data_interpret_map['timestamp']])
    return seq_out
# --- --- --- --- --- 
class PHI2_WAJYU_KEMU:
    def __init__(self,instrument):
        self._instrument=instrument
        self._inst_sequence=self._phi2_load_instrumen_state()
        self._inst_sequence=_regular_equiparts(
            seq_aux=self._inst_sequence,
            shang_hours=wjykc.PHI2.phi2_shang_HOURS_HORIZON,
            shang_seq_len=wjykc.PHI2.phi2_shang_SEQ_LEN)
        # print([__[wjykc._data_interpret_map['timestamp']] for __ in self._inst_sequence])
        self._xh_base=_hilbert_desing_matrix(
            x=numpy.array([[__[wjykc._data_interpret_map['timestamp']] for __ in self._inst_sequence]],dtype='float').transpose(),
            h_type=wjykc.PHI2.phi2_HILBER_CONFIG.phi2_base)
        self._wML=self._phi2_solve_maxLikelihood_by_moore_penrose_pseudo_inverse(
            _xh_base=self._xh_base,
            _yh_shang=numpy.array([[__[wjykc._data_interpret_map['price']] for __ in self._inst_sequence]],dtype='float').transpose())
        print("self._wML : {}".format(self._wML))
        print("self._xh_base (shape): {}".format(self._xh_base.shape))
        print("self._wML (shape): {}".format(self._wML.shape))
        self._phi2_plot_results()
        # wjykc.PHI2.phi2_shang_SEQ_LEN+wjykc.PHI2.phi2_xia_SEQ_LEN
    def _phi2_load_instrumen_state(self):
        c_n=1
        while True:
            act_time=int(time.time())
            seq_aux=subprocess.check_output(['tail', '-{}'.format(
                str(int(10*c_n*60*60*wjykc.PHI2.phi2_shang_HOURS_HORIZON))),
                wjyc.WAJYU_FARM_CONFIG.INSTRUMENT_FILES[self._instrument]]).decode('ascii').split('\n')
            seq_aux=[ast.literal_eval(__) for __ in seq_aux if __!='']
            # print(seq_aux)
            if(act_time-seq_aux[0][wjykc._data_interpret_map['timestamp']]>(60*60*wjykc.PHI2.phi2_shang_HOURS_HORIZON)):
                break
            if(c_n>100):
                assert(False), "[ERROR:] loading ph1 data"
            c_n+=1
        return seq_aux
    def _phi2_predict(self,_x):
        A=self._wML
        B=_hilbert_desing_matrix(x=_x,h_type=wjykc.PHI2.phi2_HILBER_CONFIG.phi2_base)
        C=numpy.dot(A.transpose(),B.transpose()).transpose()
        print(A.shape,B.shape,C.shape)
        return C
    def _phi2_solve_maxLikelihood_by_moore_penrose_pseudo_inverse(self,_xh_base,_yh_shang):
        return numpy.dot(numpy.dot(numpy.linalg.inv(numpy.dot(_xh_base.transpose(),_xh_base)),_xh_base.transpose()),_yh_shang)
    def _phi2_plot_results(self):
        import matplotlib.pyplot as plt
        _x=numpy.array([[__[wjykc._data_interpret_map['timestamp']] for __ in self._inst_sequence]],dtype='float').transpose()
        _xp=numpy.linspace(
            -1,
            1.5,
            wjykc.PHI2.phi2_shang_SEQ_LEN+wjykc.PHI2.phi2_xia_SEQ_LEN,
            dtype='float').transpose()
        _y=numpy.array([[__[wjykc._data_interpret_map['price']] for __ in self._inst_sequence]],dtype='float').transpose()
        _yp=self._phi2_predict(_xp)
        plt.plot(_x,_y)
        plt.plot(_xp,_yp)
        plt.show()
class PHI1_WAJYU_KEMU:
    def __init__(self,instrument):
        self._instrument=instrument
        self._velocity=None
        self._ph1_short_score=None
        self._ph1_long_score=None
    def _phi1_load_instrumen_state(self):
        self._load_phils={}
        for sq_hz_seq_len, sg_hz_hours in wjykc.PHI1.phi1_shang_HOURS_HORIZONS:
            self._load_phils[sg_hz_hours]={}
            c_n=1
            while True:
                try:
                    act_time=int(time.time())
                    seq_aux=subprocess.check_output(['tail', '-{}'.format(
                        str(int(5*c_n*60*60*sg_hz_hours))),
                        wjyc.WAJYU_FARM_CONFIG.INSTRUMENT_FILES[self._instrument]],
                        stderr=subprocess.DEVNULL).decode('ascii').split('\n')
                    seq_aux=[ast.literal_eval(__) for __ in seq_aux if __!='']
                    diff_aux = [__[wjykc._data_interpret_map['timestamp']] for __ in seq_aux]
                    diff_aux = numpy.diff(diff_aux)
                    self._velocity = numpy.mean(diff_aux)
                    if(act_time-seq_aux[0][wjykc._data_interpret_map['timestamp']]>(60*60*sg_hz_hours)):
                        self._load_phils[sg_hz_hours]['loop_failure']=False
                        break
                    c_n+=1
                    if(c_n>10):
                        # assert(False), "[ERROR:] loading ph1 data"
                        self._load_phils[sg_hz_hours]['loop_failure']=True
                        break
                except:
                    self._load_phils[sg_hz_hours]['loop_failure']=True
                    break
            if(self._load_phils[sg_hz_hours]['loop_failure']):
                self._load_phils[sg_hz_hours]['sequence']=None
                self._load_phils[sg_hz_hours]['intercep']=wjykc.PHI1.dafult_value
                self._load_phils[sg_hz_hours]['slope']=wjykc.PHI1.dafult_value
            else:
                self._load_phils[sg_hz_hours]['sequence']=_regular_equiparts(seq_aux=seq_aux,shang_hours=sg_hz_hours,shang_seq_len=sq_hz_seq_len)
                price_diff_hold = [__[wjykc._data_interpret_map['price']] for __ in self._load_phils[sg_hz_hours]['sequence']]
                for c_idx,__ in enumerate(self._load_phils[sg_hz_hours]['sequence']):
                    self._load_phils[sg_hz_hours]['sequence'][c_idx]=\
                        self._load_phils[sg_hz_hours]['sequence'][c_idx][:wjykc._data_interpret_map['price.delta']]\
                            +[price_diff_hold[c_idx]]\
                                +self._load_phils[sg_hz_hours]['sequence'][c_idx][wjykc._data_interpret_map['price.delta']:]
            # print(len(self._load_phils[sg_hz_hours]['sequence']))
        return self._load_phils
    def _phi1_uwaabo(self):
        self._phi1_load_instrumen_state()
        for _seq_key in list(self._load_phils.keys()):
            if(not self._load_phils[_seq_key]['loop_failure']):
                self._load_phils[_seq_key]['intercep'], self._load_phils[_seq_key]['slope'] = self._phi1_regressor(
                    _x=numpy.array([__[wjykc._data_interpret_map['timestamp']] for __ in self._load_phils[_seq_key]['sequence']],dtype='float'),
                    _y=numpy.array([__[wjykc._data_interpret_map['price.delta']] for __ in self._load_phils[_seq_key]['sequence']],dtype='float')
                )
            # print("key: {} :\t intercetp: {} : slope: {}".format(_seq_key, self._load_phils[_seq_key]['intercep'], self._load_phils[_seq_key]['slope']))
            # self._phi1_plot_results(self._load_phils[_seq_key])
        self._ph1_calculate_long_score()
        self._ph1_calculate_short_score()
    def _phi1_regressor(self, _x: numpy.ndarray, _y: numpy.ndarray):
        x=numpy.copy(_x)
        y=(numpy.copy(_y)-numpy.mean(_y))/(numpy.std(_y)+1e-5)
        dots = numpy.array(
            [
                x.shape[0],
                x.sum(),
                y.sum(),
                numpy.dot(x, x),
                numpy.dot(x, y),
            ]
        )
        size, sum_x, sum_y, sum_xx, sum_xy = dots
        det = size * sum_xx - sum_x ** 2
        if det > 1e-10:  # determinant may be zero initially
            intercept = (sum_xx * sum_y - sum_xy * sum_x) / det
            slope = (sum_xy * size - sum_x * sum_y) / det
            return intercept, slope
        else:
            return wjykc.PHI1.dafult_value,wjykc.PHI1.dafult_value 
    def _phi1_predict(self,c_x,c_intercept,c_slope):
        return c_slope*c_x+c_intercept
    def _ph1_calculate_long_score(self):
        if all([__(self) for __ in wjykc._instrument_filters]):
            self._ph1_long_score=0
            sum_keys=0.0
            for _seq_key in list(self._load_phils.keys()):
                if(self._load_phils[_seq_key]['slope']!=wjykc.PHI1.dafult_value):
                    self._ph1_long_score+=self._load_phils[_seq_key]['slope']*float(_seq_key)
                    sum_keys+=float(_seq_key)
            if(self._ph1_long_score==0):
                self._ph1_long_score=-999
            else:
                self._ph1_long_score/=sum_keys
        else:
            self._ph1_long_score=-999
        return self._ph1_long_score
    def _ph1_calculate_short_score(self):
        if all([__(self) for __ in wjykc._instrument_filters]):
            self._ph1_short_score=0
            sum_keys=0.0
            for _seq_key in list(self._load_phils.keys()):
                if(self._load_phils[_seq_key]['slope']!=wjykc.PHI1.dafult_value):
                    self._ph1_short_score+=self._load_phils[_seq_key]['slope']/float(_seq_key)
                    sum_keys+=float(_seq_key)
            if(self._ph1_short_score==0):
                self._ph1_short_score=-999
            else:
                self._ph1_short_score/=sum_keys
        else:
            self._ph1_short_score=-999
        return self._ph1_short_score
    def _ph1_short_report(self):
        def cal_color(val):
            return colrs.WARNING if val is None else colrs.GOOD if val>0 else colrs.BAD if val<0 else colrs.WARNING
        str_retn=""
        for _seq_key in list(self._load_phils.keys()):
            str_retn+=" {}:{}{}{:.2f}{} ··· ".format(
                _seq_key,
                cal_color(self._load_phils[_seq_key]['slope']),
                '' if self._load_phils[_seq_key]['slope']<0 else ' ',
                self._load_phils[_seq_key]['slope'],
                colrs.REGULAR)
        str_retn=str_retn[:-5]
        return str_retn
    def _ph1_report(self):
        def cal_color(val):
            return colrs.WARNING if val is None else colrs.GOOD if val>0 else colrs.BAD if val<0 else colrs.WARNING
        # if all([__(self) for __ in wjykc._instrument_filters]):
        sys.stdout.write("[{}]".format(self._instrument))
        sys.stdout.write("\t<{:.2f}[op/s]>".format(self._velocity))
        sys.stdout.write("\t<{}{}{:.2f}{}[s.scor]>".format(cal_color(self._ph1_short_score),'' if self._ph1_short_score<0 else ' ',self._ph1_short_score,colrs.REGULAR))
        sys.stdout.write("\t<{}{}{:.2f}{}[l.scor]>".format(cal_color(self._ph1_long_score),'' if self._ph1_long_score<0 else ' ',self._ph1_long_score,colrs.REGULAR))
        sys.stdout.write('\t')
        for _seq_key in list(self._load_phils.keys()):
            sys.stdout.write("\t{}[h] : {}{}{:.2f}{}\t".format(
                _seq_key,
                cal_color(self._load_phils[_seq_key]['slope']),
                '' if self._load_phils[_seq_key]['slope']<0 else ' ',
                self._load_phils[_seq_key]['slope'],
                colrs.REGULAR
            ))
        sys.stdout.write("\n")
        sys.stdout.flush()
    def _phi1_plot_results(self,sg_hz_hours):
        import matplotlib.pyplot as plt
        _x=numpy.array([[__[wjykc._data_interpret_map['timestamp']] for __ in self._load_phils[sg_hz_hours]['sequence']]],dtype='float').transpose()
        _y=numpy.array([[__[wjykc._data_interpret_map['price']] for __ in self._load_phils[sg_hz_hours]['sequence']]],dtype='float').transpose()
        _y=(numpy.copy(_y)-numpy.mean(_y))/(numpy.std(_y)+1e-5)
        _xp=numpy.linspace(
            -1,
            1.5,
            len(_x),
            dtype='float').transpose()
        _yp=self._phi1_predict(
            c_x=_xp,
            c_intercept=self._load_phils[sg_hz_hours]['intercep'],
            c_slope=self._load_phils[sg_hz_hours]['slope'])
        print("_x.shape: {} : _y.shape: {}".format(len(_x),len(_y)))
        print("_xp.shape: {} : _yp.shape: {}".format(_xp.shape,_yp.shape))
        plt.plot(_x,_y)
        plt.plot(_xp,_yp)
        plt.show()

if __name__=='__main__':
    while(True): # TESTING
        s_time=time.time()
        for __ in wjyc.ACTIVE_PAIRS:
            wk=PHI1_WAJYU_KEMU(__)
            wk._phi1_uwaabo()
            wk._ph1_report()
            # wk._phi1_plot_results(1)
        print(time.time()-s_time)

