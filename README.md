# Trabajo semestral 🗿


## 📋 Requisitos
- Python 3.8+
- Docker
- Solicitar crendenciales 🥵

## 🚄 Para probar 
1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/sebaaaap/sistemas_distribuidos.git
   ```
2. **Importante estar en el directororio del compose.yml**:
    ```bash
    cd sistemas_distribuidos/entrega_1/servicios
    ```
3. **Crear .env y colocar sus credenciales**
   ```python
   MONGO_USER=
   MONGO_PASSWORD= 
   MONGO_CLUSTER=
   MONGO_DB=       
   MONGO_COLLECTION=
   ```
4. **Levantar servicios**
   ```bash
   docker compose up --build
   ```



## 🛠️ Para correr el pig

1. **Abrir una nueva terminal y ingresar al contenedor "procesador"**:
```bash
docker exec -it procesador bash
```
2. **Crear directorio en HDFS para el archivo fuente**:
```bash
hdfs dfs -mkdir -p /user/hadoop/
```

3. **Subir el archivo CSV a HDFS**:
```bash
hdfs dfs -put /root/dataset/eventos_filtrados.csv /user/hadoop/
```
4. **Verificar que el archivo está en HDFS**:
```bash
hdfs dfs -ls /user/hadoop/
```
5. **Ejecutar el script de Pig**:
```bash
pig -x mapreduce -f /root/scripts/analisis_general.pig
```
6. **Crear carpetas locales de resultados**:
```bash
mkdir -p /root/results/{comuna,tipo,tiempo}
```
7. **Copiar archivos desde HDFS a local**:
```bash
hdfs dfs -copyToLocal /user/hadoop/results/comuna/part-r-00000 /root/results/comuna/
```
```bash
hdfs dfs -copyToLocal /user/hadoop/results/tipo/part-r-00000 /root/results/tipo/
```
```bash
hdfs dfs -copyToLocal /user/hadoop/results/tiempo/part-r-00000 /root/results/tiempo/
```
8. **Crear los CSV con encabezado**:
```bash
(echo "comuna,total" && cat /root/results/comuna/part-r-00000) > /root/results/comuna/comuna.csv
```
```bash
(echo "tipo,total" && cat /root/results/tipo/part-r-00000) > /root/results/tipo/tipo.csv
```
```bash
(echo "fecha,total" && cat /root/results/tiempo/part-r-00000) > /root/results/tiempo/tiempo.csv
```
9. **Importante** 
   - Ir a "servicios/analisis..." para ver los resultados de los pasos que se acaban de realizar





 



























