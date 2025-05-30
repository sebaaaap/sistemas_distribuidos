-- Cargar el CSV desde HDFS
eventos = LOAD '/user/hadoop/eventos_filtrados.csv'
    USING PigStorage(',') AS (
        uuid:chararray,
        tipo:chararray,
        comuna:chararray,
        timestamp:chararray,
        descripcion:chararray
    );

-- Agrupar por tipo
agrupados = GROUP eventos BY tipo;

-- Contar cuántos eventos hay por tipo
conteo_por_tipo = FOREACH agrupados GENERATE group AS tipo, COUNT(eventos) AS cantidad;

-- Guardar resultados en HDFS
STORE conteo_por_tipo INTO '/user/hadoop/resultados_eventos_tipo' USING PigStorage(',');
