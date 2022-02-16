cd {{chaosbladePath}}/bin || echo "Can not find chaosblade" && exit

blade {{exper}}

cd - || echo "Unexpected Error!" && exit
