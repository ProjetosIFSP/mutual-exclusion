# Capítulo 8: Exclusão Mútua

Eventos mutuamente exclusivos, no contexto da programação, significam que dois ou mais threads ou processos em execução concorrente nunca competem simultaneamente para adquirir um objeto compartilhado. Em outras palavras, a exclusão mútua serializa os acessos de processos concorrentes a recursos compartilhados, como seções críticas (CS) de código. A execução atômica de uma seção crítica por threads concorrentes garante que nenhum objeto compartilhado esteja em um estado inconsistente devido à execução simultânea.

Existem duas principais classes de algoritmos de exclusão mútua:

1. **Baseados em afirmações:** O privilégio de acessar a seção crítica é decidido com base em variáveis locais. Este método pode requerer múltiplas trocas de mensagens entre os processos concorrentes.
2. **Baseados em tokens:** Um token exclusivo circula entre os processos. Possuir o token dá ao processo o privilégio de executar uma seção crítica.

Os algoritmos de exclusão mútua enfrentam os seguintes desafios:

- Garantir **ausência de deadlock e starvation**.
- Assegurar **justiça** no acesso aos recursos compartilhados.
- Prover **tolerância a falhas** para recuperação e continuidade do sistema após falhas.

A performance dos algoritmos de exclusão mútua pode ser avaliada com base em:

1. **Número de mensagens:** Quantidade de mensagens trocadas por invocação da seção crítica.
2. **Atraso de sincronização:** Tempo entre a saída de um site da CS e a entrada do próximo.
3. **Tempo de resposta:** Tempo entre o envio de uma solicitação de CS e sua execução.
4. **Taxa de transferência:** Velocidade com que as solicitações são atendidas.

Este capítulo aborda ambas as classes de algoritmos, apresentando suas implementações e análises de desempenho.

---

## 8.1 Modelo de Sistema

Em sistemas distribuídos, os componentes interagem por meio de processos executados em nós autônomos. Para simplificar, o modelo discutido aqui assume:

- **N sites** distribuídos geograficamente, \({S_1, S_2, ..., S_n}\), que se comunicam por troca de mensagens.
- Não há **memória compartilhada** no sistema.
- A rede subjacente permite **conectividade total** entre os sites, com entrega de mensagens em tempo finito.

Os problemas comuns enfrentados no desenvolvimento de protocolos livres de erros incluem:

1. **Ausência de deadlock e starvation.**
2. **Justiça:** Garantir que as solicitações sejam atendidas na ordem correta.
3. **Tolerância a falhas:** Permitir recuperação de falhas sem longas esperas.

### **Parâmetros de Desempenho**

1. **Número de Mensagens:** Necessário para cada invocação da CS.
2. **Atraso de Sincronização:** Intervalo entre a saída de um site da CS e a entrada do próximo.
3. **Tempo de Resposta:** Tempo entre o envio de um pedido e sua execução.
4. **Taxa de Transferência:** Quantidade de solicitações atendidas por unidade de tempo.

### **Hipóteses Fundamentais**

- As mensagens são **entregues corretamente** em tempo finito.
- Não há **desordem** na entrega das mensagens (FIFO).
- Os atrasos de transmissão são **finitos**, mas podem variar.
- A topologia da rede é **conhecida** por todos os sites.

Este modelo forma a base para o design e análise dos algoritmos de exclusão mútua apresentados neste capítulo.

---

## 8.2 Solução Baseada em Coordenador

Uma solução baseada em coordenador central envolve um coordenador que arbitra os pedidos de acesso à seção crítica (CS) provenientes de sites concorrentes e concede as permissões de acesso. O processo funciona da seguinte maneira:

1. O site que deseja acesso à CS envia uma mensagem **REQUEST** ao coordenador.
2. O coordenador mantém uma fila ordenada de solicitações e concede o acesso por ordem de chegada, enviando uma mensagem **GRANT**.
3. Após a execução, o site envia uma mensagem **RELEASE** ao coordenador para indicar que saiu da CS.

Cada solicitação exige **três mensagens**:

- **REQUEST:** Para solicitar acesso.
- **GRANT:** Para conceder acesso.
- **RELEASE:** Para liberar a CS.

O tempo de atraso **não considera** o envio de **RELEASE**, já que é uma mensagem enviada após a saída da CS.

#### **Desvantagens**

A solução baseada em coordenador apresenta várias limitações:

1. **Ponto único de falha:** Se o coordenador falhar, todo o sistema para.
2. **Gargalo de desempenho:** O coordenador pode se tornar sobrecarregado com muitas solicitações simultâneas, dificultando a escalabilidade.
3. **Baixa taxa de transferência:** O desempenho máximo não ultrapassa \(1 / (2T + E)\), sendo \(T\) o atraso médio de mensagens e \(E\) o tempo de execução da seção crítica.

Embora seja possível melhorar o throughput reduzindo o atraso de sincronização, a solução não é ideal para sistemas distribuídos com alta carga ou grandes números de nós.

---

## 8.3 Soluções Baseadas em Afirmações

A maioria das soluções baseadas em permissões depende de alguma forma de ordenação dos pedidos de exclusão mútua. Algoritmos como o de **Lamport** utilizam marcações de tempo (timestamps) e identificadores de sites para garantir a exclusão mútua. A seguir, são apresentados três algoritmos principais:

---

### 8.3.1 Algoritmo de Lamport

Este algoritmo utiliza a troca de mensagens e relógios lógicos para ordenar os pedidos de exclusão mútua. Os principais pressupostos do algoritmo são:

1. Os relógios dos sites diferem dentro de um valor limitado.
2. Os canais de comunicação garantem entrega em ordem (FIFO).

#### **Funcionamento**

- Cada site mantém uma **fila local de pedidos (RQ)**.
- Quando um site deseja entrar na seção crítica (CS):
  1. Ele adiciona um pedido à sua fila local e envia uma mensagem **REQUEST** a todos os outros sites.
  2. Os pedidos são marcados com timestamps gerados por relógios lógicos de Lamport.
  3. Um site pode entrar na CS somente se as duas condições a seguir forem atendidas:
     - **Regra L1:** O site recebeu mensagens **REQUEST** de todos os outros sites com timestamps maiores do que o seu.
     - **Regra L2:** Seu pedido está no topo da fila local (RQ).
- Após sair da CS, o site envia uma mensagem **RELEASE** para todos os outros, permitindo que o próximo site na fila entre na CS.

#### **Complexidade:**

- Número de mensagens por invocação da CS: \(3(N-1)\)
  - \(N-1\) mensagens **REQUEST**, \(N-1\) mensagens **REPLY** e \(N-1\) mensagens **RELEASE**.
- Sincronização: \(T\), onde \(T\) é o atraso médio de mensagens.

#### **Propriedades**

- O algoritmo garante exclusão mútua estrita (Theorema 8.1).
- Ordem dos eventos é mantida pelos relógios lógicos.

---

### 8.3.2 Melhorias no Algoritmo de Lamport (Ricart e Agrawala)

Ricart e Agrawala aprimoraram o algoritmo de Lamport reduzindo o número de mensagens:

1. Mensagens **RELEASE** são eliminadas.
2. A troca de mensagens ocorre somente entre os sites que competem pela CS.

#### **Funcionamento**

- Quando um site deseja entrar na CS, ele envia mensagens **REQUEST** para todos os outros.
- Cada site decide se responde com uma mensagem **REPLY** com base no timestamp do pedido e no estado atual.
- Após completar a execução da CS, o site envia mensagens **REPLY** para os próximos da fila.

#### **Complexidade:**

- Número de mensagens por invocação da CS: \(2(N-1)\).
- Sincronização: \(T\).

---

### 8.3.3 Algoritmos Baseados em Quóruns (Maekawa)

O algoritmo de **Maekawa** é baseado na ideia de "quóruns", ou seja, subconjuntos de sites. Um site precisa obter permissões apenas de um subconjunto (quórum) para acessar a CS.

#### **Características**

- Cada site tem um conjunto de requisição \(R_i\), que é um subconjunto de sites.
- As seguintes propriedades garantem exclusão mútua:
  1. \(R_i \cap R_j \neq \emptyset\) para todos \(i\) e \(j\).
  2. Cada site pertence ao seu próprio conjunto \(R_i\).
  3. Todos os conjuntos têm o mesmo tamanho.
  4. Um site pode participar de, no máximo, \(k\) conjuntos \(R_i\).

#### **Funcionamento**

1. Um site envia mensagens **REQUEST** para todos os sites no seu quórum.
2. Cada site no quórum responde com uma mensagem **REPLY** se estiver disponível, ou aguarda a liberação do recurso.
3. Após executar a CS, o site envia mensagens **RELEASE** para liberar os membros do quórum.

#### **Complexidade**

- Número de mensagens: \(O(\sqrt{N})\) por invocação da CS.
- Sincronização: \(2T\).

#### **Desvantagens**

- Propenso a deadlocks.
- Precisa de mecanismos adicionais para resolução de deadlocks (mensagens FAILED, INQUIRE e YIELD).

---

## 8.4 Soluções Baseadas em Tokens

Algoritmos baseados em tokens usam números de sequência para distinguir novas requisições de antigas, garantindo que apenas o site que possui o token possa acessar a seção crítica (CS). A seguir, discutiremos os principais algoritmos baseados em tokens.

### 8.4.1 Algoritmo de Suzuki e Kasami

Neste algoritmo, um site que deseja acessar a CS envia uma mensagem **REQUEST** para todos os outros sites. Apenas o site que possui o token pode entrar na CS. Após sair da CS, o site envia o token para o próximo site na fila de requisições.

#### **Estrutura do Token**

O token contém:

1. Uma fila \(Q\) com os IDs dos sites que solicitaram a CS.
2. Um vetor \(L[1..N]\), onde cada \(L[i]\) armazena o número de sequência da última vez que o site \(i\) foi atendido.

#### **Funcionamento**

1. Um site \(S\) deseja acessar a CS:
   - Incrementa seu número de sequência local \(R[S]\).
   - Envia uma mensagem **REQUEST** contendo \((R[S], S)\) para todos os outros sites.
2. Quando \(S\) recebe o token:
   - Atualiza \(L[S]\) com \(R[S]\).
   - Remove da fila \(Q\) os pedidos atendidos (\(R[i] = L[i] + 1\)).
   - Se houver outros pedidos pendentes na fila \(Q\), o token é enviado ao próximo site.
3. Após concluir a execução na CS, \(S\) atualiza \(L[S]\) e verifica se há pedidos pendentes para enviar o token.

#### **Complexidade**

- Mensagens por requisição: \(N-1\).
- Sincronização: \(T\), onde \(T\) é o atraso médio de mensagens.
- Sob baixa carga, o atraso pode ser \(0\) se o site já possui o token.

#### **Vantagens**

- Baixa sobrecarga de mensagens sob baixa carga.
- Garantia de exclusão mútua.

---

### 8.4.2 Algoritmo Heurístico de Singhal

Este algoritmo é uma extensão do de Suzuki e Kasami, projetado para minimizar a troca de mensagens. Em vez de enviar mensagens **REQUEST** para todos os sites, cada site mantém informações sobre os estados dos outros sites em vetores locais.

#### **Estruturas Locais e do Token**

1. Cada site mantém:
   - \(SV[1..N]\): Estados dos sites (\(\mathcal{R}\) = requisitando, \(\mathcal{E}\) = executando, \(\mathcal{H}\) = possuindo token, \(\mathcal{N}\) = nenhum estado).
   - \(SN[1..N]\): Maior número de sequência conhecido de cada site.
2. O token contém:
   - \(TSV[1..N]\): Estados dos sites conhecidos pelo token.
   - \(TSN[1..N]\): Números de sequência conhecidos pelo token.

#### **Funcionamento**

1. Um site \(S\) deseja acessar a CS:
   - Atualiza \(SV[S] = \mathcal{R}\) e incrementa \(SN[S]\).
   - Envia mensagens **REQUEST** para um subconjunto de sites que estão em estado \(\mathcal{R}\).
2. Quando \(S\) recebe o token:
   - Atualiza o token e entra na CS.
   - Após sair, \(S\) verifica se há pedidos pendentes e envia o token ao próximo site, se necessário.

#### **Complexidade**

- Mensagens por requisição: \(N/2\) em média sob baixa carga.
- Sincronização: \(2T\).

#### **Vantagens**

- Adapta-se a diferentes níveis de carga.
- Minimiza mensagens em condições de baixa carga.

---

### 8.4.3 Algoritmo Baseado em Árvore de Raymond

O algoritmo de Raymond organiza os sites em uma topologia de árvore, onde cada nó possui um ponteiro \(HOLDER\) indicando qual nó está mais próximo do token. O site que possui o token é a raiz da árvore.

#### **Funcionamento**

1. Quando um site \(S\) deseja acessar a CS:
   - Enfileira seu pedido em sua fila local \(RQ\).
   - Envia uma mensagem **REQUEST** ao site indicado por \(HOLDER\).
2. O site que possui o token verifica sua fila local e envia o token para o próximo site na fila.
3. Após acessar a CS, o site verifica se há pedidos pendentes. Se houver, o token é enviado ao próximo site da fila; caso contrário, ele mantém o token.

#### **Complexidade**

- Mensagens por requisição: Aproximadamente \(4 \log N\).
- Sincronização: \((T \log N)/2\).

#### **Vantagens**

- Baixa sobrecarga de mensagens.
- Escalável para grandes redes.

---

## 8.5 Conclusão

Neste capítulo, foram discutidas duas abordagens diferentes para o design de algoritmos de exclusão mútua distribuída:

1. **Baseada em afirmações (assertion-based)**
2. **Baseada em tokens (token-based)**

Abaixo está um resumo das características principais dos algoritmos de exclusão mútua distribuída.

#### **Algoritmos Baseados em Afirmações**

Esses algoritmos requerem a troca de mensagens entre os sites participantes para obter permissões para entrar na seção crítica (CS). O site que consegue as permissões dos sites concorrentes entra na CS. O esforço está em reduzir os custos de comunicação.

- Cada site mantém o máximo de informações locais possível, permitindo que obtenha permissão com algumas rodadas de mensagens.
- O custo geral é amortizado pelo fato de que alguns sites atrasam suas entradas na CS, mas têm a vantagem de conhecer outros sites que já tiveram sua vez na CS.

Entre os algoritmos baseados em afirmações, o algoritmo de **Maekawa** é notável, pois reduz o número de mensagens ao buscar permissões de apenas um subconjunto de sites (quórum). A abordagem baseada em quóruns de Maekawa inspirou uma série de publicações que buscam:

- Reduzir a complexidade de mensagens.
- Aumentar a resiliência a falhas.

#### **Algoritmos Baseados em Tokens**

A abordagem baseada em tokens é mais limpa logicamente. Um token exclusivo circula entre os sites, garantindo que nenhum site possa manter o token enquanto outros estão esperando.

- O token funciona como um bilhete único que permite a entrada restrita em uma "catraca".
- O site que possui o token pode entrar na CS.

Nessa abordagem, o esforço está em armazenar informações suficientes no token e minimizar as informações de suporte armazenadas localmente nos sites. Contudo, surgem desafios como:

- Tokens perdidos ou duplicados.
- Detectar a perda de tokens pode ser difícil.
- Regenerar tokens ausentes pode ser problemático.

Pesquisas relacionadas têm focado em como lidar com a perda de tokens e sua regeneração.

#### **Resumo de Algoritmos**

A tabela abaixo resume as características dos algoritmos discutidos neste capítulo:

| **Algoritmo**       | **Complexidade de Mensagens (Alta Carga)** | **Complexidade de Mensagens (Baixa Carga)** | **Atraso de Sincronização** |
| ------------------- | ------------------------------------------ | ------------------------------------------- | --------------------------- |
| **Lamport**         | \(3(N − 1)\)                               | \(2(N − 1)\)                                | \(T\)                       |
| **Ricart-Agrawala** | \(2(N − 1)\)                               | \(N − 1\)                                   | \(T\)                       |
| **Maekawa**         | \(3\sqrt{N}\)                              | \(5\sqrt{N}\)                               | \(2T\)                      |
| **Suzuki-Kasami**   | \(N − 1\)                                  | \(0\)                                       | \(0\) ou \(T\)              |
| **Singhal**         | \(N/2\)                                    | \(N/2\)                                     | \(2T\)                      |
| **Raymond**         | \(4\log N\)                                | \(4\log N\)                                 | \(T\log N/2\)               |

#### **Considerações Finais**

- Algoritmos baseados em afirmações são úteis para sistemas menores ou cenários que requerem alta tolerância a falhas.
- **Lamport:** Simples e robusto, ideal para redes menores.
- **Suzuki e Kasami:** Escalável, eficiente em redes maiores.
- A prática é essencial: implemente os algoritmos e observe seu comportamento!
