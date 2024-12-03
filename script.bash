# Извлекаем процент выравнивания из результата
percent=$(grep -oP '\d+\.\d+%' flagstat_report.txt | head -1 | tr -d '%')
echo $percent
# Проверяем, соответствует ли результат порогу
if (( $(echo "$percent >= 90.0" | bc -l) )); then
    echo "OK"
else
    echo "not OK"
fi
