# MEMO EXECUTIVO — DUE DILIGENCE ORBITSHOP (SERIES C)
**De:** Pedro Henrique Vogt Verolla

### Q1 — Perguntas Preliminares
1. Vocês medem cancelamento por volume absoluto, taxa percentual ou receita (GMV) perdida?
2. O cálculo usa data do pedido ou cancelamento, incluindo pedidos abertos ou só concluídos?
3. Os relatórios consolidam todos os canais e segmentos (B2C/B2B) ou aplicam filtros distintos?

### Diagnóstico Executivo (Q2–Q7)
- **Paradoxo e Funil (Q2):** Cancelamento estável em **16,91%** (2.537/15.000: **16,78%** em 2023; **17,08%** em 2024). Rogério viu queda semestral em 2024 (17,66% a 16,53%; 15,00% em dez/24); Camila reagiu à alta na mídia paga. Cancelados e devolvidos (7,55%) drenam **24,47% dos pedidos (3.670; R$9,47M)**, e **788 de 2023** seguem `em_transito`.
- **Reconciliação (Q6):** Zero pedidos conciliam entre `Pedidos.valor_total` (**R$38,42M**) e `Itens_Pedido` (**R$165,88M**; desvio **-R$127,46M**). Levamos **`Pedidos.valor_total`** (imputando 79 nulos pela mediana segmentada): valida ticket B2B **6,15x** maior que B2C (**R$7.778** vs. **R$1.265**), enquanto `Itens_Pedido` tem falha de ETL (tickets ~R$11mil iguais, 21.243 descontos sem cupom e 2.574 abaixo do custo).
- **Mix, Canais e Operação (Q3–Q5, Q7):** *Eletrônicos* (18.658), *Casa&Decoração* (17.899) e *Moda* (15.680) lideram em volume, mas *Moda* é 5ª em receita pelo menor preço médio (R$1.348). **`paid_search` cancela 30,74%** (1.219/3.965; $p < 10^-158$) vs. **~11,9%** nos demais, com mesmo ticket (R$2.554), indicando tráfego desqualificado. O pico de **2.317 pedidos em nov/2023** (4,2x a média de 551/mês; 585 em nov/24) gerou o salto de tickets em nov–dez/23 (375 e 391 nos 9 fornecedores); **`DeltaFornece ME`** destoa em qualidade (nota **2,30**; **59,9%** notas 1–2), com taxa normal de tickets (22,9/100 itens).

### Recomendação e Lacunas (Q8–Q9)
- **Ação Única (Q8):** Reestruturar `paid_search` (pausar campanhas de baixa intenção e migrar verba a orgânico/indicação), reduzindo cancelamento a 11,9% e recuperando **747 pedidos (~R$1,91M)**. *Trade-off:* postergamos trocar `DeltaFornece ME` (evitando ruptura) e sanear ETL/788 `em_transito`.
- **Lacunas (Q9):** Solicitar: (1) CAC/gasto por canal, (2) motivo do cancelamento e (3) logs de status/frete.

### Uso de IA (Governança e Conflitos)
A IA foi controlada em 2 fases: auditoria exploratória em notebook fixando a verdade empírica e uso do **GSD Core** (*Spec-Driven Development*/engenharia de contexto) modularizando código/testes sem *context rot*. Foram resolvidos 3 conflitos da IA: (1) agente defendeu `Itens_Pedido` pela 3FN alegando captura só do 1º item — refutado por correlação nula $r = -0,0103$ e pois só `Pedidos.valor_total` valida B2B=6,15x B2C; (2) colisão de `id` em *merges*; (3) memo do agente descartado por omitir Q1, Q9 e *trade-offs*.
