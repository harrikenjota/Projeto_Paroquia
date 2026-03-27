============================================================
       SANTUÁRIO SÃO JOSÉ - SISTEMA DE GESTÃO DE ESTOQUE
============================================================

1. VISÃO GERAL
--------------
Este sistema foi desenvolvido em Python/Flask para o controle 
administrativo das doações da Paróquia. Ele gerencia desde 
a entrada de donativos até a entrega para as famílias, 
oferecendo transparência através de dashboards estatísticos.

2. PRINCIPAIS FUNCIONALIDADES
-----------------------------
[X] CONTROLE DE ESTOQUE: Entradas e saídas com trava de segurança.
[X] GESTÃO DE PESSOAS: Separação entre DOADORES e ASSISTIDOS.
[X] DASHBOARD: Gráficos de fluxo e níveis críticos de itens.
[X] RELATÓRIOS: Exportação de movimentações e contatos em CSV.

3. ESTRUTURA DO PROJETO (ORGANIZAÇÃO POR SEÇÕES)
------------------------------------------------
O código foi estruturado em blocos numerados para facilitar 
a leitura e futuras manutenções (Clean Code):

- SEÇÃO 1: Configurações e Banco de Dados (app.py / models.py)
- SEÇÃO 2: Identidade Visual e CSS (base.html)
- SEÇÃO 3: Painel Operacional e Inventário (index.html)
- SEÇÃO 4: Inteligência de Dados e Gráficos (dashboard.html)
- SEÇÃO 5: Cadastro e Categorização Social (beneficiarios.html)

4. REQUISITOS E INSTALAÇÃO
--------------------------
Para rodar o projeto, você precisará do Python instalado.

Passo 1: Instalar dependências
> pip install flask flask_sqlalchemy

Passo 2: Executar o servidor
> python app.py

Passo 3: Acessar no navegador
> URL: http://127.0.0.1:5000

5. REGRAS DE NEGÓCIO IMPORTANTES
--------------------------------
- O sistema NÃO permite saída de itens sem estoque (erro de validação).
- A Dashboard conta APENAS famílias assistidas como "atendidas",
  separando os doadores para não distorcer a estatística social.
- O Banco de Dados (paroquia.db) é criado automaticamente no 
  primeiro acesso.

------------------------------------------------------------
   "Ide a José" - Gestão Administrativa Santuário São José
------------------------------------------------------------