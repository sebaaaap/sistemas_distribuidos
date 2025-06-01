-- =============================================
-- ANÁLISIS DE EVENTOS DE TRÁFICO - VERSIÓN CORREGIDA
-- =============================================

-- Configuración inicial
SET pig.datetime.default.tz UTC-4;
SET pig.exec.mapPartAgg true;

-- 1. Carga de datos con validación
eventos = LOAD '/user/hadoop/eventos_filtrados.csv'
    USING PigStorage(',') 
    AS (
        uuid:chararray,
        tipo:chararray,
        comuna:chararray,
        timestamp:chararray,
        descripcion:chararray
    );

-- Limpieza inicial
eventos_filtrados = FILTER eventos BY 
    tipo IS NOT NULL AND 
    comuna IS NOT NULL AND
    timestamp IS NOT NULL;

-- 2. Conteo por tipo de evento
agrupado_por_tipo = GROUP eventos_filtrados BY tipo;

conteo_por_tipo = FOREACH agrupado_por_tipo {
    total = COUNT(eventos_filtrados);
    GENERATE
        group AS tipo_incidente,
        total AS total_eventos,
        (double) ROUND((double) total * 100.0 / total, 2) AS porcentaje;
}

-- 3. Análisis por comuna
agrupado_por_comuna = GROUP eventos_filtrados BY comuna;

conteo_por_comuna = FOREACH agrupado_por_comuna GENERATE
    group AS comuna,
    COUNT(eventos_filtrados) AS total_eventos,
    COUNT(eventos_filtrados.tipo) AS tipos_distintos;

top_comunas = ORDER conteo_por_comuna BY total_eventos DESC;
top_10_comunas = LIMIT top_comunas 10;

-- 4. Análisis por hora
eventos_con_hora = FOREACH eventos_filtrados GENERATE
    *,
    SUBSTRING(timestamp, 11, 2) AS hora;

agrupado_por_hora = GROUP eventos_con_hora BY hora;

eventos_por_hora = FOREACH agrupado_por_hora GENERATE
    group AS hora,
    COUNT(eventos_con_hora) AS total_eventos;

-- 5. Eventos críticos
eventos_criticos = FILTER eventos_filtrados BY
    descripcion MATCHES '.*(EMERGENCIA|CIERRE|ACCIDENTE|PELIGRO).*';

agrupado_criticos = GROUP eventos_criticos BY tipo;

conteo_criticos_por_tipo = FOREACH agrupado_criticos GENERATE
    group AS tipo,
    COUNT(eventos_criticos) AS total;

-- 6. Guardar resultados
STORE conteo_por_tipo INTO '/user/hadoop/resultados/conteo_por_tipo' USING PigStorage(',');
STORE top_10_comunas INTO '/user/hadoop/resultados/top_comunas' USING PigStorage('|');
STORE eventos_por_hora INTO '/user/hadoop/resultados/eventos_por_hora' USING JsonStorage();

STORE conteo_criticos_por_tipo INTO '/user/hadoop/resultados/eventos_criticos' USING PigStorage('\t');
STORE eventos_criticos INTO '/user/hadoop/resultados/detalle_eventos_criticos' USING JsonStorage();

-- 7. Estadísticas generales
eventos_totales = GROUP eventos_filtrados ALL;

resumen = FOREACH eventos_totales GENERATE
    COUNT(eventos_filtrados) AS total_registros,
    COUNT(DISTINCT eventos_filtrados.comuna) AS comunas_afectadas,
    COUNT(DISTINCT eventos_filtrados.tipo) AS tipos_incidentes;

STORE resumen INTO '/user/hadoop/resultados/resumen_general' USING PigStorage(',');
