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
