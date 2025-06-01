-- Cargar datos una sola vez para todos los procesamientos
data = LOAD '/user/hadoop/eventos_filtrados.csv' 
       USING PigStorage(',') 
       AS (uuid:chararray, tipo:chararray, comuna:chararray, timestamp:chararray, descripcion:chararray);

-- 1. Análisis por comuna -----------------------------------------------------

-- Separar comunas múltiples (separadas por ';')
data_comunas_separadas = FOREACH data GENERATE
    uuid,
    tipo,
    FLATTEN(STRSPLIT(comuna, ';')) AS comuna_individual,
    timestamp,
    descripcion;

-- Limpiar espacios
data_comunas_limpias = FOREACH data_comunas_separadas GENERATE
    uuid,
    tipo,
    TRIM(comuna_individual) AS comuna,
    timestamp,
    descripcion;

-- Agrupar por comuna
por_comuna = GROUP data_comunas_limpias BY comuna;

-- Contar incidentes por comuna
conteo_por_comuna = FOREACH por_comuna GENERATE group AS comuna, COUNT(data_comunas_limpias) AS total;

-- 2. Análisis por tipo de incidente ------------------------------------------

-- Agrupar por tipo
por_tipo = GROUP data BY tipo;

-- Contar incidentes por tipo
conteo_por_tipo = FOREACH por_tipo GENERATE group AS tipo, COUNT(data) AS total;

-- 3. Análisis temporal -------------------------------------------------------

-- Extraer solo la fecha (formato: 'YYYY-MM-DD HH:MM:SS')
data_con_fecha = FOREACH data GENERATE SUBSTRING(timestamp, 0, 10) AS fecha;

-- Agrupar por fecha
por_fecha = GROUP data_con_fecha BY fecha;

-- Contar incidentes por fecha
conteo_por_fecha = FOREACH por_fecha GENERATE group AS fecha, COUNT(data_con_fecha) AS total;

-- Guardar resultados en HDFS -------------------------------------------------
STORE conteo_por_comuna INTO '/user/hadoop/results/comuna' USING PigStorage(',');
STORE conteo_por_tipo INTO '/user/hadoop/results/tipo' USING PigStorage(',');
STORE conteo_por_fecha INTO '/user/hadoop/results/tiempo' USING PigStorage(',');