# MEMORANDO EXECUTIVO — DUE DILIGENCE SERIES C (ORBITSHOP)

**Para:** Comitê Series C | **De:** Due Diligence Analítica (Peers) | **Data:** Nov/2026
**Assunto:** Auditoria de Receita, Operação e Criação de Valor (2023–2024)


### 1. Governança de Dados e Fonte da Verdade Financeira (Q1, Q6)

As 6 tabelas relacionais (15.000 pedidos; 36.740 itens; 3.000 clientes; 200 produtos; 4.000 tickets; 8.000 avaliações) têm integridade referencial perfeita (0 duplicatas/órfãos). Contudo, `Itens_Pedido` sofre distorção de ETL: sua soma líquida atinge **R$ 165,88M** contra **R$ 38,42M** em `Pedidos.valor_total` (**0/14.921 pedidos conciliam**; divergência **-R$ 127,46M**), com 34.148 preços divergentes do catálogo, 2.574 vendas abaixo do custo e 21.243 descontos sem cupom. Adotamos `Pedidos.valor_total` como **única fonte oficial de receita**, imputando os 79 nulos (0,53%) pela mediana segmentada (**B2B: R$ 7.803,97**; **B2C: R$ 1.255,37**; total imputado **R$ 38,63M**). Isso comprova a tese da CEO: o ticket médio **B2B (R$ 7.778,34)** é **6,15x** superior ao **B2C (R$ 1.264,72)**.


### 2. Paradoxo C-Level e Diagnóstico Operacional (Q2–Q5, Q7)

- **Funil (Q2):** O crescimento bruto convive com **16,91% de cancelamento** (2.536 pedidos; 16,78% em 2023 e 17,08% em 2024) e **7,55% de devolução** (1.133). Ao todo, **24,46% dos pedidos (3.669 = R$ 9,47M)** não convertem em caixa, além de **788 pedidos de 2023 presos em `em_transito`**.
- **Categorias (Q3):** `Eletrônicos` (18.658 un.), `Casa & Decoração` (17.899 un.) e `Moda` (15.680 un.) lideram em volume físico, mas `Moda` é **5ª em receita** pelo menor preço médio praticado (**R$ 1.347,98**).
- **Canais (Q4):** `paid_search` registra **30,74% de cancelamento** (1.219/3.965; qui-quadrado 734,42, p<1e-158), concentrando **48,07%** dos cancelamentos totais contra **11,67%–12,38%** nos demais canais, sem ganho de ticket (**R$ 2.553,51**).
- **Sazonalidade (Q5):** Fora o pico isolado de **`2023-11` (2.317 pedidos, 4,2x a média de 551/mês)** — simétrico entre app (783), site (770) e marketplace (764) —, a demanda estagnou e caiu para **585 pedidos em `2024-11`**.
- **Fornecedores e Suporte (Q7):** `DeltaFornece ME` é outlier exclusivo em produto (nota **2,30**; **59,90%** notas 1–2 vs. **3,62–3,84** dos pares), mas a taxa de suporte é uniforme (**22,94 tickets/100 itens** vs. **22,16–24,85**), provando que o pico em nov–dez/2023 (**375** e **391**) foi gargalo pós-Black Friday.


### 3. Recomendação Prioritária (Q8, Q9)

**Reestruturar imediatamente `paid_search`**: qualificar tráfego e checkout para convergir seu cancelamento de **30,74%** ao benchmark interno (**11,9%**), recuperando **~747 pedidos** e **~R$ 1,91M em receita bruta** sem elevar CAC. Em paralelo: sanear `Itens_Pedido`, auditar `DeltaFornece ME` e baixar os **788 pedidos `em_transito` de 2023**.
