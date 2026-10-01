# Radar 156

Aplicação de análise das solicitações do SP156, desenvolvida para identificar mudanças de demanda, pendências e comportamentos atípicos que possam merecer investigação pela gestão municipal.

**Aplicação publicada:** [https://radar-156.streamlit.app/](https://radar-156.streamlit.app/)  
**Repositório:** [https://github.com/samueldamasceno/radar-156](https://github.com/samueldamasceno/radar-156)

---

## Sobre o projeto

O SP156 recebe solicitações relacionadas a diversos serviços da Prefeitura de São Paulo. Com um grande volume de registros, nem sempre é simples identificar rapidamente quando determinado serviço ou região começa a apresentar um comportamento diferente do habitual.

O **Radar 156** transforma esses registros em sinais analíticos, permitindo acompanhar a demanda e destacar combinações de distrito e serviço que apresentem crescimento, maior pendência, maior tempo de atendimento ou comportamento estatisticamente atípico.

A solução foi pensada principalmente como ferramenta de apoio para equipes de análise e gestão municipal.

A área municipal relacionada ao projeto é o atendimento ao cidadão e a gestão de serviços públicos, utilizando dados do SP156 disponibilizados pela Prefeitura de São Paulo e pela Secretaria Municipal de Inovação e Tecnologia (SMIT).

## Dados

Foram utilizados dados públicos reais do **SP156**, disponibilizados no Portal de Dados Abertos da Prefeitura de São Paulo:

- Dados do SP156, 1º trimestre de 2026
- Dados do SP156, 2º trimestre de 2026

Os principais campos utilizados foram:

- data de abertura;
- data de finalização;
- tema;
- serviço;
- status;
- distrito.

Não foram utilizados dados sintéticos ou simulados.

Os arquivos brutos não fazem parte do repositório devido ao tamanho das bases. O arquivo processado utilizado pelo dashboard está versionado em `data/processed/`.

Os links para as bases originais estão disponíveis na seção **Fonte** ao final deste README.

## O que a aplicação faz

O dashboard permite:

- acompanhar o volume semanal de solicitações;
- visualizar taxas de pendência e tempo médio de atendimento;
- filtrar os dados por tema, distrito e período;
- identificar serviços e regiões que merecem investigação;
- comparar a demanda atual com o comportamento recente;
- analisar individualmente cada sinal;
- detectar padrões atípicos utilizando Machine Learning.

## Metodologia

O tratamento e a análise dos dados foram feitos em Python.

Os registros originais são limpos, padronizados e agregados por **semana, distrito, tema e serviço**.

A partir desses dados são calculados indicadores como:

- volume de solicitações;
- taxa de pendência;
- tempo médio de atendimento;
- variação da demanda.

Para medir a mudança de demanda, o volume atual é comparado com a média das quatro observações anteriores disponíveis para a mesma combinação.

Também foi criado um **Índice de Atenção**:

```text
40% crescimento da demanda
35% taxa de pendência
25% tempo médio de atendimento
```

O índice é uma heurística criada para o protótipo. Ele não representa um critério oficial da Prefeitura e serve para ajudar a ordenar sinais que podem justificar uma análise mais detalhada.

## Machine Learning

Além dos indicadores, o projeto utiliza **Isolation Forest**, algoritmo de aprendizado não supervisionado para detecção de anomalias.

O modelo considera conjuntamente:

- volume de solicitações;
- crescimento da demanda;
- taxa de pendência;
- tempo médio de atendimento.

Nesta versão foi utilizado `contamination=0.03`, fazendo com que aproximadamente 3% das observações territoriais componham o conjunto considerado mais atípico pelo modelo.

Uma anomalia não significa necessariamente que existe um problema grave. Ela indica apenas que aquele comportamento é estatisticamente menos comum em relação aos demais registros analisados.

## Scripts de análise e processamento

Além da aplicação, o projeto contém scripts utilizados durante a exploração, validação e preparação dos dados.

- `verificar_dados.py`: utilizado inicialmente para identificar encoding, separador, estrutura das colunas e visualizar amostras dos arquivos.
- `verificar_status.py`: utilizado para analisar os valores existentes no campo `Status` e sua relação com a presença de data de finalização.
- `auditar_distritos.py`: verifica a qualidade do campo `Distrito`, separando registros com nome de distrito, códigos numéricos e valores ausentes. Essa análise ajudou a definir quais registros poderiam ser utilizados nas análises territoriais.
- `auditar_categorias.py`: verifica possíveis variações de escrita e duplicidades em nomes de distritos e prefeituras operacionais por meio de normalização textual.
- `preparar_dados.py`: realiza o pipeline principal de preparação, calculando os indicadores, o Índice de Atenção e as anomalias com Isolation Forest, além de gerar `data/processed/radar156.parquet`.

Os scripts de auditoria foram mantidos no projeto para registrar parte do processo de exploração dos dados e das decisões tomadas durante o tratamento da base.

## Escolhas técnicas

A aplicação foi desenvolvida em **Streamlit**.

Apesar de normalmente utilizar React em aplicações web, neste projeto optei por manter a interface dentro do ecossistema Python, já que o foco da solução está no processamento, análise e modelagem dos dados.

Isso permitiu integrar tratamento de dados, Machine Learning e visualizações sem adicionar uma camada de frontend separada que não seria necessária para o objetivo do protótipo.

Principais tecnologias utilizadas:

- Python
- Streamlit
- Pandas
- NumPy
- Scikit-learn
- Plotly
- PyArrow
- Parquet

## Uso de IA generativa

O ChatGPT foi utilizado como ferramenta de apoio durante o desenvolvimento, principalmente para discussão e revisão de código, estruturação de soluções e documentação.

As sugestões foram avaliadas antes de serem incorporadas ao projeto e as alterações foram validadas por meio da execução dos scripts e da análise dos resultados produzidos.

## Limitações

Algumas limitações atuais são:

- o histórico utilizado cobre apenas o primeiro semestre de 2026;
- solicitações do SP156 não representam diretamente a quantidade de problemas existentes na cidade;
- parte dos registros não possui distrito nominal identificado;
- os pesos do Índice de Atenção são uma heurística e ainda não foram validados com gestores;
- o baseline atual não considera explicitamente efeitos de sazonalidade.

Por isso, o Radar 156 deve ser interpretado como uma ferramenta de apoio à investigação, e não como um sistema automático de definição de prioridades.

## Possíveis evoluções

Entre possíveis próximos passos estão:

- atualização automática quando novas bases forem publicadas;
- utilização de um histórico de vários anos;
- tratamento de sazonalidade;
- calibração do Índice de Atenção junto a gestores;
- integração com dados do IBGE e GeoSampa;
- alertas automáticos para alterações relevantes.

## Executando localmente

Para executar somente o dashboard, não é necessário baixar os arquivos CSV originais, pois o dataset processado já está incluído no repositório.

Clone o projeto:

```bash
git clone https://github.com/samueldamasceno/radar-156.git
cd radar-156
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute a aplicação:

```bash
streamlit run streamlit_app.py
```

A aplicação utiliza diretamente:

```text
data/processed/radar156.parquet
```

### Reproduzindo o processamento

Caso queira executar também os scripts de auditoria e gerar novamente o arquivo processado, baixe os CSVs do 1º e 2º trimestres de 2026 do SP156 utilizando os links disponíveis na seção **Fonte**.

Coloque os arquivos em:

```text
data/raw/
```

O pipeline procura os arquivos seguindo o padrão:

```text
sp156_2026_q*.csv
```

Portanto, após o download, renomeie os arquivos para:

```text
sp156_2026_q1.csv
sp156_2026_q2.csv
```

Depois execute:

```bash
python scripts/preparar_dados.py
```

O arquivo processado será gerado em:

```text
data/processed/radar156.parquet
```

Os scripts de auditoria também podem ser executados individualmente:

```bash
python scripts/verificar_dados.py
python scripts/verificar_status.py
python scripts/auditar_distritos.py
python scripts/auditar_categorias.py
```

## Fonte

**Portal de Dados Abertos da Prefeitura de São Paulo**

Conjunto completo:

[Dados do SP156 - Solicitações](https://dados.prefeitura.sp.gov.br/dataset/dados-do-sp156)

Bases utilizadas:

- [Dados do SP156 - 1º TRI 2026](https://dados.prefeitura.sp.gov.br/dataset/dados-do-sp156/resource/75105148-4efd-48f3-8ae0-fc6c2adf7060)
- [Dados do SP156 - 2º TRI 2026](https://dados.prefeitura.sp.gov.br/dataset/dados-do-sp156/resource/368eb32d-ef25-4441-be8f-fce0146575a1)

Os dados utilizados cobrem o primeiro semestre de 2026.