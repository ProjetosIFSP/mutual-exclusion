import heapq
import threading
import time
import random

class LamportMutex:
    def __init__(self, site_id):
        self.site_id = site_id  # ID do site atual
        self.request_queue = []  # Fila de solicitações (ordenada pelo tempo lógico)
        self.request_time = 0  # Tempo lógico do site
        self.state = "Released"  # Estados possíveis: Released, Want, Held
        self.lock = threading.Lock()  # Lock para evitar concorrência na fila
    
    # Função para incrementar o tempo lógico de Lamport
    def increment_time(self):
        self.request_time += 1
        return self.request_time
    
    # Função para enviar REQUEST para todos os outros sites
    def send_request(self, sites):
        with self.lock:
            self.increment_time()
            request = (self.request_time, self.site_id)  # Solicitação com carimbo de tempo
            print(f"Site {self.site_id} enviando REQUEST com timestamp {self.request_time}.")
            for site in sites:
                if site.site_id != self.site_id:
                    delay = random.uniform(0.5, 2)  # Simula atraso na comunicação
                    threading.Thread(target=site.receive_request, args=(request, delay)).start()
            heapq.heappush(self.request_queue, request)
            self.state = "Want"
    
    # Função chamada quando o site recebe uma solicitação REQUEST
    def receive_request(self, request, delay=0):
        time.sleep(delay)  # Simula atraso na comunicação
        with self.lock:
            heapq.heappush(self.request_queue, request)
            print(f"Site {self.site_id} recebeu REQUEST de Site {request[1]} com timestamp {request[0]}.")
    
    # Função para entrar na seção crítica
    def enter_critical_section(self):
        with self.lock:
            while True:
                # Só entra se estiver no topo da fila e a solicitação for do próprio site
                if self.request_queue[0][1] == self.site_id and self.state == "Want":
                    self.state = "Held"
                    print(f"Site {self.site_id} entrou na seção crítica.")
                    break
                time.sleep(1)  # Aguarda até que possa entrar
    
    # Função para enviar RELEASE
    def send_release(self, sites):
        with self.lock:
            print(f"Site {self.site_id} saindo da seção crítica e enviando RELEASE.")
            self.state = "Released"
            heapq.heappop(self.request_queue)  # Remove sua própria solicitação
            for site in sites:
                if site.site_id != self.site_id:
                    delay = random.uniform(0.5, 2)  # Simula atraso na comunicação
                    threading.Thread(target=site.receive_release, args=(self.site_id, delay)).start()
    
    # Função chamada ao receber RELEASE
    def receive_release(self, site_id, delay=0):
        time.sleep(delay)  # Simula atraso na comunicação
        with self.lock:
            # Remove da fila as solicitações do site que enviou RELEASE
            self.request_queue = [req for req in self.request_queue if req[1] != site_id]
            heapq.heapify(self.request_queue)  # Reorganiza a fila
            print(f"Site {self.site_id} recebeu RELEASE de Site {site_id}.")

    # Função principal que executa o algoritmo
    def execute(self, sites):
        self.send_request(sites)  # Envia o pedido de acesso à seção crítica
        self.enter_critical_section()  # Aguarda para entrar na seção crítica
        time.sleep(random.uniform(1, 3))  # Simula tempo de execução na CS
        self.send_release(sites)  # Libera a CS enviando RELEASE

# Função para simular execução de um site
def simulate_site(site, sites):
    time.sleep(random.uniform(1, 3))  # Espera inicial aleatória
    site.execute(sites)

# Criando sites
site1 = LamportMutex(1)
site2 = LamportMutex(2)
site3 = LamportMutex(3)

sites = [site1, site2, site3]

# Simulando a execução dos sites em threads
threads = []
for site in sites:
    thread = threading.Thread(target=simulate_site, args=(site, sites))
    threads.append(thread)
    thread.start()

# Aguarda que todas as threads terminem
for thread in threads:
    thread.join()
