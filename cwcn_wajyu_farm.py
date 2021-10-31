# --- --- --- --- --- 
import websocket
import _thread
import time
import ast
import os
# --- --- --- --- --- 
import cwcn_instruments
import cwcn_wjy_config
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
assert_folder(cwcn_wjy_config.WAJYU_FARM_CONFIG.FARM_FOLDER)
if(cwcn_wjy_config.WAJYU_FARM_CONFIG.RESET_FOLDER):
    purge_folder(cwcn_wjy_config.WAJYU_FARM_CONFIG.FARM_FOLDER)
# --- --- --- --- --- 
websocket.enableTrace(False)
# --- --- --- --- --- 
class WAJYU_DATA_FARM:
    def __init__(self):
        self.farm_websockets=cwcn_wjy_config.WAJYU_FARM_CONFIG.FARM_WEBSOCKETS
        self.ws = websocket.WebSocketApp("wss://api2.poloniex.com",
                                on_open=self.on_open,
                                on_message=self.on_message,
                                on_error=self.on_error,
                                on_close=self.on_close)
        self.instrument_active_pairs=cwcn_wjy_config.ACTIVE_PAIRS
        self.code_active_pairs=[INV_INSTRUMENT_MAP[__] for __ in self.instrument_active_pairs]
        for __ in self.instrument_active_pairs:
            assert_folder(os.path.join(cwcn_wjy_config.WAJYU_FARM_CONFIG.FARM_FOLDER,'{}'.format(__)))
    def on_message(self, ws, message):
        def _clean(message):
            return message.replace('\x81\x06','').replace('null','\'\'')
        def _prepare(data):
            data=data[2]
            data=[INSTRUMENT_MAP[data[0]]]+[float(__) for __ in data[1:]]+[int(time.time())]
            return data
        def _dump_to_file(c_file,c_data):
            with open(c_file,"a+",encoding='utf-8') as _F:
                _F.write(str(c_data)+'\n')
        try:
            msg=_clean(message)
            if(msg[:5]=='[1002'):
                data=ast.literal_eval(msg)
                if(data[2][0] in self.code_active_pairs):
                    data=_prepare(data)
                    _dump_to_file(c_file=cwcn_wjy_config.WAJYU_FARM_CONFIG.INSTRUMENT_FILES[data[0]],c_data=data)
                    print(data)
        except Exception as e:
            print("[ERROR PROCESSING MESSAGE:] {} / / {}".format(message,e))
    def on_error(self, ws, error):
        print("[Websocket ERROR:] {}".format(error))
    def on_close(self, ws, close_status_code, close_msg):
        print("[Websocket CLOSED:] / close_status_code: {} / close_msg: {}".format(close_status_code, close_msg))
    def close(self):
        self.ws.close()
    def on_open(self, ws):
        def run(*args):
            for __ in self.farm_websockets:
                print("[CONNECTING:] {}".format(__))
                self.ws.send(__)
        _thread.start_new_thread(run, ())
# --- --- --- --- --- 
if __name__ == "__main__":
    while(True):
        try:
            wf=WAJYU_DATA_FARM()
            wf.ws.run_forever()
        except KeyboardInterrupt:
            print("[keyboard interrupt]")
            os._exit()
        except Exception as e:
            print("[MAIN LOOP ERROR:] {}".format(e))
            time.sleep(1)
