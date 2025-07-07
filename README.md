# Trabalho_CGI

## Visão Geral do Projeto

Este projeto implementa uma solução de visão computacional para monitorar e gerenciar vagas em um estacionamento. Desenvolvido em **Python** utilizando a biblioteca **OpenCV**, o sistema é capaz de:

* **Detectar e demarcar vagas** de estacionamento (suportando formatos poligonais).
* **Identificar carros** dentro dessas vagas através de técnicas de processamento de imagem e detecção de bordas.
* **Classificar a cor** predominante dos veículos estacionados.
* Fornecer uma **contagem em tempo real** de vagas disponíveis.

O sistema é robusto a variações de iluminação e utiliza uma pipeline de pré-processamento de imagem, detecção de bordas (Canny), operações morfológicas para fechamento de contornos e K-Means clustering para classificação de cores.

---

## Manual para Desenvolvedores

Este manual é destinado a desenvolvedores que desejam entender, modificar ou otimizar o código-fonte do Sistema de Monitoramento de Estacionamento Inteligente.

### 1. Estrutura do Projeto

O projeto é organizado nos seguintes arquivos e diretórios:
SeuProjeto/
├── estacionamento.mp4        # Vídeo de entrada para análise.
├── configs.py                # Contém todos os parâmetros de configuração e limiares ajustáveis.
├── get_vaga_coords.py        # Script auxiliar para demarcar vagas e ROI no vídeo.
├── main.py                   # Lógica principal do programa, loop de processamento de vídeo.
└── utils.py                  # Funções auxiliares, como o algoritmo de detecção de cores.



### 2. Configuração do Ambiente de Desenvolvimento

Para configurar o ambiente de desenvolvimento, siga os passos de instalação de dependências:

1.  **Crie um Ambiente Virtual (venv):**
    Abra seu terminal ou prompt de comando na pasta raiz do projeto (`SeuProjeto/`) e execute:
    ```bash
    python -m venv venv
    ```
2.  **Ative o Ambiente Virtual:**
    * **Windows (Prompt de Comando):**
        ```bash
        venv\Scripts\activate
        ```
    * **Windows (PowerShell):**
        ```powershell
        .\venv\Scripts\Activate.ps1
        ```
    * **macOS / Linux:**
        ```bash
        source venv/bin/activate
        ```
3.  **Instale as Dependências:** Com a `venv` ativada, instale as bibliotecas necessárias:
    ```bash
    pip install opencv-python numpy
    ```

### 3. Fluxo de Processamento Principal (`main.py`)

O arquivo `main.py` é o ponto de entrada e orquestra o pipeline de visão computacional:

* **`initialize_video_capture(video_path)`**: Inicializa a captura de vídeo e realiza uma verificação inicial de integridade.
* **Loop `while True`**: Processa o vídeo frame a frame.
    * **Redimensionamento e Cópia**: Redimensiona o frame para um tamanho padrão e cria uma cópia (`display_frame`) para anotações visuais.
    * **Máscara de ROI Geral**: Cria e aplica `roi_mask_general` (definida em `configs.py`) para focar o processamento apenas na área relevante do estacionamento.
    * **Pré-processamento de Imagem**: Converte para escala de cinza (`gray_image`) e aplica melhorias (atualmente `GAUSSIAN_BLUR`) que suavizam ruídos.
    * **Detecção de Contornos de Carros (`find_car_contours`)**:
        * Aplica `cv2.Canny` (detecção de bordas).
        * Aplica `cv2.MORPH_CLOSE` (fechamento morfológico) para solidificar os contornos.
        * Aplica a `roi_mask_general` final nas bordas fechadas.
        * Encontra os contornos (`cv2.findContours`).
    * **Processamento por Vaga**: Itera sobre cada vaga definida em `PARKING_SPOTS`.
        * Para cada vaga, cria uma máscara específica.
        * Verifica a **interseção** dos contornos detectados (que passaram pelos filtros) com a máscara da vaga.
        * Se houver interseção significativa, a vaga é marcada como ocupada.
        * Chama `get_car_color()` para identificar a cor do carro.
    * **Filtragem Temporal**: Utiliza `consecutive_occupied_frames_count` para estabilizar o status da vaga antes de atualizar a exibição.
    * **Desenho e Exibição**: `draw_vaga_status()` desenha os polígonos das vagas, status e cores. `cv2.imshow()` exibe as janelas de visualização (`Estacionamento Inteligente`) e de depuração (`Canny Edges (Debug)`, `Closed Edges (Debug)`).

### 4. Parâmetros de Configuração (`configs.py`)

O arquivo `configs.py` centraliza **todos os parâmetros ajustáveis** do sistema. A modificação desses parâmetros é a principal forma de otimizar o desempenho do algoritmo para diferentes cenários ou condições de vídeo.

* **`VIDEO_PATH`**: Caminho para o arquivo de vídeo de entrada.
* **`PARKING_SPOTS`**: Lista de dicionários, cada um definindo uma vaga por um polígono (`coords`), e um `id`. **CRÍTICO para a precisão da detecção de ocupação.**
* **`PARKING_AREA_MASK_COORDS`**: Polígono que define a área geral do estacionamento a ser analisada, filtrando o fundo.
* **`KNOWN_COLORS_BGR`**: Dicionário com a paleta de cores conhecidas em formato BGR. As cores dominantes encontradas pelo K-Means serão comparadas a esta paleta. **A precisão desta paleta é FUNDAMENTAL para a classificação de cores.**
* **`GAUSSIAN_BLUR_KERNEL_SIZE`, `GAUSSIAN_BLUR_SIGMA_X`**: Parâmetros para o filtro Gaussiano. Afetam a suavização da imagem antes do Canny.
* **`CANNY_THRESHOLD1`, `CANNY_THRESHOLD2`**: Limiares de histerese para o algoritmo Canny. Controlam a sensibilidade da detecção de bordas.
* **`CLOSE_KERNEL_SIZE`, `CLOSE_ITERATIONS`**: Parâmetros para a operação morfológica `cv2.MORPH_CLOSE`. Cruciais para fechar e solidificar os contornos das bordas.
* **`MIN_CAR_AREA`, `MAX_CAR_AREA`**: Limites de área para filtrar contornos que não representam carros (ex: ruído, pessoas).
* **`MIN_ASPECT_RATIO`, `MAX_ASPECT_RATIO`**: Limites da proporção largura/altura para filtrar contornos por forma.
* **`MIN_INTERSECTION_AREA_PERCENT_POLY`**: Porcentagem de sobreposição que um contorno de carro deve ter com a vaga para ser considerada ocupada.
* **`CAR_ROI_PADDING`**: Padding adicionado à ROI do carro para análise de cor.
* **`CONSECUTIVE_FRAMES_THRESHOLD`**: Número de frames consecutivos para estabilizar a detecção de ocupação.
* **`S_MIN_FILTER_COLOR_ANALYSIS`, `V_MIN_FILTER_COLOR_ANALYSIS`**: Limiares para a filtragem de pixels de vidro/sombra antes da análise de cor (em `utils.py`).

### 6. Funções Auxiliares (`utils.py`)

O arquivo `utils.py` contém a função `get_car_color()`, que é responsável pela complexa lógica de detecção de cores:

* **`get_car_color(roi)`**:
    * Recebe uma Região de Interesse (ROI) BGR do carro.
    * Aplica um filtro (usando `S_MIN_FILTER_COLOR_ANALYSIS` e `V_MIN_FILTER_COLOR_ANALYSIS`) para **ignorar pixels de vidro escuro e sombras**, focando na pintura do carro.
    * Executa o algoritmo **K-Means Clustering (com K=1)** nos pixels restantes para encontrar a cor BGR mais dominante na ROI.
    * Compara essa cor dominante com as cores em `KNOWN_COLORS_BGR` (definidas em `configs.py`) usando distância euclidiana.
    * Retorna o nome da cor mais próxima ou "Desconhecida" se a distância for muito grande.

### 7. Scripts Auxiliares

* **`get_vaga_coords.py`**: Um script independente para auxiliar na demarcação visual das vagas e da área de interesse geral no vídeo. Ele gera as coordenadas poligonais que devem ser copiadas para `configs.py`.

## Como Calibrar e Ajustar o Sistema

Ajustar o sistema para o seu vídeo específico é um processo iterativo e crucial.

1.  **Primeira Execução e Demarcação:**
    * Siga os passos em "[3. Definição das Vagas e da Área de Interesse (ROI)](#3-definição-das-vagas-e-da-área-de-interesse-roi)" para obter as coordenadas precisas das vagas e da ROI geral. **Copie-as e cole-as em `configs.py`**.

2.  **Depuração Visual e Ajuste de Parâmetros:**
    * Execute `python main.py`.
    * **Observe as Janelas de Debug:**
        * `Canny Edges (Debug)`: Deve mostrar as bordas dos carros e linhas principais, com o mínimo de ruído de textura do chão. Ajuste `GAUSSIAN_BLUR_KERNEL_SIZE`, `CANNY_THRESHOLD1`, `CANNY_THRESHOLD2` em `configs.py`.
        * `Closed Edges (Debug)`: **CRÍTICA.** Deve mostrar os carros como formas brancas sólidas e bem definidas, com o fundo preto. Ajuste `CLOSE_KERNEL_SIZE`, `CLOSE_ITERATIONS` em `configs.py`. Se os carros não forem sólidos aqui, as etapas seguintes falharão.
    * **Ative os Prints de Debug:**
        * Em `main.py`, descomente `print(f"Contorno - Área: {area:.2f}, Proporção: {aspect_ratio:.2f}")` para ver os tamanhos e formas dos contornos detectados.
        * Em `utils.py`, o `print(f"DEBUG - Cor Dominante BGR da ROI (Filtrada): {dominant_bgr}")` já está ativo. Use-o para ver as cores BGR que o K-Means está encontrando.
    * **Ajuste os Filtros de Contorno (`MIN_CAR_AREA`, `MAX_CAR_AREA`, `MIN_ASPECT_RATIO`, `MAX_ASPECT_RATIO`):** Com base nos prints do console, refine esses parâmetros em `configs.py` para incluir apenas os contornos dos carros e excluir ruídos ou pessoas.
    * **Ajuste a Detecção de Cores (`KNOWN_COLORS_BGR` e `min_distance` em `utils.py`):**
        * Use os prints de `DEBUG - Cor Dominante BGR da ROI (Filtrada)` para carros que estão dando a cor errada (ex: "Cinza" para um carro laranja).
        * **Atualize a paleta `KNOWN_COLORS_BGR` em `configs.py` com esses valores BGR reais.** Por exemplo, se seu carro laranja está dando `[68 60 66]`, adicione `(68, 60, 66)` como a cor "Laranja" na sua paleta.
        * Ajuste o limiar `min_distance` em `utils.py` (linha `if min_distance > 50:`). Se carros com cores que você adicionou ainda derem "Desconhecida", **aumente** este `50`. Se as cores estiverem se confundindo, **diminua** este `50`.
    * **Ajuste `S_MIN_FILTER_COLOR_ANALYSIS`, `V_MIN_FILTER_COLOR_ANALYSIS`:** Se os vidros ainda estiverem influenciando a cor ou se o programa não encontrar pixels para a cor, ajuste esses limiares no `configs.py`.
