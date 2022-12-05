from __future__ import annotations

from signal import signal, SIGPIPE, SIG_DFL

from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
from typing import List, Type, Tuple, Mapping, Optional

from src.StateHolder.BaseStateHolder import BaseStateHolder
from src.WSModules.BaseWSModule import BaseWSModule
from src.WebSocketInterface import WSInterface, WSIPackets

# signal(SIGPIPE, SIG_DFL)

class Packets:

    class CODES:
        EXIT = 1
        APPEND = 2
        OVERWRITE = 3



class WSInstatiator:
    """Classe que instancia um WebServer Permanente e retorna pipes para Comunicação"""

    def __init__(self, modules_to_load: List[Tuple[Type[BaseWSModule], Type[BaseStateHolder], Tuple | None, Mapping | None]], *serve_args, **serve_kwargs):
        pps_p: List[Tuple[Connection, Type[BaseWSModule]]] = []
        pps_c: List[Tuple[Connection, Type[BaseWSModule]]] = []

        def _run(wsi_con: Connection, _modules_to_load_connected: List[Tuple[Type[BaseWSModule], Type[BaseStateHolder], Connection, Tuple | None,
                                              Mapping | None]],
                 *args, **kwargs):

            wsi = WSInterface()

            wsi.serve(wsi_con, _modules_to_load_connected, *args, **kwargs)

        pw, cw = Pipe()
        self._wsi_parent_pipe = pw
        modules_to_load_connected: List[Tuple[Type[BaseWSModule], Type[BaseStateHolder], Connection, Tuple | None,
                                              Mapping | None]] = self.connect_module_list(modules_to_load)
        self.process = Process(target=_run, args=(cw, modules_to_load_connected or [], *serve_args), kwargs=serve_kwargs)
        self.process.start()

        # self._module_child_pipe: List[Tuple[Connection, Type[BaseWSModule]]] = pps_c # não necessita, comássim o child
        # que usa esse end do pipe
        self._modules_parent_pipes: List[Tuple[Connection, Type[BaseWSModule]]] = []  # = pps_p
        # Podia passar a Tuple
        # ... A um dict em que a key seria um hash que aponta para a classe num hashmap gerado na criação do programa.
        # ... Mas, é escusado, apesar do ganho de desempenho...



    def add_modules(self, modules: List[Tuple[Type[BaseWSModule], Type[BaseStateHolder], Optional[Tuple],
                                        Optional[Mapping]]]):
        real_modules_needed = []

        for m in modules:
            if not self.is_module_loaded(m[0]):
                real_modules_needed.append(m)

        real_modules_needed = self.connect_module_list(real_modules_needed)
        print(self._wsi_parent_pipe.closed)

        self._wsi_parent_pipe.send({"code": WSIPackets.CODES.ADD_MODULES, "data": real_modules_needed})

    def send_message_to_module(self, module: Type[BaseWSModule], code: int, data=None):
        for mpp in self._modules_parent_pipes:
            if mpp[1] == module:
                mpp[0].send({"code": code, "data": data})
                return  # break não, para não executar o debaixo
        raise RuntimeError(f'Can\'t send message, module <{module}> not found!')

    def remove_modules(self, modules: List[Type[BaseWSModule]]):

        self._wsi_parent_pipe.send({"code": WSIPackets.CODES.REMOVE_MODULES, "data": modules})
        self.remove_modules_pipe(modules)

    def kill(self):
        self.process.kill()

    def connect_module_list(self, modules_to_load: List[Tuple[Type[BaseWSModule], Type[BaseStateHolder], Tuple | None,
                                                              Mapping | None]]) -> List[Tuple[Type[BaseWSModule], Type[BaseStateHolder], Connection, Tuple | None,
                     Mapping | None]]:

        modules_to_load_connected: List[Tuple[Type[BaseWSModule], Type[BaseStateHolder], Connection, Tuple | None,
                                              Mapping | None]] = []

        for i in range(0, len(modules_to_load)):
            p, c = Pipe()
            self._modules_parent_pipes.append((p, modules_to_load[i][0]))
            # _modules_parent_child.append((c, modules_to_load[i][0]))
            modules_to_load_connected.append((modules_to_load[i][0], modules_to_load[i][1], c, modules_to_load[i][2],
                                              modules_to_load[i][3]))
        return modules_to_load_connected

    def remove_module_pipe(self, module: Type[BaseWSModule]):
        for i in range(0, len(self._modules_parent_pipes)):
            if self._modules_parent_pipes[i][1] == module:
                self._modules_parent_pipes.pop(i)
                return

    def remove_modules_pipe(self, modules: List[Type[BaseWSModule]]):
        for m in modules:
            self.remove_module_pipe(m)

    def clean_module(self, module: Type[BaseWSModule]):

        if self.is_module_loaded(module):
            self.send_message_to_module(module, WSIPackets.CODES.CLEAN_MODULE, data=module)

    def clean_modules(self, modules: List[Type[BaseWSModule]]):
        for m in modules:
            self.clean_module(m)

    def is_module_loaded(self, module: Type[BaseWSModule]):
        for pm in self._modules_parent_pipes:
            if pm[1] == module:
                return True
        return False

    def all_modules_loaded(self) -> List[Type[BaseWSModule]]:
        ms = []
        for m in self._modules_parent_pipes:
            ms.append(m[1])
        return ms


