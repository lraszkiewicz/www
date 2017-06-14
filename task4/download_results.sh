rm -r ./results/
mkdir ./results/
cd ./results/
for i in {01..68}; do wget http://prezydent2000.pkw.gov.pl/gminy/obwody/obw$i.xls; done
