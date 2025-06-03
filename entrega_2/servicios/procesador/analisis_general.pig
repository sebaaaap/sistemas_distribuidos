data = LOAD '/user/hadoop/eventos_filtrados.csv' 
       USING PigStorage(',') 
       AS (uuid:chararray, tipo:chararray, comuna:chararray, timestamp:chararray, descripcion:chararray);


data_comunas_separadas = FOREACH data GENERATE
    uuid,
    tipo,
    FLATTEN(STRSPLIT(comuna, ';')) AS comuna_individual,
    timestamp,
    descripcion;

data_comunas_limpias = FOREACH data_comunas_separadas GENERATE
    uuid,
    tipo,
    TRIM(comuna_individual) AS comuna,
    timestamp,
    descripcion;

por_comuna = GROUP data_comunas_limpias BY comuna;

conteo_por_comuna = FOREACH por_comuna GENERATE group AS comuna, COUNT(data_comunas_limpias) AS total;


por_tipo = GROUP data BY tipo;

conteo_por_tipo = FOREACH por_tipo GENERATE group AS tipo, COUNT(data) AS total;


data_con_fecha = FOREACH data GENERATE SUBSTRING(timestamp, 0, 10) AS fecha;

por_fecha = GROUP data_con_fecha BY fecha;

conteo_por_fecha = FOREACH por_fecha GENERATE group AS fecha, COUNT(data_con_fecha) AS total;

STORE conteo_por_comuna INTO '/user/hadoop/results/comuna' USING PigStorage(',');
STORE conteo_por_tipo INTO '/user/hadoop/results/tipo' USING PigStorage(',');
STORE conteo_por_fecha INTO '/user/hadoop/results/tiempo' USING PigStorage(',');